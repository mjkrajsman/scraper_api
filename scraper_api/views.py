from pyramid.view import view_config, view_defaults
from .models import DBSession, Page, WebScraper
import simplejson


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

    # TODO: split into texts and images?
    # TODO: tests for this
    @view_config(route_name='texts', request_method='POST')
    def create_text(self):
        scraper = WebScraper()

        # TODO: validation?
        new_url = scraper.normalize_url(self.request.params['url'])
        new_text = scraper.get_text_from_url(new_url)

        image_source_urls = scraper.get_image_links_from_url(new_url)
        image_local_urls = scraper.get_images(image_source_urls, destination='img')
        new_images = '; '.join(image_local_urls)

        new_page = Page(url=new_url, text=new_text, images=new_images)
        DBSession.add(new_page)
        DBSession.flush()
        DBSession.refresh(new_page)
        self.request.response.status = '200 OK'
        # TODO: handle failures
        return simplejson.dumps(new_page, for_json=True)

