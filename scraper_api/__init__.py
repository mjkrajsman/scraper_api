from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          root_factory='scraper_api.models.Root')
    config.include('pyramid_chameleon')
    config.add_route('texts', '/texts')
    config.add_route('text', '/texts/{id}')
    config.scan('.views')
    return config.make_wsgi_app()
