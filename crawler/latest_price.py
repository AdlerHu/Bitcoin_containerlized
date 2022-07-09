'''
Get lastest bitcoin、gold、oil price from Yahoo Finance
'''
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import config as conf
from pytz import utc


# insert bitcoin、gold、oil historical price to each table
def insert_target_table(raw_data, cursor, table):
    now = datetime.now().strftime('%Y-%m-%d %H:%m')
    date_list = raw_data['Date']
    price_list = raw_data['Close*']

    for i in range(len(date_list) -1):

        date_str = datetime.strptime(date_list[i], '%b %d, %Y').strftime('%Y-%m-%d')
        sql_str = f'INSERT INTO {table} (`date`, `price`) VALUES (\"{date_str}\", {price_list[i]});'

        try:
            cursor.execute(sql_str)
        except Exception as err:
            print(f'{now}: {err.args}')


# from yahoo finance api get lastest raw data
def crawler(url, cursor, table):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/80.0.3987.132 Safari/537.36'}
    ss = requests.session()
    res = ss.get(url, headers=headers)
    raw_data = pd.read_html(res.text)[0]
    insert_target_table(raw_data=raw_data, cursor=cursor, table=table)


# get the start date & end date
def get_date(cursor, table):
    sql_str = f'SELECT `date` FROM {table} ORDER BY `date` DESC LIMIT 1;'
    cursor.execute(sql_str)
    data_row = cursor.fetchall()

    # start date shoud be the last date + 1 day
    new_date = datetime.strptime(data_row[0][0], "%Y-%m-%d") + timedelta(days=1)
    new_date_str = datetime.strftime(new_date, '%Y-%m-%d')
    today_str = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')

    return date_str_to_timpstamp(new_date_str), date_str_to_timpstamp(today_str)

 
# timestamp format, time zone require UTC
def date_str_to_timpstamp(date_str):
    return str(int(datetime.strptime(date_str, '%Y-%m-%d').astimezone(tz=utc).timestamp()))


def main():
    cursor = conf.connect_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%m')

    # 'target-name': ['url-code', 'table-name']
    target_dict = {'Bitcoin':['BTC-USD','bitcoin_historical_data'],
                   'Gold':['GC%3DF','gold_historical_data'],
                   'Oil':['BZ%3DF','oil_historical_data'] 
    }

    for key in target_dict.keys():
        code = target_dict[key][0]
        table = target_dict[key][1]

        start, end = get_date(cursor=cursor, table=table)

        url = 'https://finance.yahoo.com/quote/' + code + '/history?period1=' + start \
                    + '&period2=' + end + '&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
        crawler(url=url, cursor=cursor, table=table)
    
    cursor.close()
    print(f'{now}: Collection Done')


if __name__ == '__main__':
    main()
