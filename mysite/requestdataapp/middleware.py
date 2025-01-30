
import time

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def setup_useragent_on_request_middleware(get_response):
    print("initial call")
    def middleware(request: HttpRequest) -> HttpResponse:
        print("before get_response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get_response")
        return response

    return middleware

class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0
        self.user_last_request = {}
        self.timeout = 1

    def __call__(self, request: HttpRequest):
        user_ip = request.META.get('REMOTE_ADDR')
        print(user_ip)
        self.requests_count += 1
        print(self.user_last_request)

        # current_time = time.time()

        # if user_ip in self.user_last_request:
        #     last_request_time = self.user_last_request[user_ip]
        #     print("last request time", last_request_time)
        #     time_since_last_request = time.time() - last_request_time
        #     print("since last request - ", time_since_last_request)
        #     if time_since_last_request < self.timeout:
        #         return render(request, 'requestdataapp/throttle_error_handler.html')
        #
        # self.user_last_request[user_ip] = current_time
        print(f"requests count - {self.requests_count}")
        response = self.get_response(request)
        self.responses_count += 1
        print(f"responses number - {self.responses_count}")
        return response

    def process_exception (self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")
