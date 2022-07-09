from datetime import datetime
import pandas as pd
import MySQLdb


def connect_db():
    # Connect the database
    db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='hl4su3ao4', db='bitcoin_historical_price', port=3306, charset='utf8')
    cursor = db.cursor()
    db.autocommit(True)
    return db, cursor


# update bitcoin、gold、oil historical price to historical data table
def update_historical_table(cursor, date_list):

    for date in date_list:
        now = datetime.utcnow().strftime('%Y-%m-%d')
        sql_str = f'''UPDATE `historical_data` as h
            SET 
            h.bitcoin_price = (
                SELECT 	price
                FROM	`bitcoin_historical_data`
                WHERE	date <= h.date
                ORDER BY date DESC LIMIT 1
            ), 
            h.gold_price = (
                SELECT 	price
                FROM	`gold_historical_data`
                WHERE	date <= h.date
                ORDER BY date DESC LIMIT 1
            ), 
            h.oil_price = (
                SELECT 	price
                FROM	`oil_historical_data`
                WHERE	date <= h.date
                ORDER BY date DESC LIMIT 1
            )WHERE h.date = \'{date}\';'''
        try:
            cursor.execute(sql_str)
        except Exception as err:
            print(f'{now}: {err.args}')


# from bitcoin table get the dates havn't been insert into historical table
def get_new_date(db):
    sql_str = '''SELECT b.date FROM `bitcoin_historical_data` as b WHERE ( 
        SELECT COUNT(1) FROM `historical_data` as h WHERE b.date = h.date) = 0;'''
    data_row = pd.read_sql_query(sql_str, db)

    return list(data_row['date'])


# insert lastest date to historical data table
def update_historical_data(db, cursor):
    date_list = get_new_date(db=db)
    for date in date_list:
        sql_str = f'''INSERT INTO `historical_data` (`date`) VALUES (\'{date}\');'''
        try:
            cursor.execute(sql_str)
        except Exception as err:
            print(f'{date}: {err.args}')
    update_historical_table(cursor=cursor, date_list=date_list)


def main():
    db, cursor = connect_db()
    update_historical_data(db=db, cursor=cursor)
    now = datetime.utcnow().strftime('%Y-%m-%d %H-%M')

    cursor.close()
    print(f'{now}: Update Done')
    db.close()


if __name__ == '__main__':
    main()
