import json
from .models import Base, DBSession, ImagesScraper, Page, TextScraper
from pyramid import testing
from pyramid.paster import get_app
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
        model = Page(id=1, url='http://www.example.com',
                     text='Lorem ipsum dolor sit amet, consectetur adipiscing elit',
                     images='path1; path2; longer/path3')
        DBSession.add(model)
        model = Page(id=2, url='http://www.example2.com',
                     text='Lorem ipsum dolor sit amet, consectetur adipiscing elit2',
                     images='path11; path22; longer/path33')
        DBSession.add(model)
    return DBSession


class ViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = _init_testing_db()
        self.config = testing.setUp()
        self.mock_webpage_url = 'mock://test.com'
        self.mock_webpage_contents = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'

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
        request = testing.DummyRequest(params={'url': 'http://www.example2.com'})
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
        request = testing.DummyRequest(params={'url': 'http://www.example2.com'})
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

    def test_post_text(self) -> None:
        with requests_mock.Mocker() as m:
            m.get('mock://test.com', text=self.mock_webpage_contents)
            request = testing.DummyRequest(params={'url': 'mock://test.com'}, method='GET')
            inst = TextPoster(request)
            response = json.loads(inst.post_text())
            self.assertEqual(response['id'], 3)
            self.assertEqual(response['url'], 'mock://test.com')
            self.assertEqual(response['text'], 'Lorem ipsum dolor sit amet, consectetur adipiscing elit')

    # TODO: Add images
    def test_post_images(self) -> None:
        with requests_mock.Mocker() as m:
            m.get(self.mock_webpage_url, text=self.mock_webpage_contents)
            request = testing.DummyRequest(params={'url': self.mock_webpage_url}, method='GET')
            inst = ImagesPoster(request)
            response = json.loads(inst.post_images())
            self.assertEqual(response['id'], 3)
            self.assertEqual(response['url'], self.mock_webpage_url)
            self.assertEqual(response['text'], None)

    def test_scrap_text(self) -> None:
        text_scraper = TextScraper()
        with requests_mock.Mocker() as m:
            m.get(self.mock_webpage_url, text=self.mock_webpage_contents)
            scraped_text = text_scraper.scrap_text(self.mock_webpage_url)
            self.assertEqual(scraped_text, self.mock_webpage_contents)

    # TODO: Add images
    def test_scrap_images(self) -> None:
        images_scraper = ImagesScraper('/img')
        with requests_mock.Mocker() as m:
            m.get(self.mock_webpage_url, text=self.mock_webpage_contents)
            scraped_images = images_scraper.scrap_images(self.mock_webpage_url)
            self.assertEqual(scraped_images, [])


class FunctionalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = _init_testing_db()
        self.config = testing.setUp()
        app = get_app('development.ini')
        self.test_app = TestApp(app)
        self.mock_webpage_url = 'mock://test.com'
        self.mock_webpage_contents = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'

    def tearDown(self) -> None:
        DBSession.remove()
        self.session.remove()
        testing.tearDown()

    def test_get_all_texts(self) -> None:
        response = self.test_app.get('/texts', status=200)
        self.assertEqual(response.content_type, 'application/json')

    def test_get_text(self) -> None:
        response = self.test_app.get('/texts/1', status=200)
        self.assertEqual(response.content_type, 'application/json')

    def test_get_all_images(self) -> None:
        response = self.test_app.get('/images', status=200)
        self.assertEqual(response.content_type, 'application/json')

    def test_get_images(self) -> None:
        response = self.test_app.get('/images/1', status=200)
        self.assertEqual(response.content_type, 'application/json')

    def test_post_text(self) -> None:
        with requests_mock.Mocker() as m:
            m.get(self.mock_webpage_url, text=self.mock_webpage_contents)
            param = {'url': self.mock_webpage_url}
            response = self.test_app.post('/texts', param, status=201)
            self.assertEqual(response.content_type, 'application/json')

    def test_post_images(self) -> None:
        with requests_mock.Mocker() as m:
            m.get(self.mock_webpage_url, text=self.mock_webpage_contents)
            param = {'url': self.mock_webpage_url}
            response = self.test_app.post('/images', param, status=201)
            self.assertEqual(response.content_type, 'application/json')
