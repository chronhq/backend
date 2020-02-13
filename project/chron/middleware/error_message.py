""" Use JSON response for some exceptions """
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.request import WrappedAttributeError


class ErrorMessageFormatter(MiddlewareMixin):  # pylint: disable=too-few-public-methods
    """ Format exceptions as a JSON errors """

    def process_exception(self, request, exception):
        """ Handle various exceptions """
        if isinstance(exception, ValidationError):
            return JsonResponse({"error": exception.messages}, status=400)
        if isinstance(exception, WrappedAttributeError):
            # This is a bug in drf-firebase-auth module
            # https://github.com/garyburgmann/drf-firebase-auth/issues/13
            err = "module 'firebase_admin.auth' has no attribute 'AuthError'"
            if str(exception) == err:
                return JsonResponse({"error": "Authorization error"}, status=401)
        return None
