# -*- coding: utf-8 -*-

"""Module with classes to manage all the data."""

# Custom modules
from .persistent import Persistent
from custom.config import channel
import constants.status as status
import constants.common as common
import data.mydb_buffer as mydb_buffer
import data.mydb_scheduler as mydb_scheduler
import data.mydb_summary as mydb_summary

# Standard modules
import random
import time


class User(Persistent):
    """Class with all the information related to the user. Init with user id."""
    def _init(self):
        # User parameters
        self.channel = 0
        self.channels = []
        self.status = status.DEFAULT
        self.service = status.DEFAULT
        self.text = common.EMPTY

        # User options
        self.multi_channel = False
        self.keep_channel = False
        self.amazon_refurbish = False

        # Channel parameters
        self._custom_footer = {}
        self._message_buttons = {}
        self._custom_image = {}
        self._shorten_URL = {}
        self._create_affiliate = {}

    def next_channel(self):
        self.channel += 1
        if self.channel >= channel.NUMBER:
            self.channel = 0
        return self.channel

    def toggle_channel(self, channel):
        channel = int(channel)
        if channel in self.channels:
            self.channels.remove(channel)
        else:
            self.channels.append(channel)
        self._save()
        return self.channels

    def clear_status(self):
        self.status = status.DEFAULT
        self.service = status.DEFAULT
        self.text = common.EMPTY

    def clear_channels(self):
        self.channels = []

    def clear_all(self):
        self._init()

    def change_multi_channel(self, value=None):
        if value is None:
            self.multi_channel = not self.multi_channel
        else:
            self.multi_channel = value
        return self.multi_channel

    def change_keep_channel(self, value=None):
        if value is None:
            self.keep_channel = not self.keep_channel
        else:
            self.keep_channel = value
        return self.keep_channel

    def change_amazon_refurbish(self, value=None):
        if value is None:
            self.amazon_refurbish = not self.amazon_refurbish
        else:
            self.amazon_refurbish = value
        return self.amazon_refurbish

    def custom_footer(self, channel):
        if channel not in self._custom_footer:
            self._custom_footer[channel] = common.EMPTY
        return self._custom_footer[channel]

    def write_custom_footer(self, channel, footer):
        self._custom_footer[channel] = footer

    def message_buttons(self, channel):
        if channel not in self._message_buttons:
            self._message_buttons[channel] = False
        return self._message_buttons[channel]

    def change_message_buttons(self, channel, value=None):
        if value is None:
            self._message_buttons[channel] = not self._message_buttons[channel]
        else:
            self._message_buttons[channel] = value
        return self._message_buttons[channel]

    def custom_image(self, channel):
        if channel not in self._custom_image:
            self._custom_image[channel] = False
        return self._custom_image[channel]

    def change_custom_image(self, channel, value=None):
        if value is None:
            self._custom_image[channel] = not self._custom_image[channel]
        else:
            self._custom_image[channel] = value
        return self._custom_image[channel]

    def shorten_URL(self, channel):
        if channel not in self._shorten_URL:
            self._shorten_URL[channel] = False
        return self._shorten_URL[channel]

    def change_shorten_URL(self, channel, value=None):
        if value is None:
            self._shorten_URL[channel] = not self._shorten_URL[channel]
        else:
            self._shorten_URL[channel] = value
        return self._shorten_URL[channel]

    def create_affiliate(self, channel):
        if channel not in self._create_affiliate:
            self._create_affiliate[channel] = False
        return self._create_affiliate[channel]

    def change_create_affiliate(self, channel, value=None):
        if value is None:
            self._create_affiliate[channel] = not self._create_affiliate[channel]
        else:
            self._create_affiliate[channel] = value
        return self._create_affiliate[channel]


