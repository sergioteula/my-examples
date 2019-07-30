# -*- coding: utf-8 -*-

# Standard modules
import sqlite3


def add(channel, post, service, title='', long_url='', short_url='', current_price='', pvp='',
        flash_code='', buttons=''):
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""INSERT INTO buffer
                          (channel, post, service, title, long_url, short_url, current_price,
                          pvp, flash_code, buttons) VALUES
                          (%d, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")""" %
                       (channel, post, service, title, long_url, short_url, current_price,
                        pvp, flash_code, buttons))
        db.commit()
        result = True
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result


def read(channel):
    try:
        db = sqlite3.connect('./saves/mydb.db')
        cursor = db.cursor()
        cursor.execute("""SELECT id_number, post, service, title, long_url, short_url,
                          current_price, pvp, flash_code, buttons
                          FROM buffer WHERE channel = %d""" % (channel))
        info = cursor.fetchall()
        db.commit()

        result = {}
        result['id_number'] = []
        result['post'] = []
        result['service'] = []
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
            result['title'].append(row[3])
            result['long_url'].append(row[4])
            result['short_url'].append(row[5])
            result['current_price'].append(row[6])
            result['pvp'].append(row[7])
            result['flash_code'].append(row[8])
            result['buttons'].append(row[9])

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
        cursor.execute("""DELETE FROM buffer WHERE id_number = %d""" % (id_number))
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
        cursor.execute("""DELETE FROM buffer WHERE channel = %d""" % (channel))
        db.commit()
        result = True
    except Exception:
        db.rollback()
        result = False
    finally:
        db.close()
    return result
