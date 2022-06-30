from django.http import JsonResponse
from django.shortcuts import render


class Response:

    code_200 = {"response": "200", "message": "Ok"}
    code_201 = {"response": "201", "message": "Created"}
    code_204 = {"response": "204", "message": "No Content"}
    code_400 = {"response": "400", "message": "Bad Request"}
    code_401 = {"response": "401", "message": "Unauthorized"}
    code_403 = {"response": "403", "message": "Forbidden"}
    code_404 = {"response": "404", "message": "Not Found"}
    code_405 = {"response": "405", "message": "Method Not Allowed"}
    code_500 = {"response": "500", "message": "Internal Server Error"}
    code_501 = {"response": "501", "message": "Not Implemented"}
    code_502 = {"response": "502", "message": "Bad Gateway"}
    code_503 = {"response": "503", "message": "Service Unavailable"}
    code_504 = {"response": "504", "message": "Gateway Timeout"}


class ResponseMixin(object):
    @staticmethod
    def json_response_200():
        return JsonResponse(Response.code_200, status=200)

    @staticmethod
    def json_response_201():
        return JsonResponse(Response.code_201, status=201)

    @staticmethod
    def json_response_204():
        return JsonResponse(Response.code_204, status=204)

    @staticmethod
    def json_response_400():
        return JsonResponse(Response.code_400, status=400)

    @staticmethod
    def json_response_401():
        return JsonResponse(Response.code_401, status=401)

    @staticmethod
    def json_response_403():
        return JsonResponse(Response.code_403, status=403)

    @staticmethod
    def json_response_404():
        return JsonResponse(Response.code_404, status=404)

    @staticmethod
    def json_response_405():
        return JsonResponse(Response.code_405, status=405)

    @staticmethod
    def json_response_500():
        return JsonResponse(Response.code_500, status=500)

    @staticmethod
    def json_response_501():
        return JsonResponse(Response.code_501, status=501)

    @staticmethod
    def json_response_502():
        return JsonResponse(Response.code_502, status=502)

    @staticmethod
    def json_response_503():
        return JsonResponse(Response.code_503, status=503)

    @staticmethod
    def json_response_504():
        return JsonResponse(Response.code_504, status=504)

    @staticmethod
    def http_responce_400(request):
        return render(request, Response.code_400, status=400)

    @staticmethod
    def http_responce_401(request):
        return render(request, Response.code_401, status=401)

    @staticmethod
    def http_responce_403(request):
        return render(request, Response.code_403, status=403)

    @staticmethod
    def http_responce_404(request):
        return render(request, "404.html", Response.code_404, status=404)

    @staticmethod
    def http_responce_405(request):
        return render(request, Response.code_405, status=405)
