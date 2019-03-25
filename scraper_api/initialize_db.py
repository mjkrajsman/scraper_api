import os
import sys
import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
from .models import DBSession, Page, Base


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = Page(url='www.example.com', text='A B C D')
        DBSession.add(model)
        model = Page(url='www.example2.com', text='A B C D E F G H')
        DBSession.add(model)
        model = Page(url='www.example3.com', text='A B C D E F G H I J K L')
        DBSession.add(model)
