#!/usr/bin/python

import requests
from lxml import etree
from requests import Timeout


class Downloader(object):
    """
    Download text content from URL
    """
    def __init__(self):
        self.request_session = requests.session()
        self.request_session.proxies

    def download(self, url:str, retry_count=0, http_headers=None, proxies=None, data=None):
        """Download the content from URL
        Args:
            url (str): The URL to download content from.
        Returns:
            str: The downloaded content, None if there's an error.
        """
        if http_headers:
            self.request_session.http_headers.update(http_headers)
        try:
            if data:
                content = self.request_session.post(url, data, proxies=proxies).content
            else:
                content = self.request_session.get(
                    url, proxies=proxies, timeout=3
                ).content
            content = content.decode("utf8", "ignore")
            content = str(content)
        except (ConnectionError, Timeout) as e:
            print("Downloader download ConnectionError or Timeout:" + str(e))
            content = None
            if retry_count > 0:
                self.download(url, retry_count - 1, http_headers, proxies, data)
        except Exception as e:
            print("Downloader download Exception: " + str(e))
            content = None
        return content

    def download_text(self, url:str):
        try:
            content = self.download(url)
            if content is None:
                return ""
            html = etree.HTML(content)
            context_text = "".join(html.itertext())
            context_list = [l for l in context_text.splitlines()]
            context_list = [l for l in context_list if not self.is_noise_text(l)]
            print("Download OK")
        except Exception as e:
            return ""
        return context_list

    @staticmethod
    def is_noise_text(text:str):
        forbidden_words = ["<", ">", "Cookies"]
        words = text.split()
        if len(text) < 50 or len(words) < 20 or len(text) / len(words) > 10:
            return True
        if any([s in text for s in forbidden_words]):
            return True
        return False
