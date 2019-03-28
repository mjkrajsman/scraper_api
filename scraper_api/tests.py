import json
from .models import Base, DBSession, ImageScraper, Page, TextScraper
from pyramid import testing
from pyramid.paster import get_app
import requests
import requests_mock
from sqlalchemy import create_engine
import transaction
import unittest
from .views import ImagesGetter, ImagesPoster, TextGetter, TextPoster
from webtest import TestApp


def _init_testing_db():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Page(id=1, url='http://www.example.com', text='Lorem ipsum dolor sit amet, consectetur adipiscing elit',
                     images='path1; path2; longer/path3')
        DBSession.add(model)
        model = Page(id=2, url='http://www.example2.com', text='Lorem ipsum dolor sit amet, consectetur adipiscing elit2',
                     images='path11; path22; longer/path33')
        DBSession.add(model)
    return DBSession


class ViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = _init_testing_db()
        self.config = testing.setUp()

    def tearDown(self) -> None:
        self.session.remove()
        testing.tearDown()

    def test_get_all_texts(self) -> None:
        request = testing.DummyRequest()
        inst = TextGetter(request)
        response = json.loads(inst.get_all_texts())
        self.assertTrue('1' in response)
        self.assertTrue('2' in response)
        self.assertEqual(response['1']['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit')
        self.assertEqual(response['1']['url'], 'http://www.example.com')
        self.assertEqual(response['2']['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit2')
        self.assertEqual(response['2']['url'], 'http://www.example2.com')

    def test_get_all_texts_with_param(self) -> None:
        request = testing.DummyRequest(params={'url':'http://www.example2.com'})
        inst = TextGetter(request)
        response = json.loads(inst.get_all_texts())
        self.assertTrue('1' not in response)
        self.assertTrue('2' in response)
        self.assertEqual(response['2']['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit2')
        self.assertEqual(response['2']['url'], 'http://www.example2.com')

    def test_get_text(self) -> None:
        request = testing.DummyRequest()
        request.matchdict['id'] = '1'
        inst = TextGetter(request)
        response = json.loads(inst.get_text())
        self.assertEqual(response['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit')
        self.assertEqual(response['url'], 'http://www.example.com')

    def test_get_all_images(self) -> None:
        request = testing.DummyRequest()
        inst = ImagesGetter(request)
        response = json.loads(inst.get_all_images())
        self.assertEqual(response['1']['images'], 'path1; path2; longer/path3')
        self.assertEqual(response['1']['url'], 'http://www.example.com')

    def test_get_all_images_with_param(self) -> None:
        request = testing.DummyRequest(params={'url':'http://www.example2.com'})
        inst = ImagesGetter(request)
        response = json.loads(inst.get_all_images())
        self.assertTrue('1' not in response)
        self.assertTrue('2' in response)
        self.assertEqual(response['2']['images'], 'path11; path22; longer/path33')
        self.assertEqual(response['2']['url'], 'http://www.example2.com')

    def test_get_images(self) -> None:
        request = testing.DummyRequest()
        request.matchdict['id'] = '1'
        inst = ImagesGetter(request)
        response = json.loads(inst.get_images())
        self.assertEqual(response['images'], 'path1; path2; longer/path3')
        self.assertEqual(response['url'], 'http://www.example.com')


    # TODO: implement this, improve this - mock?
    def test_post_text(self) -> None:
        request = testing.DummyRequest(params={'url':'http://www.ztm.waw.pl'}, method = 'POST')
        inst = TextPoster(request)
        response = json.loads(inst.post_text())
        #self.assertEqual('Lorem ipsum dolor sit amet, consectetur adipiscing elit', response['url'])
        self.assertEqual(response['url'], 'http://www.ztm.waw.pl')

    # TODO: uncomment this, improve this - mock?
    # def test_post_images(self) -> None:
    #     request = testing.DummyRequest(params={'url':'http://www.ztm.waw.pl'}, method = 'POST')
    #     inst = ImagesPoster(request)
    #     response = json.loads(inst.post_images())
    #     #self.assertEqual('Lorem ipsum dolor sit amet, consectetur adipiscing elit', response['url'])
    #     self.assertEqual(response['url'], 'http://www.ztm.waw.pl')

    # # TODO: uncomment this, mock
    # def test_scrap_text(self) -> None:
    #     scraped_text = TextScraper.scrap_text()
    #     self.assertEqual(response['url'], 'http://www.ztm.waw.pl')
    #
    # # TODO: uncomment this, mock
    # def test_scrap_images(self) -> None:
    #     scraped_text = ImageScraper.scrap_images()
    #     self.assertEqual(response['url'], 'http://www.ztm.waw.pl')


class FunctionalTests(unittest.TestCase):
    def setUp(self) -> None:
        app = get_app('development.ini')
        self.test_app = TestApp(app)

    def tearDown(self) -> None:
        DBSession.remove()

    def test_get_all_texts(self) -> None:
        response = self.test_app.get('/texts', status=200)
        self.assertTrue((b'"{\\"1\\": {\\"id\\": 1, \\"url\\": \\"' in response.body) or (response.status_code == 404))
        self.assertEqual(response.content_type, 'application/json')

    # TODO: improve this
    def test_get_text(self):
        response = self.test_app.get('/texts/1', status=200)
        self.assertEqual(response.content_type, 'application/json')

    # TODO: improve this
    def test_get_all_images(self):
        response = self.test_app.get('/images', status=200)
        self.assertTrue((b'"{\\"1\\": {\\"id\\": 1, \\"url\\": \\"' in response.body) or (response.status_code == 404))
        self.assertEqual(response.content_type, 'application/json')

    # TODO: improve this
    def test_get_images(self):
        response = self.test_app.get('/images/1', status=200)
        self.assertEqual(response.content_type, 'application/json')

    # TODO: mock testing?
    def test_post_text(self) -> None:
        param = {'url': 'http://www.ztm.waw.pl'}
        response = self.test_app.post('/texts', param, status=201)
        self.assertTrue(b'\\"url\\": \\"http://www.ztm.waw.pl\\", \\"text\\": \\' in response.body)
        self.assertEqual(response.content_type, 'application/json')

    # TODO: uncomment later, mock testing?
    # def test_post_images(self):
    #     param = {'url': 'http://www.ztm.waw.pl'}
    #     res = self.test_app.post('/images', param, status=201)
    #     self.assertTrue(b'\\"url\\": \\"http://www.ztm.waw.pl\\", \\"text\\": \\' in res.body)
    #     self.assertEqual(res.content_type, 'application/json')
