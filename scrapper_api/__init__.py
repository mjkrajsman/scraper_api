from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_route('texts', '/texts')
    config.add_route('text', '/texts/{id}')
    config.scan('.views')
    return config.make_wsgi_app()