from typing import List
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.models import StudentModel, AssignmentModel, SubmissionModel
from app.core.exceptions import SubmissionNotFoundException
from app.services import StudentService, StudentAssignmentService

class SubmissionService:
    def __init__(self, session: Session):
        self.session = session

    async def create_submission(
        self,
        student: StudentModel,
        assignment: AssignmentModel,
        commit_id: str
    ) -> SubmissionModel:
        # TODO: We should validate that the submitted commit id actually exists in gitea before persisting it in the database.
        # We don't want another component of EduHeLx to assume the commit we return exists and crash when it doesn't.
        # Alternatively, we could bake this logic into the endpoints to get submissions, rather than into this one.

        # Assert the assignment can be submitted to by the student.
        await StudentAssignmentService(self.session, student, assignment).validate_student_can_submit()

        submission = SubmissionModel(
            student_id=student.id,
            assignment_id=assignment.id,
            commit_id=commit_id
        )

        self.session.add(submission)
        self.session.commit()

        return submission
    
    async def get_submission_by_id(
        self,
        submission_id: int
    ) -> SubmissionModel:
        submission = self.session.query(SubmissionModel) \
            .filter_by(id=submission_id) \
            .one()
        if submission is None:
            raise SubmissionNotFoundException()
        return submission

    async def get_submissions(
        self,
        student: StudentModel,
        assignment: AssignmentModel
    ) -> List[SubmissionModel]:
        submissions = self.session.query(SubmissionModel) \
            .filter_by(student_id=student.id, assignment_id=assignment.id) \
            .order_by(desc(SubmissionModel.submission_time)) \
            .all()

        return submissions

    async def get_latest_submission(
        self,
        student: StudentModel,
        assignment: AssignmentModel
    ) -> SubmissionModel:
        submission = self.session.query(SubmissionModel) \
            .filter_by(student_id=student.id, assignment_id=assignment.id) \
            .order_by(desc(SubmissionModel.submission_time)) \
            .limit(1) \
            .first()
        if submission is None:
            raise SubmissionNotFoundException()
        return submission
        