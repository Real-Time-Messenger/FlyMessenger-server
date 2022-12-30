from app.common.swagger.responses.common import USER_NOT_AUTHORIZED_RESPONSE

DELETE_ME_RESPONSES = {
    204: {
        "description": "User deleted successfully.",
    },
    401: USER_NOT_AUTHORIZED_RESPONSE,
}