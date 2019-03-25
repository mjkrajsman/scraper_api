from pyramid.security import Allow, Everyone
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import requests
from bs4 import BeautifulSoup
import json
import re

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
    def from_json(cls, source):
        obj = cls()
        obj.id = source['id']
        obj.url = source['url']
        obj.text = source['text']
        return obj


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass


class WebScraper(object):
    @staticmethod
    def get_beautiful_soup(url):
        html = requests.get(url)
        # print(html.status_code)
        soup = BeautifulSoup(html.content, features="lxml")
        return soup

    @staticmethod
    def get_json_from_text(text):
        return json.dumps(text)

    def get_text_from_url(self, url):
        soup = self.get_beautiful_soup(url)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        whitespace_removed_text = re.sub("\s+", " ", text)
        return whitespace_removed_text
