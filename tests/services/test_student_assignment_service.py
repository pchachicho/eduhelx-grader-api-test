import datetime
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services import AssignmentService, StudentAssignmentService
from app.models import AssignmentModel, StudentModel, ExtraTimeModel
from app.core.exceptions import AssignmentNotFoundException, AssignmentNotOpenException
from ..data.database.assignment import assignment_data

class TestStudentAssignmentService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_session = MagicMock()
        self.mock_student = MagicMock(spec=StudentModel)
        self.mock_assignment = MagicMock(spec=AssignmentModel)
        self.mock_extra_time_model = MagicMock(spec=ExtraTimeModel)

    # async def test_get_adjusted_available_date_with_extra_time(self):
    #     self.mock_assignment.available_date = datetime(2022, 1, 1)
    #     self.mock_extra_time_model.deferred_time = datetime.timedelta(days=1)
    #     self.mock_session.query().filter().first.return_value = self.mock_extra_time_model

    #     student_assignment_service = StudentAssignmentService(
    #         session=self.mock_session,
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     result = await student_assignment_service.get_adjusted_available_date()

    #     expected_date = datetime(2022, 1, 2)
    #     self.assertEqual(result, expected_date)

    # async def test_get_adjusted_available_date_without_extra_time(self):
    #     self.mock_assignment.available_date = datetime(2022, 1, 1)
    #     self.mock_session.query().filter().first.return_value = None

    #     student_assignment_service = StudentAssignmentService(
    #         session=self.mock_session,
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     result = student_assignment_service.get_adjusted_available_date()

    #     self.assertEqual(result, datetime(2022, 1, 1))

    # async def test_get_adjusted_due_date_with_extra_time(self):
    #     self.mock_assignment.due_date = datetime(2022, 1, 1)
    #     self.mock_extra_time_model.deferred_time = datetime.timedelta(days=1)
    #     self.mock_session.query().filter().first.return_value = self.mock_extra_time_model

    #     student_assignment_service = StudentAssignmentService(
    #         session=self.mock_session,
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     result = student_assignment_service.get_adjusted_due_date()

    #     expected_date = datetime(2022, 1, 2)
    #     self.assertEqual(result, expected_date)

    # async def test_get_adjusted_due_date_without_extra_time(self):
    #     self.mock_assignment.due_date = datetime(2022, 1, 1)
    #     self.mock_session.query().filter().first.return_value = None

    #     student_assignment_service = StudentAssignmentService(
    #         session=self.mock_session,
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     result = student_assignment_service.get_adjusted_due_date()

    #     self.assertEqual(result, datetime(2022, 1, 1))

    # async def test_validate_student_can_submit(self):
    #     self.mock_assignment.is_created = True
    #     self.mock_assignment.available_date = datetime(2022, 1, 1)
    #     self.mock_assignment.due_date = datetime(2025, 1, 1)
    #     self.mock_session.query().filter().first.return_value = self.mock_extra_time_model

    #     student_assignment_service = StudentAssignmentService(
    #         session=self.mock_session,
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     student_assignment_service.validate_student_can_submit()

    # async def test_validate_student_cannot_submit(self):
    #     self.mock_assignment.is_created = True
    #     self.mock_assignment.available_date = datetime(2022, 1, 1)
    #     self.mock_session.query().filter().first.return_value = None

    #     student_assignment_service = StudentAssignmentService(
    #         session=self.mock_session,
    #         student=self.mock_student,
    #         assignment=self.mock_assignment
    #     )

    #     with self.assertRaises(AssignmentNotOpenException):
    #         student_assignment_service.validate_student_can_submit()


suite = unittest.TestLoader().loadTestsFromTestCase(TestStudentAssignmentService)
unittest.TextTestRunner(verbosity=2).run(suite)
