from aiohttp import web

from api.utils.json_serializers import to_json


class RecordNotFoundException(ValueError):
    """Exception raised when record doesn't exist"""

    MESSAGE: str = "Specified record doesn't exist"

    def __init__(self, message: str = MESSAGE):
        self.message = message
        self.field = None

    def __str__(self):
        return self.message

    def error_dict(self) -> dict:
        """
        Return dict for validation error.

        :return: Validation error dict
        :rtype: dict
        """

        return {"errors": {self.field: self.message}}

    def response(self) -> web.Response:
        """
        Return the response of not found record.

        :return: Response of not found record
        :rtype: web.Response
        """

        return web.json_response(text=to_json(self.error_dict()), status=404)


class PostNotFoundException(RecordNotFoundException):
    def __init__(self):
        self.message = "Specified post doesn't exist"
        self.field = "post_id"


class UserNotFoundException(RecordNotFoundException):
    def __init__(self):
        self.message = "Specified user doesn't exist"
        self.field = "user_id"
