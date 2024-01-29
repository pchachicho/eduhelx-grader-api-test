import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services import AssignmentService
from app.models import AssignmentModel
from app.core.exceptions import AssignmentNotFoundException
from ..data.database.assignment import assignment_data

class TestAssignmentService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_session = MagicMock()
        self.assignment_service = AssignmentService(session=self.mock_session)


    async def test_get_assignment_by_id_success(self):
        mock_assignment = assignment_data["available"]
        self.mock_session.query().first.return_value = mock_assignment

        result = await self.assignment_service.get_assignment_by_id(id=1)
        self.assertEqual(result, mock_assignment)

    async def test_get_assignment_by_id_not_found(self):
        self.mock_session.query().first.return_value = None

        with self.assertRaises(AssignmentNotFoundException):
            await self.assignment_service.get_assignment_by_id(id=1)

    async def test_get_assignments_success(self):
        mock_assignments = [
            assignment_data["available"],
            assignment_data["closed"],
            assignment_data["unavialable"]
        ]
        self.mock_session.query().all.return_value = mock_assignments

        result = await self.assignment_service.get_assignments()
        self.assertEqual(len(result), len(mock_assignments))

    async def test_get_assignment_by_name_success(self):
        mock_assignment = assignment_data["available"]
        self.mock_session.query().filter_by().first.return_value = mock_assignment

        result = await self.assignment_service.get_assignment_by_name(name="available")
        self.assertEqual(result.name, mock_assignment.name)

    async def test_get_assignment_by_name_not_found(self):
        self.mock_session.query().filter_by().first.return_value = None

        with self.assertRaises(AssignmentNotFoundException):
            await self.assignment_service.get_assignment_by_name(name="available")

    async def test_update_assignment_name_success(self):
        mock_assignment = assignment_data["available"]
        self.mock_session.commit.return_value = None

        result = await self.assignment_service.update_assignment_name(assignment=mock_assignment, new_name="new_name")
        self.assertEqual(result.name, "new_name")

    async def test_update_assignment_directory_path_success(self):
        mock_assignment = assignment_data["available"]
        self.mock_session.commit.return_value = None

        result = await self.assignment_service.update_assignment_directory_path(assignment=mock_assignment, directory_path="new/directory/path")
        self.assertEqual(result.directory_path, "new/directory/path")

    async def test_update_assignment_available_date_success(self):
        mock_assignment = assignment_data["available"]
        self.mock_session.commit.return_value = None

        result = await self.assignment_service.update_assignment_available_date(assignment=mock_assignment, available_date=mock_assignment.available_date)
        self.assertEqual(result.available_date, mock_assignment.available_date)

    async def test_update_assignment_due_date_success(self):
        mock_assignment = assignment_data["available"]
        self.mock_session.commit.return_value = None

        result = await self.assignment_service.update_assignment_due_date(assignment=mock_assignment, due_date=mock_assignment.due_date)
        self.assertEqual(result.due_date, mock_assignment.due_date)


suite = unittest.TestLoader().loadTestsFromTestCase(TestAssignmentService)
unittest.TextTestRunner(verbosity=2).run(suite)
