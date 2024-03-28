from fastapi import HTTPException
import requests
from app.core.exceptions import NoCourseFetchedException, NoAssignmentFetchedException

# Assuming we'll store our Canvas LMS API key securely, for now I am just hard coding it
CANVAS_API_KEY = "7006~RMJbYVaRDn3SeKt3kekSHJ1RaVk5oLbmDjkxg650f2rQ6MXwHoeAl3xiWO2rtnzZ"
CANVAS_API_URL = "https://uncch.instructure.com/api/v1"

class CanvasService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {CANVAS_API_KEY}"})

    async def get_courses(self):
        try:
            url = f"{CANVAS_API_URL}/courses"
            response = self.session.get(url)
            # Raise exception for 4xx or 5xx status codes
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise NoCourseFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)
        )

    def get_course(self, course_id):
        try:
            url = f"{CANVAS_API_URL}/courses/{course_id}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise NoCourseFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # returns a dictionary of assignments for a course
    async def get_assignments(self, course_id):
        try:
            url = f"{CANVAS_API_URL}/courses/{course_id}/assignments"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise NoAssignmentFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_assignment(self, course_id, assignment_id):
        try:
            url = f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise NoAssignmentFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    #  GET /api/v1/courses/:course_id/recent_students 
    async def get_recent_students(self, course_id):
        try:
            url = f"{CANVAS_API_URL}/courses/{course_id}/recent_students"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise NoCourseFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))




    
    
    
    

