from enum import Enum


class HttpRequestType(str, Enum):
    GET = 'GET'
    POST = 'POST'
