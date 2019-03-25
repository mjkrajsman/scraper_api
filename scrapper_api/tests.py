import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_list_texts(self):
        from .views import Views

        request = testing.DummyRequest()
        inst = Views(request)
        response = inst.list_texts()
        self.assertEqual('GET all', response['text'])

    def test_create_text(self):
        from .views import Views

        request = testing.DummyRequest()
        inst = Views(request)
        response = inst.create_text()
        self.assertEqual('POST', response['text'])

    def test_read_text(self):
        from .views import Views

        request = testing.DummyRequest()
        inst = Views(request)
        response = inst.read_text()
        self.assertEqual('GET 1', response['text'])


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from scrapper_api import main

        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_list_texts(self):
        res = self.testapp.get('/texts', status=200)
        self.assertIn(b'{"text": "GET all"}', res.body)
        self.assertEqual(res.content_type, 'application/json')

    def test_create_text(self):
        res = self.testapp.post('/texts', status=200)
        self.assertIn(b'{"text": "POST"}', res.body)
        self.assertEqual(res.content_type, 'application/json')

    def test_read_text(self):
        res = self.testapp.get('/texts/1', status=200)
        self.assertIn(b'{"text": "GET 1"}', res.body)
        self.assertEqual(res.content_type, 'application/json')