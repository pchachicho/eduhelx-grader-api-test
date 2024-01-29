import datetime
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services import SubmissionService
from app.models import StudentModel, AssignmentModel, SubmissionModel
from app.core.exceptions import SubmissionNotFoundException
from app.services import StudentService, StudentAssignmentService


# Note: Waiting for Griffin's SubmissionService change to be merged, 
# minor impact but will need to update the test again to reflect the changes


class TestSubmissionService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_session = MagicMock()
        self.mock_student = MagicMock(spec=StudentModel)
        self.mock_assignment = MagicMock(spec=AssignmentModel)
        self.mock_submission = MagicMock(spec=SubmissionModel)

    # async def test_create_submission(self):
    #     self.mock_session.query().filter().first.return_value = self.mock_submission

    #     submission_service = SubmissionService(
    #         session=self.mock_session
    #     )

    #     result = await submission_service.create_submission(
    #         student=self.mock_student,
    #         assignment=self.mock_assignment,
    #         commit_id="1234567890"
    #     )

    #     self.assertEqual(result, self.mock_submission)

    # async def test_get_submissions(self):
    #     self.mock_session.query().filter().order_by().all.return_value = [self.mock_submission]

    #     submission_service = SubmissionService(
    #         session=self.mock_session
    #     )

    #     result = await submission_service.get_submissions(
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     self.assertEqual(result, [self.mock_submission])

    # async def test_get_latest_submission(self):
    #     self.mock_session.query().filter().order_by().limit().first.return_value = self.mock_submission

    #     submission_service = SubmissionService(
    #         session=self.mock_session
    #     )

    #     result = await submission_service.get_latest_submission(
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     self.assertEqual(result, self.mock_submission)

    # async def test_get_latest_submission_not_found(self):
    #     self.mock_session.query().filter().order_by().limit().first.return_value = None

    #     submission_service = SubmissionService(
    #         session=self.mock_session
    #     )

    #     with self.assertRaises(SubmissionNotFoundException):
    #         await submission_service.get_latest_submission(
    #             student=self.mock_student,
    #             assignment=self.mock_assignment
    #         )

suite = unittest.TestLoader().loadTestsFromTestCase(TestSubmissionService)
unittest.TextTestRunner(verbosity=2).run(suite)
