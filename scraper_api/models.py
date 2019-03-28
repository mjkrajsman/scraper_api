from bs4 import BeautifulSoup
import os
from pyramid.security import Allow, Everyone
import re
import requests
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import urllib.parse
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Page(Base):
    __tablename__ = 'scraped_data'
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    text = Column(Text)
    images = Column(Text)


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request) -> None:
        pass


class UrlNormalizer(object):
    @staticmethod
    def normalize_url(website_url: str) -> str:
        split_url = urllib.parse.urlsplit(website_url)
        return split_url.scheme + '://' + split_url.netloc


class TextScraper(object):
    @staticmethod
    def scrape_text(website_url: str) -> str:
        html = requests.get(website_url)
        soup = BeautifulSoup(html.content, features="lxml")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        whitespace_removed_text = re.sub("\s+", " ", text)
        return whitespace_removed_text


class ImageScraper(object):
    def __init__(self, destination: str) -> None:
        self.destination = destination

    def scrape_images(self, website_url: str) -> list:
        image_source_urls = self._get_image_urls(website_url)
        if not os.path.exists(str(self.destination)):
            os.makedirs(str(self.destination))
        links = []
        for src in image_source_urls:
            link = self._scrape_image(src)
            links.append(link)
        return links

    @staticmethod
    def _get_image_urls(website_url: str) -> list:
        image_urls = []
        html = requests.get(website_url)
        soup = BeautifulSoup(html.content, features="lxml")
        for img in soup.findAll('img'):
            image_url = img.get('src')
            image_url = urllib.parse.urljoin(website_url, image_url)
            image_urls.append(image_url)
        image_urls = list(dict.fromkeys(image_urls))
        return image_urls

    def _scrape_image(self, source: str) -> str:
        r = requests.get(source)
        img_name = source.replace("://", "_").replace("/", "_")
        img_location = '%s/%s' % (self.destination, img_name)
        # open(img_location, 'wb').write(r.content)
        with open(img_location, 'wb') as f:
            f.write(r.content)
        return img_location
