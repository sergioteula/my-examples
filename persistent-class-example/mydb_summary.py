# -*- coding: utf-8 -*-

# Standard modules
import sqlite3
from datetime import datetime, timedelta


def add(channel, year, month, day, hour, minute, title, post_url, long_url='', short_url='',
        current_price='', pvp='', flash_code=''):
    datetime = '%04d-%02d-%02d %02d:%02d:00' % (year, month, day, hour, minute)
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""INSERT INTO summary
                          (channel, year, month, day, hour, minute, datetime, title, post_url,
                          long_url, short_url, current_price, pvp, flash_code)
                          VALUES (%d, %d, %d, %d, %d, %d, "%s", "%s", "%s", "%s", "%s", "%s",
                          "%s", "%s")""" %
                       (channel, year, month, day, hour, minute, datetime, title, post_url,
                        long_url, short_url, current_price, pvp, flash_code))
        db.commit()
        result = True
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def read_day(channel, lag=0):
    time = datetime.today() - timedelta(days=lag)
    day = time.day
    month = time.month
    year = time.year
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""SELECT id_number, year, month, day, hour, minute, title, post_url,
                          long_url, short_url, current_price, pvp, flash_code
                          FROM summary WHERE channel = %d AND day = %d AND month = %d AND year = %d
                          ORDER BY datetime(datetime) ASC""" % (channel, day, month, year))
        info = cursor.fetchall()
        db.commit()
        result = _save_dict(info)
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def read_week(channel):
    result = {}
    for x in range(7):
        partial = read_day(x)
        if not result:
            result = partial
        else:
            for key in partial:
                result[key] = result[key] + partial[key]
    return result


def read_month(channel):
    time = datetime.today()
    month = time.month
    year = time.year
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""SELECT id_number, year, month, day, hour, minute, title, post_url,
                          long_url, short_url, current_price, pvp, flash_code
                          FROM summary WHERE channel = %d AND month = %d AND year = %d
                          ORDER BY datetime(datetime) ASC""" % (channel, month, year))
        info = cursor.fetchall()
        db.commit()
        result = _save_dict(info)
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def delete():
    time = datetime.today()
    month = time.month
    year = time.year
    if month <= 2:
        month = 12
        year = year - 1
    else:
        month = month - 2
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""DELETE FROM summary WHERE month <= %d AND year <= %d""" % (month, year))
        db.commit()
        result = True
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def _save_dict(info):
    result = {}
    result['id_number'] = []
    result['year'] = []
    result['month'] = []
    result['day'] = []
    result['hour'] = []
    result['minute'] = []
    result['title'] = []
    result['post_url'] = []
    result['long_url'] = []
    result['short_url'] = []
    result['current_price'] = []
    result['pvp'] = []
    result['flash_code'] = []

    for row in info:
        result['id_number'].append(row[0])
        result['year'].append(row[1])
        result['month'].append(row[2])
        result['day'].append(row[3])
        result['hour'].append(row[4])
        result['minute'].append(row[5])
        result['title'].append(row[6])
        result['post_url'].append(row[7])
        result['long_url'].append(row[8])
        result['short_url'].append(row[9])
        result['current_price'].append(row[10])
        result['pvp'].append(row[11])
        result['flash_code'].append(row[12])

    return result
