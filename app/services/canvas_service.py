from fastapi import HTTPException
import requests
from app.core.exceptions import LMSNoCourseFetchedException, LMSNoAssignmentFetchedException, LMSNoStudentsFetchedException


# Assuming we'll store our Canvas LMS API key securely, for now I am just hard coding it
CANVAS_API_KEY = "YOUR_API_KEY"
CANVAS_API_URL = "https://uncch.instructure.com/api/v1"

class CanvasService:
    def __init__(self, course_id):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {CANVAS_API_KEY}"})
        self.course_id = course_id

    async def get_courses(self):
        try:
            url = f"{CANVAS_API_URL}/courses"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            raise NoCourseFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)
        )

    async def get_course(self, additional_params=None):
        try:
            url = f"{CANVAS_API_URL}/courses/{self.course_id}"
            
            if additional_params:
                # Append additional parameters to the URL
                url += "?" + "&".join([f"{key}={value}" for key, value in additional_params.items()])
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            raise NoCourseFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # returns a dictionary of assignments for a course
    async def get_assignments(self):
        try:
            url = f"{CANVAS_API_URL}/courses/{self.course_id}/assignments"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            raise NoAssignmentFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_assignment(self, assignment_id):
        try:
            url = f"{CANVAS_API_URL}/courses/{self.course_id}/assignments/{assignment_id}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            raise NoAssignmentFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_students(self, additional_params=None):
        try:
            url = f"{CANVAS_API_URL}/courses/{self.course_id}/users"

            if additional_params:
                # Append additional parameters to the URL
                url += "?" + "&".join([f"{key}={value}" for key, value in additional_params.items()])

            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            raise NoStudentsFetchedException()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 

