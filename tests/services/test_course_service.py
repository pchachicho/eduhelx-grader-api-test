import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.services import CourseService
from app.models import CourseModel, InstructorModel
from app.services.user import InstructorService
from ..data.database.course import data
from app.schemas import CourseWithInstructorsSchema
from app.core.exceptions import (
    MultipleCoursesExistException,
    NoCourseExistsException,
)

class TestCourseService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_session = MagicMock(spec=Session)

        self.course_service = CourseService(session=self.mock_session)
        self.mock_course = CourseModel(name="COMP 555", master_remote_url="")

    async def test_get_course_single_result(self):
        self.mock_session.query().one.return_value = self.mock_course
        result = await self.course_service.get_course()

        self.assertIsInstance(result, CourseModel)
        self.assertEqual(result, self.mock_course)
    
    async def test_get_course_multiple_results(self):
        self.mock_session.query().one.side_effect = MultipleResultsFound()

        with self.assertRaises(MultipleCoursesExistException):
            self.assertRaises(await self.course_service.get_course())

    async def test_get_course_no_result(self):
        self.mock_session.query().one.side_effect = NoResultFound()

        with self.assertRaises(NoCourseExistsException):
            self.assertRaises(await self.course_service.get_course())
    
    async def test_get_course_with_instructors_schema_success(self):
        mock_course = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
        instructorList = [InstructorModel(id=1, onyen="instructor_onyen", first_name="Ins", last_name="Tructor", email="email@unc.com")]

        self.mock_session.query().one.return_value = mock_course
        self.mock_session.query().all.return_value = instructorList

        expected_course = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
        expected_course.instructors=instructorList

        result = await self.course_service.get_course_with_instructors_schema()
        expected_result = CourseWithInstructorsSchema.from_orm(expected_course)

        self.assertEqual(result, expected_result)

    # def test_create_course_success(self):

    #     self.mock_session.query().one.side_effect = NoResultFound()
    #     self.mock_session.add.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
    #     self.mock_session.commit.return_value = None

    #     result = self.course_service.create_course(name="Math")
    #     assert result.id == 1
    
    # def test_get_instructor_gitea_organization_name(self):
    #     self.mock_session.query().one.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")

    #     result = self.course_service.get_instructor_gitea_organization_name()
    #     assert result == "Math-instructors"

    # def test_get_master_repository_name(self):
    #     self.mock_session.query().one.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")

    #     result = self.course_service.get_master_repository_name()
    #     assert result == "Math-class-master-repo"


suite = unittest.TestLoader().loadTestsFromTestCase(TestCourseService)
unittest.TextTestRunner(verbosity=2).run(suite)
