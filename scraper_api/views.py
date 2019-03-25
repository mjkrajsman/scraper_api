from pyramid.view import view_config, view_defaults
from .models import DBSession, Page, WebScraper
import simplejson


@view_defaults(renderer='json')
class View(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='texts', request_method='GET')
    def list_texts(self):
        pages = DBSession.query(Page).order_by(Page.id)
        pages_dict = {}
        for page in pages.all():
            pages_dict[page.id] = page
        self.request.response.status = '200 OK'
        # TODO: handle failures
        return simplejson.dumps(pages_dict, for_json=True)

    @view_config(route_name='texts', request_method='POST')
    def create_text(self):
        # TODO: validation?
        # TODO: image scraping
        scraper = WebScraper()
        new_url = (self.request.params['url']).encode('utf-8')
        new_text = scraper.get_text_from_url(new_url)
        new_page = Page(url=new_url, text=new_text)
        DBSession.add(new_page)
        DBSession.flush()
        DBSession.refresh(new_page)
        self.request.response.status = '200 OK'
        # TODO: handle failures
        return simplejson.dumps(new_page, for_json=True)

    @view_config(route_name='text', request_method='GET')
    def read_text(self):
        page_id = int(self.request.matchdict['id'])
        page = DBSession.query(Page).filter_by(id=page_id).one()
        self.request.response.status = '200 OK'
        # TODO: handle failures
        return simplejson.dumps(page, for_json=True)
