from .base import CustomException

class LDAPConnectionTimeoutException(CustomException):
    code = 500
    error_code = "LDAP_CONNECTION_TIMEOUT"
    message = "LDAP connection timed out, try again shortly"


class LDAPUserNotFoundException(CustomException):
    code = 404
    error_code = "LDAP_USER_NOT_FOUND"
    message = "LDAP user not found, login with valid credentials"


class LDAPSocketOpenError(CustomException):
    code = 502
    error_code = "LDAP_Bad_Gateway"
    message = "LDAP bad gateway, please try again"


class LDAPBadRequestException(CustomException):
    code = 400
    error_code = "LDAP_Invalid_Request"
    message = "LDAP request is invalid, please check and try again"


class LDAPNotAcceptableException(CustomException):
    code = 406
    error_code = "LDAP_Request_Not_Acceptable"
    message = "LDAP filter error, please validate query and try again"


class LDAPUnauthorizedException(CustomException):
    code = 401
    error_code = "LDAP_Authorization_Error"
    message = "LDAP authorization error, please try again with valid credentials"


class LDAPRequestTimeout(CustomException):
    code = 408
    error_code = "LDAP_Request_Timeout"
    message = "LDAP server timed out, please reload and try again"


class LDAPServiceUnavailable(CustomException):
    code = 503
    error_code = "LDAP_Temporarily_Unavailable"
    message = "LDAP currently unavailable due to high volumes of traffic, please try again later"


class LDAPInternalServerError(CustomException):
    code = 500
    error_code = "LDAP_Internal_Server_Error"
    message = "LDAP internal server error"