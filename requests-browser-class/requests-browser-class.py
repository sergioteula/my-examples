# -*- coding: utf-8 -*-

"""Requests and browser class with proxies compatibility."""

# Custom modules
from data.data import System

# Standard modules
import requests
import logging

# Third party modules
from selenium import webdriver
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException


USER_AGENT = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36'
              ' (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
logger = logging.getLogger(__name__)


class Browser:
    SIMPLE = 'simple'
    SIMPLE_PROXY = 'simple_proxy'
    BROWSER = 'browser'

    def __bool__(self):
        return bool(self.status)

    def __init__(self, url, mode, cookies=None):
        self.status = False
        self.page = False
        self.url = url

        if mode == self.SIMPLE:
            # Cookies with the format {'cookie_name': 'xxx', 'cookie_name': 'xxx'}
            try:
                page = requests.get(url, headers=USER_AGENT, cookies=cookies, timeout=5)
                if page.status_code == requests.codes.ok:
                    self.status = True
                    self.page = page.content
                    self.url = page.url
                else:
                    logger.warning('Unable to load %s with status code %s using simple method' %
                                   (url, page.status_code))
            except RequestException:
                logger.warning('Unable to load %s with simple method' % (url))

        elif mode == self.SIMPLE_PROXY:
            # Cookies with the format {'cookie_name': 'xxx', 'cookie_name': 'xxx'}
            system = System()

            if system.count_proxies() < 20:
                try:
                    page = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list'
                                        '/master/proxy-list.txt', headers=USER_AGENT, timeout=10)
                    if page.status_code == requests.codes.ok:
                        parser = page.text.split('\n\n')[1].split('\n')
                        for i in parser:
                            if 'H' in i and 'S' in i and '+' in i:
                                proxy = i.split()[0]
                                system.add_proxy(proxy)
                    else:
                        logger.error('Unable to update proxies with status code %s' %
                                     (page.status_code))

                except RequestException:
                    logger.error('Unable to update proxies')

            if system.count_proxies() > 0:
                while system.count_proxies() > 0:
                    try:
                        proxy = system.get_proxy()
                        page = requests.get(url, proxies={'http': proxy, 'https': proxy},
                                            headers=USER_AGENT, cookies=cookies, timeout=5)
                        if page.status_code == requests.codes.ok:
                            self.status = True
                            self.page = page.content
                            self.url = page.url
                            break
                        else:
                            system.remove_proxy(proxy)
                    except RequestException:
                        system.remove_proxy(proxy)
            else:
                logger.error('The proxy list is empty')

        elif mode == self.BROWSER:
            # Cookies with the format [{'name': 'xxx', 'value': 'xxx', 'domain': 'xxx'}, {cookie}]
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-gpu')
            options.add_argument('--headless')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument("--user-agent={'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2)"
                                 " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 "
                                 "Safari/537.36'}")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            try:
                browser = webdriver.Chrome(executable_path='./webdriver/chromedriver',
                                           chrome_options=options)
                browser.set_page_load_timeout(20)
            except Exception:
                browser = webdriver.Chrome(executable_path='./webdriver/chromedriver.exe',
                                           chrome_options=options)
                browser.set_page_load_timeout(20)
            try:
                browser.get(url)
                if cookies:
                    for cookie in cookies:
                        browser.add_cookie(cookie)
                    browser.get(url)
                self.page = browser.page_source
                self.status = True
            except WebDriverException:
                try:
                    browser.get(url)
                    self.page = browser.page_source
                    self.status = True
                except WebDriverException:
                    logger.error('Unable to load web %s using browser method' % (url))
            finally:
                browser.quit()
