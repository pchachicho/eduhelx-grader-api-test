import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.services import CourseService
from app.models import CourseModel, InstructorModel
from ..data.database.course import data
from app.schemas import CourseWithInstructorsSchema
from app.core.exceptions import (
    MultipleCoursesExistException,
    NoCourseExistsException,
)

class TestCourseService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=Session)
        self.course_service = CourseService(session=self.mock_session)

    def test_get_course_single_result(self):
        self.mock_session.query().one.return_value = CourseModel()
        result = self.course_service.get_course()

        self.assertIsInstance(result, CourseModel)
    
    def test_get_course_multiple_results(self):
        self.mock_session.query().one.side_effect = MultipleResultsFound()

        with self.assertRaises(MultipleCoursesExistException):
            self.assertRaises(self.course_service.get_course())

    def test_get_course_no_result(self):
        self.mock_session.query().one.side_effect = NoResultFound()

        with self.assertRaises(NoCourseExistsException):
            self.assertRaises(self.course_service.get_course())
    
    async def test_get_course_with_instructors_schema_success(self):
        self.mock_session.query().one.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
        course = self.course_service.get_course()
        instructorList = [InstructorModel(id=1, onyen="instructor_onyen", first_name="Ins", last_name="Tructor")]

        mock_instructor_service = MagicMock()
        self.mock_session.query().one.return_value = course
        mock_instructor_service.list_instructors.return_value = instructorList

        result = await self.course_service.get_course_with_instructors_schema()
        assert course.instructors == instructorList
        assert result == CourseWithInstructorsSchema(id=1, name="Math", master_remote_url="http://example.com", instructors=instructorList)

    def test_get_course_with_instructors_schema_no_course(self):
        self.mock_session.query().one.side_effect = NoResultFound()

        with self.assertRaises(NoCourseExistsException):
            self.assertRaises(self.course_service.get_course_with_instructors_schema())

    def test_get_course_with_instructors_schema_multiple_courses(self):
        self.mock_session.query().one.side_effect = MultipleResultsFound()

        with self.assertRaises(MultipleCoursesExistException):
            self.assertRaises(self.course_service.get_course_with_instructors_schema())

    def test_create_course_success(self):
        self.mock_session.query().one.side_effect = NoResultFound()
        self.mock_session.add.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
        self.mock_session.commit.return_value = None

        result = self.course_service.create_course(name="Math")
        assert result.id == 1
    
    def test_get_instructor_gitea_organization_name(self):
        self.mock_session.query().one.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")

        result = self.course_service.get_instructor_gitea_organization_name()
        assert result == "Math-instructors"

    def test_get_master_repository_name(self):
        self.mock_session.query().one.return_value = CourseModel(id=1, name="Math", master_remote_url="http://example.com")

        result = self.course_service.get_master_repository_name()
        assert result == "Math-class-master-repo"


suite = unittest.TestLoader().loadTestsFromTestCase(TestCourseService)
unittest.TextTestRunner(verbosity=2).run(suite)
