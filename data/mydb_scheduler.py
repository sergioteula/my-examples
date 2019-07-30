# -*- coding: utf-8 -*-

# Standard modules
import sqlite3
import time


def add(channel, post, service, year, month, day, hour, minute, title='', long_url='',
        short_url='', current_price='', pvp='', flash_code='', buttons=''):
    datetime = '%04d-%02d-%02d %02d:%02d:00' % (year, month, day, hour, minute)
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""INSERT INTO scheduled
                          (channel, post, service, year, month, day, hour, minute, datetime,
                          title, long_url, short_url, current_price, pvp, flash_code, buttons)
                          VALUES (%d, "%s", "%s", %d, %d, %d, %d, %d, "%s", "%s", "%s", "%s",
                          "%s", "%s", "%s", "%s")""" %
                       (channel, post, service, year, month, day, hour, minute, datetime,
                        title, long_url, short_url, current_price, pvp, flash_code, buttons))
        db.commit()
        result = True
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def read(channel):
    year = time.localtime().tm_year
    month = time.localtime().tm_mon
    day = time.localtime().tm_mday
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""SELECT id_number, post, service, year, month, day, hour, minute,
                          title, long_url, short_url, current_price, pvp, flash_code, buttons
                          FROM scheduled
                          WHERE channel = %d AND year <= %d AND month <= %d AND day <= %d
                          AND hour <= %d AND minute <= %d ORDER BY datetime(datetime) ASC""" %
                       (channel, year, month, day, hour, minute))
        info = cursor.fetchall()
        db.commit()
        result = _save_dict(info)
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def read_all(channel):
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""SELECT id_number, post, service, year, month, day, hour, minute,
                          title, long_url, short_url, current_price, pvp, flash_code, buttons
                          FROM scheduled
                          WHERE channel = %d ORDER BY datetime(datetime) ASC""" % (channel))
        info = cursor.fetchall()
        db.commit()
        result = _save_dict(info)
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def delete(id_number):
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""DELETE FROM scheduled WHERE id_number = %d""" % (id_number))
        db.commit()
        result = True
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def delete_all(channel):
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""DELETE FROM scheduled WHERE channel = %d""" % (channel))
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
    result['post'] = []
    result['service'] = []
    result['year'] = []
    result['month'] = []
    result['day'] = []
    result['hour'] = []
    result['minute'] = []
    result['title'] = []
    result['long_url'] = []
    result['short_url'] = []
    result['current_price'] = []
    result['pvp'] = []
    result['flash_code'] = []
    result['buttons'] = []

    for row in info:
        result['id_number'].append(row[0])
        result['post'].append(row[1])
        result['service'].append(row[2])
        result['year'].append(row[3])
        result['month'].append(row[4])
        result['day'].append(row[5])
        result['hour'].append(row[6])
        result['minute'].append(row[7])
        result['title'].append(row[8])
        result['long_url'].append(row[9])
        result['short_url'].append(row[10])
        result['current_price'].append(row[11])
        result['pvp'].append(row[12])
        result['flash_code'].append(row[13])
        result['buttons'].append(row[14])

    return result
