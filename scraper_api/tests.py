import unittest
import transaction
import json
from pyramid import testing


def _init_testing_db():
    from sqlalchemy import create_engine
    from .models import (
        DBSession,
        Page,
        Base
        )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Page(url='www.example.com', text='Lorem ipsum dolor sit amet, consectetur adipiscing elit',
                     images='path1; path2; longer/path3')
        DBSession.add(model)
    return DBSession


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _init_testing_db()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_list_texts(self):
        from .views import View

        request = testing.DummyRequest()
        request.matchdict['id'] = '1'
        inst = View(request)
        response = json.loads(inst.list_text())
        self.assertEqual(response['1']['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit')
        self.assertEqual(response['1']['url'], 'www.example.com')

    def test_read_text(self):
        from .views import View

        request = testing.DummyRequest()
        request.matchdict['id'] = '1'
        inst = View(request)
        response = json.loads(inst.read_text())
        self.assertEqual(response['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit')
        self.assertEqual(response['url'], 'www.example.com')

    def test_list_images(self):
        from .views import View

        request = testing.DummyRequest()
        request.matchdict['id'] = '1'
        inst = View(request)
        response = json.loads(inst.list_images())
        self.assertEqual(response['1']['images'], 'path1; path2; longer/path3')
        self.assertEqual(response['1']['url'], 'www.example.com')

    def test_read_images(self):
        from .views import View

        request = testing.DummyRequest()
        request.matchdict['id'] = '1'
        inst = View(request)
        response = json.loads(inst.read_images())
        self.assertEqual(response['images'], 'path1; path2; longer/path3')
        self.assertEqual(response['url'], 'www.example.com')

    # TODO: implement POST test
    # def test_create_text(self):
    #     from .views import View
    #
    #     request = testing.DummyRequest()
    #     inst = View(request)
    #     response = inst.create_text()
    #     self.assertEqual('POST', response['text'])




class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('development.ini')
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        from .models import DBSession
        DBSession.remove()

    def test_list_texts(self):
        res = self.testapp.get('/texts', status=200)
        self.assertEqual(res.content_type, 'application/json')

    # TODO: implement POST test
    # def test_create_text(self):
    #     res = self.testapp.post('/texts', status=200)
    #     self.assertEqual(res.content_type, 'application/json')

    def test_read_text(self):
        res = self.testapp.get('/texts/1', status=200)
        self.assertEqual(res.content_type, 'application/json')

# TODO: SADeprecationWarning: SessionExtension is deprecated in favor of the SessionEvents listener interface.
