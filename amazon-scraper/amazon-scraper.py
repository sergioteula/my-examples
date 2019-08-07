# -*- coding: utf-8 -*-

"""Amazon scraper."""

# Custom modules
from helpers.web import Browser, is_url
from data.data import Store, User
from helpers.tools import format_price, clean_text, get_float
import constants.service as service
from scrapers.tools import write_all_affiliate_url
import custom.config as conf

# Standard modules
import logging
import re

# Third party modules
from bs4 import BeautifulSoup
from amazon.api import AmazonAPI, AsinNotFound, LookupException, RequestThrottled

logger = logging.getLogger(__name__)

if conf.amazon.ENABLED:
    amazon = AmazonAPI(conf.amazon.KEY, conf.amazon.SECRET, conf.amazon.TAG,
                       region=conf.amazon.REGION, MaxQPS=0.1, Timeout=6)


def get_asin(url):
    asin = False
    clean_url = url.split('?')[0]
    split_url = clean_url.replace('?', '/').replace('&', '/').split('/')
    for c in list(reversed(split_url)):
        if len(c) == 10 and c.isalnum():
            asin = c
            break
    return asin


def clean_url(url, asin):
    clean_url = url
    if 'offer-listing' in url:
        if '&tag=' in url:
            clean_url = re.sub(r'&tag=.*-[0-9][0-9]', '', url)
        elif '?tag=' in url:
            clean_url = re.sub(r'\?tag=.*-[0-9][0-9].', '?', url)
            if 'tag=' in clean_url:
                clean_url = re.sub(r'\?tag=.*-[0-9][0-9]', '', clean_url)
    else:
        url_watermark = url.split('/', 3)[-1]
        url_watermark = url.replace(url_watermark, '')
        clean_url = url.split('?')[0]

    if 'offer-listing' not in url:
        if conf.amazon.WATERMARK:
            clean_url = url_watermark + '_customwatermark_/dp/' + asin
        if 'th=1' in url:
            clean_url += '&th=1'
        if 'psc=1' in url:
            clean_url += '&psc=1'
        if '&m=' in url.replace('?', '&'):
            model = re.findall(r'\&m\=.*', url.replace('?', '&'))[0].split('&')[1]
            clean_url += '&' + model

    return clean_url


def scrape_refurbish(asin, user_id):
    store = Store(user_id)
    url = ('https://www.amazon.es/gp/offer-listing/' + asin
           + '/ref=olp_f_used?f_usedAcceptable=true&f_usedGood=true&f_used='
           'true&f_usedLikeNew=true&f_usedVeryGood=true')

    web_status = False
    web = Browser(url, Browser.SIMPLE_PROXY)
    if web:
        soup = BeautifulSoup(web.page, 'lxml')
        web_status = True
    else:
        logger.warning('Error loading web')
        web = Browser(url, Browser.BROWSER)
        if web:
            soup = BeautifulSoup(web.page, 'lxml')
            web_status = True
        else:
            logger.warning('Error loading web with alternative method')

    if web_status:
        price_list = []
        status_list = []

        prices = soup.find('div', {'id': 'olpOfferList'})
        prices = prices.findAll('span', {'class': 'olpOfferPrice'})
        for price in prices:
            price_list.append(format_price(price.text))

        statuses = soup.find('div', {'id': 'olpOfferList'})
        statuses = statuses.findAll('span', {'class': 'olpCondition'})
        for status in statuses:
            status_list.append(clean_text(status.text.split('- ')[-1]))

        if price_list and status_list:
            store.original_refurbish_url = url
            store.refurbish_price_list = price_list
            store.refurbish_status_list = status_list
            store.refurbish_price = price_list[0]
            store.refurbish_status = status_list[0]
            write_all_affiliate_url(user_id, url, service.AMAZON, refurbish=True)


