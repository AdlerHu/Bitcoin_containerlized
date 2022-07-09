'''
insert verifiable prediction to result table
'''
from datetime import datetime
import MySQLdb


def connect_database():
    # Connect the database
    db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='hl4su3ao4', db='bitcoin_historical_price', port=3306, charset='utf8')
    cursor = db.cursor()
    db.autocommit(True)
    return db, cursor

# insert verifiable prediction to result table
def insert_result_table(cursor):
    sql_str = '''INSERT INTO `result` (`date`, `prediction`, `real`)
                SELECT 	x.date, p.prediction, x.bitcoin_price
                FROM `prediction` as p
                JOIN 
                (SELECT h.date, h.bitcoin_price 
                FROM `historical_data` as h  
                WHERE ( SELECT COUNT(1) FROM `result` as r WHERE h.date = r.date) = 0) as x
                ON p.date = x.date;'''
    try:
        cursor.execute(sql_str)
    except Exception as err:
        print(err.args)


def main():
    db, cursor = connect_database()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    insert_result_table(cursor=cursor)

    print(f'{now}: Insert Result Done')
    cursor.close()
    db.close()


if __name__ == '__main__':
    main()