class Store(Persistent):
    """Class with the information to create the message. Init with user id."""
    def _init(self):
        # Common parameters for all channels
        self.post = common.EMPTY
        self.title = common.EMPTY
        self.image = common.EMPTY
        self.coupon_price = common.EMPTY
        self.coupon = common.EMPTY
        self.current_price = common.EMPTY
        self.flash_price = common.EMPTY
        self.day_price = common.EMPTY
        self.pvp = common.EMPTY
        self.original_url = common.EMPTY
        self.description = common.EMPTY
        self.header = common.EMPTY
        self.footer = common.EMPTY
        self.service = common.EMPTY
        self.buttons = common.EMPTY
        self.refurbish_price_list = []
        self.refurbish_status_list = []
        self.refurbish_price = common.EMPTY
        self.refurbish_status = common.EMPTY
        self.customer_reviews = None
        self.edited = False

        # Parameters specific for each channel
        self._custom_image = {}
        self._long_url = {}
        self._short_url = {}
        self._refurbish_url = {}
        self._refurbish_short_url = {}

    def clear(self):
        self._init()

    def custom_image(self, channel):
        if channel not in self._custom_image:
            self._custom_image[channel] = common.EMPTY
        return self._custom_image[channel]

    def write_custom_image(self, channel, custom_image):
        self._custom_image[channel] = custom_image

    def long_url(self, channel):
        if channel not in self._long_url:
            self._long_url[channel] = common.EMPTY
        return self._long_url[channel]

    def write_long_url(self, channel, long_url):
        self._long_url[channel] = long_url

    def short_url(self, channel):
        if channel not in self._short_url:
            self._short_url[channel] = common.EMPTY
        return self._short_url[channel]

    def write_short_url(self, channel, short_url):
        self._short_url[channel] = short_url

    def refurbish_url(self, channel):
        if channel not in self._refurbish_url:
            self._refurbish_url[channel] = common.EMPTY
        return self._refurbish_url[channel]

    def write_refurbish_url(self, channel, refurbish_url):
        self._refurbish_url[channel] = refurbish_url

    def refurbish_short_url(self, channel):
        if channel not in self._refurbish_short_url:
            self._refurbish_short_url[channel] = common.EMPTY
        return self._refurbish_short_url[channel]

    def write_refurbish_short_url(self, channel, refurbish_short_url):
        self._refurbish_short_url[channel] = refurbish_short_url

    def flash_code(self):
        if self.coupon_price:
            flash_code = self.coupon_price + ' ' + self.coupon
        elif self.day_price:
            flash_code = self.day_price + ' day_price'
        elif self.flash_price:
            flash_code = self.flash_price + ' flash_price'
        else:
            flash_code = ''
        return flash_code


class System(Persistent):
    """Class with parameters common for all users. Don't use any id."""
    def _init(self):
        self._last_post = {}
        self.proxies = set()
        self._buffer_status = {}
        self._buffer_time = {}
        self._buffer_counter = {}
        self._scheduled_status = {}

    def write_last_post(self, channel, post_id):
        self._last_post[channel] = ('https://t.me/' + channel.ALIAS[channel].replace('@', '')
                                    + '/' + str(post_id))
        return self._last_post[channel]

    def last_post(self, channel):
        if channel not in self._last_post:
            self._last_post[channel] = 'https://t.me/' + channel.ALIAS[channel].replace('@', '')
        return self._last_post[channel]

    def add_proxy(self, proxy):
        self.proxies.add(proxy)
        self._save()

    def get_proxy(self):
        return random.choice(list(self.proxies))

    def remove_proxy(self, proxy):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self._save()

    def clear_proxies(self):
        self.proxies = set()

    def buffer_status(self, channel):
        if channel not in self._buffer_status:
            self._buffer_status[channel] = True
        return self._buffer_status[channel]

    def change_buffer_status(self, channel, value=None):
        if value is None:
            self._buffer_status[channel] = not self._buffer_status[channel]
        else:
            self._buffer_status[channel] = value
        return self._buffer_status[channel]

    def buffer_time(self, channel):
        if channel not in self._buffer_time:
            self._buffer_time[channel] = 30
        return self._buffer_time[channel]

    def write_buffer_time(self, channel, value):
        self._buffer_time[channel] = value

    def buffer_counter(self, channel):
        if channel not in self._buffer_counter:
            self._buffer_counter[channel] = 0
        return self._buffer_counter[channel]

    def write_buffer_counter(self, channel, value):
        self._buffer_counter[channel] = value

    def scheduled_status(self, channel):
        if channel not in self._scheduled_status:
            self._scheduled_status[channel] = True
        return self._scheduled_status[channel]

    def write_scheduled_status(self, channel, value=None):
        if value is None:
            self._scheduled_status[channel] = not self._scheduled_status[channel]
        else:
            self._scheduled_status[channel] = value
        return self._scheduled_status[channel]


