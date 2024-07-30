from .base import CustomException

class GiteaInternalServerError(CustomException):
    code = 500
    error_code = "GITEA_ERROR"
    message = "Gitea internal server error, please try again shortly"