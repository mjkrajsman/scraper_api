from pyramid.security import Allow, Everyone
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Page(Base):
    __tablename__ = 'scraped_data'
    id = Column(Integer, primary_key=True)
    url = Column(Text)
    text = Column(Text)
    # TODO: add images

    def __json__(self):
        return {
            'id': self.id,
            'url': self.url,
            'text': self.text
        }

    for_json = __json__

    @classmethod
    def from_json(cls, json):
        obj = cls()
        obj.id = json['id']
        obj.url = json['url']
        obj.text = json['text']
        return obj


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
