""" Use JSON response for some exceptions """
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse


class ErrorMessageFormatter(MiddlewareMixin):
    """ Format exceptions as a JSON errors """

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            return JsonResponse({"error": exception.messages}, status=400)
        return None
