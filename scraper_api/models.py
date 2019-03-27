from pyramid.security import Allow, Everyone
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import requests
import os
from bs4 import BeautifulSoup
import re
import urllib.parse

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Page(Base):
    __tablename__ = 'scraped_data'
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    text = Column(Text)
    images = Column(Text)

    def __json__(self):
        return {
            'id': self.id,
            'url': self.url,
            'text': self.text,
            'images': self.images
        }

    for_json = __json__

    @classmethod
    def from_json(cls, source):
        obj = cls()
        obj.id = source['id']
        obj.url = source['url']
        obj.text = source['text']
        obj.images = source['images']
        return obj


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass


class TextScraper(object):
    @staticmethod
    def get_text_from_url(website_url):
        html = requests.get(website_url)
        soup = BeautifulSoup(html.content, features="lxml")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        whitespace_removed_text = re.sub("\s+", " ", text)
        return whitespace_removed_text


class ImageScraper(object):
    def get_images(self, website_url, destination='img', verbose=False):
        image_source_urls = self._get_image_urls(website_url)
        if not os.path.exists(str(destination)):
            os.makedirs(str(destination))
        links = []
        for src in image_source_urls:
            link = self._get_image(src, destination, verbose)
            links.append(link)
        return links

    @staticmethod
    def _get_image_urls(website_url, verbose=False):
        image_urls = []
        html = requests.get(website_url)
        soup = BeautifulSoup(html.content, features="lxml")
        for img in soup.findAll('img'):
            image_url = img.get('src')
            image_url = urllib.parse.urljoin(website_url, image_url)
            image_urls.append(image_url)
        image_urls = list(dict.fromkeys(image_urls))
        if verbose:
            print("Found " + str(len(image_urls)) + " images.")
        return image_urls

    @staticmethod
    def _get_image(source, destination='img', verbose=False):
        if verbose:
            print("Processing image: " + source)
        r = requests.get(source)
        img_name = source.replace("://", "_").replace("/", "_")
        img_location = '%s/%s' % (str(destination), img_name)
        # open(img_location, 'wb').write(r.content)
        with open(img_location, 'wb') as f:
            f.write(r.content)
        return img_location
