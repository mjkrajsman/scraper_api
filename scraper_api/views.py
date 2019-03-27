from pyramid.view import view_config, view_defaults
from .models import DBSession, Page, TextScraper, ImageScraper
import simplejson
import urllib.parse

@view_defaults(renderer='json')
class View(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='texts', request_method='GET')
    def list_text(self):
        pages = DBSession.query(Page.id, Page.url, Page.text).order_by(Page.id)
        pages_dict = {}
        for page in pages.all():
            pages_dict[page.id] = page

        if len(pages_dict) is 0:
            self.request.response.status = '404 Not Found'
        else:
            self.request.response.status = '200 OK'

        return simplejson.dumps(pages_dict, for_json=True)

    @view_config(route_name='text', request_method='GET')
    def read_text(self):
        page_id = int(self.request.matchdict['id'])
        page = DBSession.query(Page.id, Page.url, Page.text).filter_by(id=page_id).first()
        if page is None:
            self.request.response.status = '404 Not Found'
            page = {}
        else:
            self.request.response.status = '200 OK'

        return simplejson.dumps(page, for_json=True)

    # TODO: add image dowloading
    @view_config(route_name='images', request_method='GET')
    def list_images(self):
        pages = DBSession.query(Page.id, Page.url, Page.images).order_by(Page.id)
        pages_dict = {}
        for page in pages.all():
            pages_dict[page.id] = page

        if len(pages_dict) is 0:
            self.request.response.status = '404 Not Found'
        else:
            self.request.response.status = '200 OK'

        return simplejson.dumps(pages_dict, for_json=True)

    # TODO: add image dowloading
    @view_config(route_name='image', request_method='GET')
    def read_images(self):
        page_id = int(self.request.matchdict['id'])
        page = DBSession.query(Page.id, Page.url, Page.images).filter_by(id=page_id).first()
        if page is None:
            self.request.response.status = '404 Not Found'
            page = {}
        else:
            self.request.response.status = '200 OK'

        return simplejson.dumps(page, for_json=True)

    @view_config(route_name='texts', request_method='POST')
    def create_text(self):
        scraper = TextScraper()
        if 'url' in self.request.params:
            split_url = urllib.parse.urlsplit(self.request.params['url'])
            new_url = split_url.scheme + '://' + split_url.netloc
            new_text = scraper.get_text_from_url(new_url)
            page = DBSession.query(Page).filter_by(url=new_url).first()
            self.request.response.status = '201 Created'
            if page is None:
                page = Page(url=new_url, text=new_text)
            else:
                page.text = new_text
            DBSession.add(page)
            DBSession.flush()
            DBSession.refresh(page)
        else:
            self.request.response.status = '400 Bad Request'
            page = {}
        return simplejson.dumps(page, for_json=True)

    @view_config(route_name='images', request_method='POST')
    def create_images(self):
        scraper = ImageScraper()
        if 'url' in self.request.params:
            split_url = urllib.parse.urlsplit(self.request.params['url'])
            new_url = split_url.scheme + '://' + split_url.netloc
            image_local_urls = scraper.get_images(new_url, destination='img')
            new_images = '; '.join(image_local_urls)

            page = DBSession.query(Page).filter_by(url=new_url).first()
            self.request.response.status = '201 Created'
            if page is None:
                page = Page(url=new_url, images=new_images)
            else:
                page.images = new_images
            DBSession.add(page)
            DBSession.flush()
            DBSession.refresh(page)
        else:
            self.request.response.status = '400 Bad Request'
            page = {}
        return simplejson.dumps(page, for_json=True)

        # TODO: URLvalidation?
