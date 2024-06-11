from sqlalchemy.orm import Session
from app.models import UserModel
from app.services import GiteaService, KubernetesService, CourseService

class CleanupService:
    class User:
        def __init__(self, session: Session, user: UserModel):
            self.session = session
            self.user = user

        async def undo_create_user(self, delete_database_user=False, delete_password_secret=False, delete_gitea_user=False):
            course = await CourseService(self.session).get_course()
            if delete_database_user:
                self.session.delete(self.user)
                self.session.commit()

            if delete_password_secret:
                KubernetesService().delete_credential_secret(course.name, self.user.onyen)
            
            if delete_gitea_user:
                await GiteaService(self.session).delete_user(self.user.onyen, purge=True)
            
        async def undo_delete_user(self):
            ...