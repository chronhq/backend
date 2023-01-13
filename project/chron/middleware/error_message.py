""" Use JSON response for some exceptions """
import traceback
import sys
import re
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.request import WrappedAttributeError


class ErrorMessageFormatter(MiddlewareMixin):  # pylint: disable=too-few-public-methods
    """Format exceptions as a JSON errors"""

    def process_exception(self, request, exception):
        """Handle various exceptions"""
        if isinstance(exception, ValidationError):
            return JsonResponse({"error": exception.messages}, status=400)
        if isinstance(exception, WrappedAttributeError):
            # This is a bug in drf-firebase-auth module
            # https://github.com/garyburgmann/drf-firebase-auth/issues/13
            err = "module 'firebase_admin.auth' has no attribute 'AuthError'"
            if str(exception) == err:
                t, v, tb = sys.exc_info()  # pylint: disable=invalid-name
                text = ""
                for line in reversed(traceback.format_exception(t, v, tb)):
                    search = re.search("firebase_admin.*\.(.*):", line)
                    if not search:
                        continue
                    # firebase_admin._auth_utils.InvalidIdTokenError
                    if search.group(1) == "InvalidIdTokenError":
                        text = "Invalid token. Try to relogin"
                    # firebase_admin._token_gen.ExpiredIdTokenError
                    elif search.group(1) == "ExpiredIdTokenError":
                        text = "Token expired. Try to relogin"
                    # firebase_admin._token_gen.CertificateFetchError
                    elif search.group(1) == "CertificateFetchError":
                        text = "Server can't connect to authentication authority. Try again later"
                    elif search.group(1) == "RevokedIdTokenError":
                        text = "Token revoked. Try to relogin"
                return JsonResponse(
                    {"error": "Authorization error. {}".format(text)}, status=401
                )
        return None
