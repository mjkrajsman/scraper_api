from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
    )
import pyramid.httpexceptions as exc
from pyramid.response import Response

@view_defaults(renderer='json')
class Views(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='texts', request_method='GET')
    def list_texts(self):
        self.request.response.status = '200 OK'
        return {'text': 'GET all'}

    @view_config(route_name='texts', request_method='POST')
    def create_text(self):
        self.request.response.status = '200 OK'
        return {'text': 'POST'}

    @view_config(route_name='text', request_method='GET')
    def read_text(self):
        self.request.response.status = '200 OK'
        return {'text': 'GET 1'}
