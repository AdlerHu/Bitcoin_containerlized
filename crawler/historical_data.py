'''
Get Historical bitcoin、gold、oil price from Yahoo Finance
'''
import requests
import pandas as pd
from datetime import datetime, timezone
import time
import config as conf
from pytz import utc

# insert bitcoin、gold、oil historical price to each table
def insert_target_table(cursor, raw_data, table):
    date_list = raw_data['Date']
    price_list = raw_data['Close*']

    for i in range(len(date_list) -1):
        date_str = datetime.strptime(date_list[i], '%b %d, %Y').strftime('%Y-%m-%d')
        sql_str = f'INSERT INTO {table} (`date`, `price`) VALUES (\"{date_str}\", {price_list[i]});'

        try:
            cursor.execute(sql_str)
        except Exception as err:
            print(err.args)    


# from yahoo finance api get historical raw data
def crawler(url, cursor, table):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/80.0.3987.132 Safari/537.36'}
    ss = requests.session()
    res = ss.get(url, headers=headers)

    raw_data = pd.read_html(res.text)[0]
    insert_target_table(cursor=cursor, raw_data=raw_data, table=table)


# timestamp format, time zone require UTC
def date_str_to_timpstamp(date_str):
    return str(int(datetime.strptime(date_str, '%Y-%m-%d').astimezone(tz=utc).timestamp()))


def main():
    # data of 3 months at once
    cursor = conf.connect_db()
    start_date_list, end_date_list = conf.get_period()
    now = datetime.now().strftime('%Y-%m-%d %H:%m')

    # 'target-name': ['url-code', 'table-name']
    target_dict = {'Bitcoin':['BTC-USD','bitcoin_historical_data'],
                   'Gold':['GC%3DF','gold_historical_data'],
                   'Oil':['BZ%3DF','oil_historical_data'] 
    }
    
    for key in target_dict.keys():
        code = target_dict[key][0]
        table = target_dict[key][1]

        for i in range(len(start_date_list)):
            start_date_str = date_str_to_timpstamp(start_date_list[i])
            end_date_str = date_str_to_timpstamp(end_date_list[i])

            url = 'https://finance.yahoo.com/quote/' + code + '/history?period1=' + start_date_str \
                    + '&period2=' + end_date_str + '&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'

            crawler(url=url, cursor=cursor, table=table)
            time.sleep(5)

    cursor.close()
    print(f'{now} done')


if __name__ == '__main__':
    main()