from pyramid.security import Allow, Everyone
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import requests
import os
from bs4 import BeautifulSoup
import json
import re

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


class WebScraper(object):
    @staticmethod
    def get_beautiful_soup(url):
        html = requests.get(url)
        soup = BeautifulSoup(html.content, features="lxml")
        return soup

    @staticmethod
    def get_json_from_text(text):
        return json.dumps(text)

    @staticmethod
    def normalize_url(url):
        if url[-1:] == "/":
            url = url[:-1]
        if url[0:8] != "https://" and url[0:7] != "http://":
            url = 'https://' + url
        return url

    @staticmethod
    def normalize_image_url(image_url, website_url):
        if image_url[0:2] == "./":
            image_url = website_url + image_url[1:]
        elif image_url[0:1] == "/":
            image_url = website_url + image_url
        # TODO: code below breaks some images. make workaround for images starting with subfolder name.
        # elif image_url.find(self.normalize_url(website_url)):
        #     image_url = website_url + "/" + image_url
        return image_url

    def get_text_from_url(self, website_url):
        soup = self.get_beautiful_soup(website_url)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        whitespace_removed_text = re.sub("\s+", " ", text)
        return whitespace_removed_text

    def get_image_links_from_url(self, website_url, verbose=False):
        image_urls = []
        soup = self.get_beautiful_soup(website_url)
        for img in soup.findAll('img'):
            image_url = img.get('src')
            image_url = self.normalize_image_url(image_url, website_url)
            image_urls.append(image_url)
        image_urls = list(dict.fromkeys(image_urls))
        if verbose:
            print("Found " + str(len(image_urls)) + " images.")
        return image_urls

    @staticmethod
    def get_image(source, destination='img', verbose=False):
        if verbose:
            print("Processing image: " + source)
        r = requests.get(source)
        img_name = source.replace("://", "_").replace("/", "_")
        img_location = '%s/%s' % (str(destination), img_name)
        # open(img_location, 'wb').write(r.content)
        with open(img_location, 'wb') as f:
            f.write(r.content)
        return img_location

    def get_images(self, source, destination='img', verbose=False):
        if not os.path.exists(str(destination)):
            os.makedirs(str(destination))
        links = []
        for src in source:
            link = self.get_image(src, destination, verbose)
            links.append(link)
        return links