class Affiliate(Persistent):
    """Class with the affiliate codes. Don't use any id."""
    def _init(self):
        self._front_affiliate = {}
        self._rear_affiliate = {}

    def clear(self):
        self._init()

    def _init_affiliate(self, service, channel):
        if service not in self._front_affiliate:
            self._front_affiliate[service] = {}
        elif channel not in self._front_affiliate[service]:
            self._front_affiliate[service][channel] = common.EMPTY
        if service not in self.rear_affiliate:
            self._rear_affiliate[service] = {}
        elif channel not in self._rear_affiliate[service]:
            self._rear_affiliate[service][channel] = common.EMPTY

    def write_front_affiliate(self, service, channel, affiliate):
        self._init(service)
        self._front_affiliate[service][channel] = affiliate

    def write_rear_affiliate(self, service, channel, affiliate):
        self._init(service)
        self._rear_affiliate[service][channel] = affiliate

    def front_affiliate(self, service, channel):
        self._init(service)
        return self._front_affiliate[service][channel]

    def rear_affiliate(self, service, channel):
        self._init(service)
        return self._rear_affiliate[service][channel]


class Loader:
    def __bool__(self):
        return bool(self.number)

    def __len__(self):
        return self.number

    def __call__(self, number):
        self.load_post(number)

    def __iter__(self):
        for x in range(self.number):
            self.load_post(x)
            yield self
        self.load_post(0)

    def _init(self):
        if self._raw:
            self.number = len(self._raw['id_number'])
        else:
            self.number = 0
        self.current = 0
        if self.number:
            self._load(0)

    def _refresh(self, status):
        if status:
            current = self.current
            self.__init__(self.channel)
            if self.number:
                self.load_post(current)

    def next_post(self):
        if self.number:
            self.current += 1
            if self.current >= self.number:
                self.load_post(0)
                return False
            else:
                self.load_post(self.current)
                return True
        else:
            self.current = 0
            return False

    def previous_post(self):
        if self.number:
            self.current -= 1
            if self.current < 0:
                self.load_post(self.number - 1)
                return False
            else:
                self.load_post(self.current)
                return True
        else:
            self.current = 0
            return False

    def load_post(self, number):
        if self.number:
            self.current = number
            if number >= self.number:
                self.current = self.number - 1
            self._load(self.current)
            return True
        else:
            self.current = 0
            return False


class Buffer(Loader):
    """Class to access buffer info. Loads the next post by default."""
    def __init__(self, channel):
        self.channel = channel
        self._raw = mydb_buffer.read(self.channel)
        self._init()

    def add(self, store):
        status = mydb_buffer.add(self.channel, store.post, store.service, store.title,
                                 store.long_url, store.short_url, store.current_price,
                                 store.pvp, store.flash_code(), store.buttons)
        self._refresh(status)
        return status

    def delete(self):
        if self.number:
            status = mydb_buffer.delete(self.id_number)
            self._refresh(status)
        else:
            status = False
        return status

    def delete_all(self):
        if self.number:
            status = mydb_buffer.delete_all(self.channel)
            self._refresh(status)
        else:
            status = False
        return status

    def _load(self, number):
        self.id_number = self._raw['id_number'][number]
        self.post = self._raw['post'][number]
        self.service = self._raw['service'][number]
        self.title = self._raw['title'][number]
        self.long_url = self._raw['long_url'][number]
        self.short_url = self._raw['short_url'][number]
        self.current_price = self._raw['current_price'][number]
        self.pvp = self._raw['pvp'][number]
        self.flash_code = self._raw['flash_code'][number]
        self.buttons = self._raw['buttons'][number]


