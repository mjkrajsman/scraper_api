import sqlalchemy
from bs4 import BeautifulSoup
import os
from pyramid.security import Allow, Everyone
import re
import requests
from requests import Response
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from typing import List
import urllib.parse
from zope.sqlalchemy import ZopeTransactionExtension


DBSession: sqlalchemy.orm.scoping.scoped_session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base: sqlalchemy.ext.declarative.api.DeclarativeMeta = declarative_base()


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


class TextScraper(object):
    @staticmethod
    def scrap_text(website_url: str) -> str:
        html: Response = requests.get(website_url)
        soup: BeautifulSoup = BeautifulSoup(html.content, features="lxml")
        for script in soup(["script", "style"]):
            script.extract()
        text: str = soup.get_text()
        whitespace_removed_text: str = re.sub("\s+", " ", text)
        return whitespace_removed_text


class ImageScraper(object):
    def __init__(self, destination: str) -> None:
        self.destination = destination

    def scrap_images(self, website_url: str) -> list:
        image_source_urls: List[str] = self._get_image_urls(website_url)
        if not os.path.exists(str(self.destination)):
            os.makedirs(str(self.destination))
        links: List[str] = []
        for src in image_source_urls:
            link: str = self._scrape_image(src)
            links.append(link)
        return links

    @staticmethod
    def _get_image_urls(website_url: str) -> List[str]:
        image_urls: List[str] = []
        html: Response = requests.get(website_url)
        soup: BeautifulSoup = BeautifulSoup(html.content, features="lxml")
        for img in soup.findAll('img'):
            image_url: str = img.get('src')
            image_url = urllib.parse.urljoin(website_url, image_url)
            image_urls.append(image_url)
        image_urls = list(dict.fromkeys(image_urls))
        return image_urls

    def _scrape_image(self, source: str) -> str:
        r: Response = requests.get(source)
        img_name: str = re.sub(r'[^\w^\.]',"_", source) #source.replace("://", "_").replace("/", "_")
        img_location: str = '%s/%s' % (self.destination, img_name)
        with open(img_location, 'wb') as f:
            f.write(r.content)
        return img_location