def scrape(url, user_id):
    store = Store(user_id)
    user = User(user_id)
    original_url = url
    aws_status = False
    web_status = False
    asin = False

    if 'offer-listing' in url:
        offer_listing = True
    else:
        offer_listing = False

    if len(url) == 10 and url.isalnum():
        asin = url
        url = 'https://www.amazon.es/dp/' + asin
    else:
        asin = get_asin(url)

    url = clean_url(url, asin)

    if conf.amazon.ENABLED and asin:
        try:
            product = amazon.lookup(ItemId=asin)
            aws_status = True
        except AsinNotFound:
            logger.warning('ASIN %s not found with API' % (asin))
        except LookupException:
            logger.error('API lookup exception for %s' % (asin))
        except RequestThrottled:
            logger.error('API request throttled exception')
        except Exception:
            logger.exception('API exception for asin %s' % (asin))

    web = Browser(url, Browser.SIMPLE_PROXY)
    if web:
        soup = BeautifulSoup(web.page, 'lxml')
        web_status = True
    else:
        web = Browser(url, Browser.BROWSER)
        if web:
            soup = BeautifulSoup(web.page, 'lxml')
            web_status = True

    if web_status is True or aws_status is True:
        store.clear()
        if user.amazon_refurbish and not offer_listing:
            scrape_refurbish(asin, user_id)

        # Get the title
        title = ''
        if aws_status:
            if product.title:
                title = product.title
        if web_status and title == '':
            if offer_listing:
                try:
                    title = soup.find('div', {'id': 'olpProductDetails'})
                    title = title.find('h1', {'class': 'a-size-large a-spacing-none'}).text
                    title = clean_text(title)
                except Exception:
                    pass
            else:
                try:
                    title = soup.find('span', {'id': 'productTitle'}).text
                    title = clean_text(title)
                except Exception:
                    pass

        # Get the image
        image = ''
        if web_status:
            if offer_listing:
                try:
                    image = soup.find('div', {'id': 'olpProductImage'}).findAll('img')[0].get('src')
                    image = re.sub(r'._.*_.', '._AC_.', image)
                except Exception:
                    image = ''
            else:
                try:
                    image = soup.find('div', {'id': 'main-image-container'})
                    image = image.find('div', {'class': 'imgTagWrapper'})
                    image = image.findAll('img')[0].get('data-old-hires')
                    if image == '':
                        image = soup.find('div', {'id': 'main-image-container'})
                        image = image.find('div', {'class': 'imgTagWrapper'}).findAll('img')[0]
                        image = image.get('src')
                    if is_url(image):
                        image = re.sub(r'._.*_.', '._AC_.', image)
                    else:
                        image = soup.find('div', {'id': 'main-image-container'})
                        image = image.find('div', {'class': 'imgTagWrapper'}).findAll('img')[0]
                        image = image.get('data-a-dynamic-image')
                        image = image.replace('"', ' ').replace('{', ' ').split()[0]
                        if is_url(image):
                            image = re.sub(r'._.*_.', '._AC_.', image)
                        else:
                            image = ''
                except Exception:
                    try:
                        image = soup.find('div', {'id': 'main-image-container'})
                        image = image.find('div', {'class': 'imgTagWrapper'}).findAll('img')[0]
                        image = image.get('src')
                        if is_url(image):
                            image = re.sub(r'._.*_.', '._AC_.', image)
                        else:
                            image = soup.find('div', {'id': 'main-image-container'})
                            image = image.find('div', {'class': 'imgTagWrapper'}).findAll('img')[0]
                            image = image.get('data-a-dynamic-image')
                            image = image.replace('"', ' ').replace('{', ' ').split()[0]
                            if is_url(image):
                                image = re.sub(r'._.*_.', '._AC_.', image)
                            else:
                                image = ''
                    except Exception:
                        image = ''
        if aws_status and image == '':
            if product.large_image_url:
                image = product.large_image_url
            elif product.medium_image_url:
                image = product.medium_image_url
            elif product.small_image_url:
                image = product.small_image_url

        # Get prices
        current_price = ''
        pvp = ''
        flash_price = ''
        day_price = ''
        is_flash = False
        is_day = False

        if web_status:
            # Get current price
            if offer_listing:
                try:
                    web_current_price = soup.find('span', {'class': 'olpOfferPrice'}).text
                    web_current_price = format_price(web_current_price, blank=True)
                except Exception:
                    web_current_price = ''
            else:
                try:
                    web_current_price = soup.find('div', {'id': 'price'})
                    web_current_price = web_current_price.find('span',
                                                               {'id': 'priceblock_ourprice'}).text
                    web_current_price = format_price(web_current_price, blank=True)
                except Exception:
                    try:
                        web_current_price = soup.find('div', {'id': 'price'})
                        web_current_price = web_current_price.find('span',
                                                                   {'id': 'priceblock_saleprice'})
                        web_current_price = web_current_price.text
                        web_current_price = format_price(web_current_price, blank=True)
                    except Exception:
                        try:
                            web_current_price = soup.find('div', {'id': 'price'})
                            web_current_price = web_current_price.find('span',
                                                                       {'id':
                                                                        'priceblock_dealprice'})
                            web_current_price = web_current_price.text
                            web_current_price = format_price(web_current_price, blank=True)
                        except Exception:
                            web_current_price = ''

            # Get customer reviews
            reviews_number = None
            reviews_score = None
            if web_status:
                try:
                    reviews_score = soup.find('span', {'class': 'a-icon-alt'}).text
                    reviews_score = reviews_score.split()[0].replace('.', ',')
                    reviews_number = soup.find('span', {'id': 'acrCustomerReviewText'}).text
                    reviews_number = reviews_number.split()[0]
                except Exception:
                    pass

            # Get pvp price
            try:
                web_pvp = soup.find('div', {'id': 'price'})
                web_pvp = web_pvp.find('span', {'class': 'a-text-strike'}).text
                web_pvp = format_price(web_pvp, blank=True)
            except Exception:
                web_pvp = ''

            # Get flash or day price
            try:
                prices = soup.find('div', {'id': 'price'})
                try:
                    web_flash = prices.find('span', {'id': 'priceblock_saleprice'}).text
                    web_flash = format_price(web_flash, blank=True)
                except Exception:
                    web_flash = ''
                try:
                    web_flash_alt = prices.find('span', {'id': 'priceblock_dealprice'}).text
                    web_flash_alt = format_price(web_flash_alt, blank=True)
                except Exception:
                    web_flash_alt = ''

                if web_flash and web_flash_alt:
                    if get_float(web_flash) > get_float(web_flash_alt):
                        web_flash = web_flash_alt
                elif web_flash_alt:
                    web_flash = web_flash_alt
            except Exception:
                web_flash = ''

            # Check if there is a flash or day offer
            try:
                is_flash = soup.find('div', {'id': 'LDBuybox'}).text
                if 'oferta flash' in is_flash.lower():
                    is_flash = True
                else:
                    is_flash = False
            except Exception:
                is_flash = False
            try:
                is_day = soup.find('div', {'id': 'unifiedPrice_feature_div'}).text
                if 'oferta del día' in is_day.lower():
                    is_day = True
                else:
                    is_day = False
            except Exception:
                is_day = False

        if aws_status:
            if product.list_price[0]:
                aws_pvp = format_price(product.list_price[0], blank=True)
            else:
                aws_pvp = ''

            if product.price_and_currency:
                aws_current_price = format_price(product.price_and_currency[0], blank=True)
            else:
                aws_current_price = ''

        # Adjust final prices
        if aws_status and not web_status:
            if aws_current_price == aws_pvp:
                current_price = aws_current_price
            else:
                current_price = aws_current_price
                pvp = aws_pvp
        elif not aws_status and web_status:
            if offer_listing:
                if web_current_price == web_pvp:
                    current_price = web_current_price
                else:
                    current_price = web_current_price
                    pvp = web_pvp
            else:
                if web_pvp == web_current_price:
                    current_price = web_current_price
                else:
                    pvp = web_pvp
                if is_day or is_flash:
                    if web_current_price:
                        if web_current_price == web_flash:
                            current_price = ''
                        elif not web_flash:
                            web_flash = web_current_price
                            current_price = ''
                        else:
                            current_price = web_current_price
                    if is_flash:
                        flash_price = web_flash
                    else:
                        day_price = web_flash
                else:
                    current_price = web_current_price
        else:
            if offer_listing:
                if web_current_price == aws_pvp:
                    current_price = web_current_price
                else:
                    current_price = web_current_price
                    pvp = aws_pvp
            else:
                if aws_pvp:
                    pvp = aws_pvp
                else:
                    pvp = web_pvp
                if is_day or is_flash:
                    if web_current_price:
                        if web_current_price == web_flash:
                            current_price = ''
                        elif not web_flash:
                            web_flash = web_current_price
                            current_price = ''
                        else:
                            current_price = web_current_price
                    if is_flash:
                        flash_price = web_flash
                    else:
                        day_price = web_flash
                else:
                    if aws_current_price:
                        current_price = aws_current_price
                    else:
                        current_price = web_current_price
                if current_price == pvp:
                    pvp = ''
            if pvp == flash_price:
                pvp = ''
            if pvp == day_price:
                pvp = ''
            if current_price == flash_price:
                current_price = ''
            if current_price == day_price:
                current_price = ''
            if (get_float(current_price) > get_float(pvp) or get_float(flash_price) > get_float(pvp)
                    or get_float(day_price) > get_float(pvp)):
                pvp = ''

        # Save results to database
        if title or image or current_price or flash_price or day_price or pvp:
            status = True
            store.service = service.AMAZON
            store.original_url = original_url
            write_all_affiliate_url(user_id, url, service.AMAZON)
            store.title = title
            store.image = image
            store.current_price = current_price
            store.pvp = pvp
            store.flash_price = flash_price
            store.day_price = day_price
            store.reviews_number = reviews_number
            store.reviews_score = reviews_score
        else:
            status = False
    else:
        status = False

    return status