class Scheduled(Loader):
    """Class to access scheduled info. Loads the next post by default."""
    def __init__(self, channel):
        self.channel = channel
        self._raw = mydb_scheduler.read(self.channel)
        self._init()

    def add(self, store, year, month, day, hour, minute):
        status = mydb_scheduler.add(self.channel, store.post, store.service, year, month, day, hour,
                                    minute, store.title, store.long_url, store.short_url,
                                    store.current_price, store.pvp, store.flash_code(),
                                    store.buttons)
        self._refresh(status)
        return status

    def read_current(self):
        self.__init__(self.channel)

    def read_all(self):
        self._raw = mydb_scheduler.read_all(self.channel)
        self._init()

    def delete(self):
        if self.number:
            status = mydb_scheduler.delete(self.id_number)
            self._refresh(status)
        else:
            status = False
        return status

    def delete_all(self):
        if self.number:
            status = mydb_scheduler.delete_all(self.channel)
            self._refresh(status)
        else:
            status = False
        return status

    def _load(self, number):
        self.id_number = self._raw['id_number'][number]
        self.post = self._raw['post'][number]
        self.service = self._raw['service'][number]
        self.year = self._raw['year'][number]
        self.month = self._raw['month'][number]
        self.day = self._raw['day'][number]
        self.hour = self._raw['hour'][number]
        self.minute = self._raw['minute'][number]
        self.title = self._raw['title'][number]
        self.long_url = self._raw['long_url'][number]
        self.short_url = self._raw['short_url'][number]
        self.current_price = self._raw['current_price'][number]
        self.pvp = self._raw['pvp'][number]
        self.flash_code = self._raw['flash_code'][number]
        self.buttons = self._raw['buttons'][number]


class Summary(Loader):
    """Class to access summary info."""
    def __init__(self, channel, period='day'):
        mydb_summary.delete()
        self.channel = channel
        if period == 'day':
            self._raw = mydb_summary.read_day(self.channel)
        elif period == 'week':
            self._raw = mydb_summary.read_week(self.channel)
        elif period == 'month':
            self._raw = mydb_summary.read_month(self.channel)
        self._init()

    def add(self, store, post_id):
        year = time.localtime().tm_year
        month = time.localtime().tm_mon
        day = time.localtime().tm_mday
        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min

        post_url = ('https://t.me/' + channel.ALIAS[self.channel].replace('@', '') + '/'
                    + str(post_id))

        status = mydb_summary.add(self.channel, year, month, day, hour, minute, store.title,
                                  post_url, store.long_url, store.short_url, store.current_price,
                                  store.pvp, store.flash_code())
        self._refresh(status)
        return status

    def read_day(self):
        self.__init__(self.channel, 'day')

    def read_week(self):
        self.__init__(self.channel, 'week')

    def read_month(self):
        self.__init__(self.channel, 'month')

    def _load(self, number):
        self.id_number = self._raw['id_number'][number]
        self.year = self._raw['year'][number]
        self.month = self._raw['month'][number]
        self.day = self._raw['day'][number]
        self.hour = self._raw['hour'][number]
        self.minute = self._raw['minute'][number]
        self.title = self._raw['title'][number]
        self.post_url = self._raw['post_url'][number]
        self.long_url = self._raw['long_url'][number]
        self.short_url = self._raw['short_url'][number]
        self.current_price = self._raw['current_price'][number]
        self.pvp = self._raw['pvp'][number]
        self.flash_code = self._raw['flash_code'][number]
