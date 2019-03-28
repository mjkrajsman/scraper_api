import json
from .models import DBSession, ImagesScraper, Page, TextScraper
from pyramid.view import view_config, view_defaults
from typing import ClassVar, Dict, List


@view_defaults(renderer='json', request_method='GET')
class TextGetter(object):
    def __init__(self, request) -> None:
        self.request = request

    @view_config(route_name='texts')
    def get_all_texts(self) -> str:

        if 'url' in self.request.params:
            website_url: str = self.request.params['url']
            pages = DBSession.query(Page.id, Page.url, Page.text)\
                .order_by(Page.id).filter_by(url=website_url)
        else:
            pages = DBSession.query(Page.id, Page.url, Page.text).order_by(Page.id)
        pages_dict: ClassVar[Dict] = {}
        for page in pages.all():
            pages_dict[page.id] = dict(id=page.id, url=page.url, text=page.text)

        if len(pages_dict) == 0:
            self.request.response.status = '404 Not Found'
        else:
            self.request.response.status = '200 OK'

        return json.dumps(pages_dict)

    @view_config(route_name='text')
    def get_text(self) -> str:
        page_id: int = self.request.matchdict['id']
        page = DBSession.query(Page.id, Page.url, Page.text).filter_by(id=page_id).first()
        if page is None:
            self.request.response.status = '404 Not Found'
            page = Page()
        else:
            self.request.response.status = '200 OK'

        return json.dumps(dict(id=page.id, url=page.url, text=page.text))


@view_defaults(renderer='json', request_method='GET')
class ImagesGetter(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='images')
    def get_all_images(self) -> str:
        if 'url' in self.request.params:
            website_url: str = self.request.params['url']
            pages = DBSession.query(Page.id, Page.url, Page.images)\
                .order_by(Page.id).filter_by(url=website_url)
        else:
            pages = DBSession.query(Page.id, Page.url, Page.images).order_by(Page.id)
        pages_dict: ClassVar[Dict] = {}
        for page in pages.all():
            pages_dict[page.id] = dict(id=page.id, url=page.url, images=page.images)

        if len(pages_dict) == 0:
            self.request.response.status = '404 Not Found'
        else:
            self.request.response.status = '200 OK'

        return json.dumps(pages_dict)

    @view_config(route_name='image')
    def get_images(self) -> str:
        page_id: int = self.request.matchdict['id']
        page = DBSession.query(Page.id, Page.url, Page.images).filter_by(id=page_id).first()
        if page is None:
            self.request.response.status = '404 Not Found'
            page = Page()
        else:
            self.request.response.status = '200 OK'

        return json.dumps(dict(id=page.id, url=page.url, images=page.images))


@view_defaults(renderer='json', request_method='POST')
class TextPoster(object):
    def __init__(self, request) -> None:
        self.request = request

    @view_config(route_name='texts')
    def post_text(self) -> str:
        scraper: TextScraper = TextScraper()
        if 'url' in self.request.params:
            new_url: str = self.request.params['url']
            new_text: str = scraper.scrap_text(new_url)
            page = DBSession.query(Page).filter_by(url=new_url).first()
            self.request.response.status = '201 Created'
            if page is None:
                page = Page(url=new_url, text=new_text)
            else:
                page.text: str = new_text
            DBSession.add(page)
            DBSession.flush()
            DBSession.refresh(page)
        else:
            self.request.response.status = '400 Bad Request'
            page = Page()
        return json.dumps(dict(id=page.id, url=page.url, text=page.text, images=page.images))


@view_defaults(renderer='json', request_method='POST')
class ImagesPoster(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='images')
    def post_images(self) -> str:
        scraper: ImagesScraper = ImagesScraper('img')
        if 'url' in self.request.params:
            new_url: str = self.request.params['url']
            image_local_urls: List[str] = scraper.scrap_images(new_url)
            new_images: str = '; '.join(image_local_urls)

            page = DBSession.query(Page).filter_by(url=new_url).first()
            self.request.response.status = '201 Created'
            if page is None:
                page = Page(url=new_url, images=new_images)
            else:
                page.images: str = new_images
            DBSession.add(page)
            DBSession.flush()
            DBSession.refresh(page)
        else:
            self.request.response.status = '400 Bad Request'
            page = Page()
        return json.dumps(dict(id=page.id, url=page.url, text=page.text, images=page.images))
