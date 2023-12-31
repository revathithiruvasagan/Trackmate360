import psycopg2

def connection():
    return psycopg2.connect(
    dbname='test',
    user='postgres',
    password='postgres',
    host='10.11.155.109'
    )

# import psycopg2

# def connection():
#     return psycopg2.connect(
#     dbname='test',
#     user='postgres',
#     password='postgres',
#     host='10.11.155.109'
#     )

import psycopg2

def connection():
    return psycopg2.connect(
    dbname='trackmate',
    user='trackmate',
    password='LuMB2jRBLleXqpmyD4Yv7ircnKNYzoXm',
    host='dpg-cm1ejjmn7f5s73e849k0-a.singapore-postgres.render.com'
    )