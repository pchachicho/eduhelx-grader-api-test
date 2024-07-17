import tempfile
import zipfile
import glob
import json
from otter.assign import main as otter_assign
from otter.run import main as otter_run
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings, DevPhase
from app.core.exceptions import SubmissionNotFoundException, OtterConfigViolationException
from app.core.utils.datetime import get_now_with_tzinfo
from app.services import StudentService, SubmissionService, CourseService, GiteaService, LmsSyncService, CleanupService
from app.models import AssignmentModel, SubmissionModel, GradeReportModel
from app.schemas import GradeReportSchema, SubmissionGradeSchema

class GradingService:
    def __init__(self, session: Session):
        self.session = session

    """ You can retrace which submissions were used to generate a grade report by using its created_date. """
    async def compute_submissions_at_moment(self, assignment: AssignmentModel, moment: datetime | None = None) -> list[SubmissionModel]:
        if moment is None: moment = get_now_with_tzinfo()

        student_service = StudentService(self.session)
        submission_service = SubmissionService(self.session)

        students = await student_service.list_students()
        submissions = []
        for student in students:
            try:
                active_submission = await submission_service.get_active_submission(student, assignment, moment)
                submissions.append(active_submission)
            except SubmissionNotFoundException:
                # The student hasn't made a submission
                pass
            
        return submissions
    
    async def generate_config(
        self,
        master_notebook_content: str,
        otter_config_content: str,
        requirements_txt_content: str
    ) -> tuple[str, bytes]:
        # The master notebook isn't actually the final revision used for grading
        # We also need to generate a zip config.
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            master_notebook_path = temp_dir / "master.ipynb"
            requirements_txt_path = temp_dir / "requirements.txt"
            config_dir = temp_dir / "otter"
            autograder_path = config_dir / "autograder"

            with open(master_notebook_path, "w+") as f:
                f.write(master_notebook_content)

            with open(requirements_txt_path, "w+") as f:
                f.write(requirements_txt_content)

            otter_assign(master_notebook_path, str(config_dir), no_pdfs=True)
            
            zip_config_glob = glob.glob(str(autograder_path / f"{ master_notebook_path.stem }*.zip"))
            if len(zip_config_glob) == 0:
                raise OtterConfigViolationException("could not generate/find otterconfig zip for assignment")
            
            autograder_notebook_path = autograder_path / master_notebook_path.name
            zip_config_path = zip_config_glob[0]

            with open(autograder_notebook_path, "r") as f:
                final_graded_notebook_content = f.read()

            config_zip = BytesIO()
            # Overwrite the otter_config.json generated inside the zip with the user-supplied config. 
            with zipfile.ZipFile(zip_config_path, "r") as old_zip:
                with zipfile.ZipFile(config_zip, "w") as new_zip:
                    for item in old_zip.infolist():
                        if item.filename != "otter_config.json":
                            new_zip.writestr(item, old_zip.read(item.filename))
                    new_zip.writestr("otter_config.json", otter_config_content)


        return final_graded_notebook_content, config_zip.getvalue()

    async def grade_assignment(
        self,
        assignment: AssignmentModel,
        master_notebook_content: str,
        otter_config_content: str,
        requirements_txt_content: str = "otter-grader==5.5.0",
        *,
        dry_run=False
    ) -> GradeReportModel:
        course_service = CourseService(self.session)
        gitea_service = GiteaService(self.session)
        submission_service = SubmissionService(self.session)
        lms_sync_service = LmsSyncService(self.session)

        submissions = await self.compute_submissions_at_moment(assignment)
        final_graded_notebook_content, zip_config_bytes = await self.generate_config(
            master_notebook_content,
            otter_config_content,
            requirements_txt_content
        )

        final_scores = {}
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            graded_notebook_path = temp_dir / "graded.ipynb"
            otter_config_path = temp_dir / "config.zip"
            with open(graded_notebook_path, "w+") as f:
                f.write(final_graded_notebook_content)
            with open(otter_config_path, "wb+") as f:
                f.write(zip_config_bytes)
            for submission in submissions:
                submission_archive_path = temp_dir / str(submission.id)
                submission_graded_path = temp_dir / f"{ submission.id }-graded.json"
                submission_notebook_path = submission_archive_path / submission.assignment.student_notebook_path
                student_repo_name = await course_service.get_student_repository_name(submission.student.onyen)
                archive_stream = await gitea_service.download_repository(
                    name=student_repo_name,
                    owner=submission.student.onyen,
                    treeish_id=submission.commit_id,
                    path=submission.assignment.directory_path
                )
                with zipfile.ZipFile(archive_stream, "r") as zip:
                    zip.extractall(submission_archive_path)
                otter_run(
                    submission=str(submission_notebook_path),
                    autograder=str(otter_config_path),
                    output_dir=str(submission_graded_path),
                    no_logo=True,
                    debug=settings.DEV_PHASE == DevPhase.DEV
                )

                with open(submission_graded_path, "r") as f:
                    grade_data = json.load(f)

                tests = [test for test in grade_data["tests"] if "score" in test]
                public_tests = [test for test in grade_data["tests"] if "score" not in test]
                public_test_comments = "\n".join([test["output"] for test in public_tests])

                score = sum([question["score"] for question in tests])
                max_score = sum([question["max_score"] for question in tests])
                with open(submission_notebook_path, "rb") as f:
                    student_notebook_content = f.read()
                final_scores[submission] = (
                    SubmissionGradeSchema(
                        score=score,
                        total_points=max_score,
                        comments=public_test_comments,
                        submission_already_graded=submission.graded
                    ),
                    student_notebook_content
                )

            grade_report = GradeReportModel.from_submission_grades(
                assignment=assignment,
                submission_grades=[submission_grade for (submission_grade, _) in final_scores.values()],
                master_notebook_content=master_notebook_content,
                otter_config_content=otter_config_content
            )
            # If it's a dry run, stop right here and return the grade report.
            if dry_run: return grade_report

            self.session.add(grade_report)
            self.session.commit()

            cleanup_service = CleanupService.Grading(self.session, grade_report)

            try:
                for submission, (
                    submission_grade,
                    student_notebook_content
                ) in final_scores.items():
                    if submission.graded:
                        # This submission is already graded. No point in reuploading it to Canvas.
                        continue
                    
                    attempt = await submission_service.get_submission_attempt(submission)
                    student_notebook = BytesIO(student_notebook_content)
                    student_notebook.name = f"{ submission.student.onyen }-submission-{ attempt }.ipynb"
                    await lms_sync_service.upsync_grade(
                        submission=submission,
                        grade=submission_grade.score,
                        student_notebook=student_notebook,
                        comments=submission_grade.comments if assignment.grader_question_feedback else None,
                    )
                    submission.graded = True
            except Exception as e:
                await cleanup_service.undo_grade_assignment(delete_database_grade_report=True)
                raise e
            
            # All we've done is change `graded` on submissions, which can't cause any violations here.
            self.session.commit()
            
            return grade_report