#!/usr/bin/env python

import decimal
import json
import os
import re
import sqlite3
import sys

import isodate


def demongo(s):
    def isodecode(m):
        date_string = m.group(2)
        date_obj = isodate.parse_datetime(date_string)
        return m.group(1) + date_obj.strftime("%s")

    # None
    s = re.sub(r'(:\s+)"None"', r'\1null', s)

    # ISO Date to Timestamp
    s = re.sub(r'(:\s+)ISODate\("(.+)"\)', isodecode, s)

    # Everything else (as string)
    s = re.sub(r'(:\s+)\w+\((.+)\)', r'\1\2', s)

    return json.loads(s, parse_float=decimal.Decimal)

def main():
    try:
        input_file = sys.argv[1]
    except IndexError:
        print('Usage: %s INPUT' % sys.argv[0])
        exit(1)

    output_file = 'carrefour.sqlite'

    try:
        os.remove(output_file)
    except FileNotFoundError:
        pass

    conn = sqlite3.connect(output_file)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE purchases(
            id      int primary key,
            mall    int                 not null,
            date    int                 not null,
            client  int
        )
    ''')

    c.execute('''
        CREATE TABLE items(
            id          int primary key,
            purchase_id int                 not null,
            description text                not null,
            cost        decimal(20,10)      not null,
            amount      int                 not null
        )
    ''')

    with open('data.json') as f:
        buff = ""
        for line in f:
            buff += line
            if line.startswith('}'):
                purchase = demongo(buff)
                buff = ""

                c.execute(
                    '''
                        INSERT INTO purchases
                        (id, mall, date, client)
                        VALUES (?, ?, ?, ?)
                    ''',
                    [
                        purchase['_id'],
                        purchase['mall'],
                        purchase['date'],
                        purchase.get('client'),
                    ]
                )

                # No items
                if not purchase['items']:
                    continue

                for item in purchase['items']:
                    # 0 items (bug?)
                    if item['n_unit'] == 0:
                        continue

                    c.execute(
                        '''
                            INSERT INTO items
                            (purchase_id, description, cost, amount)
                            VALUES(?, ?, ?, ?)
                        ''',
                        [
                          purchase['_id'],
                          item['desc'],
                          str(item['net_am']/item['n_unit']),
                          item['n_unit']
                        ]
                    )

    # Commit to file
    conn.commit()

if __name__ == '__main__':
    main()
