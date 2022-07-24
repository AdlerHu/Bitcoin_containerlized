'''
predict from lastest data, insert into prediction table
'''
from numpy import array
import pandas as pd
from keras.models import load_model
from datetime import datetime
import MySQLdb


def connect_database():
    # Connect the database
    db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='hl4su3ao4', db='bitcoin_historical_price', port=3306, charset='utf8')
    cursor = db.cursor()
    db.autocommit(True)
    return db, cursor


# insert the prediction table
def insert_prediction(cursor, date, prediction):
    sql_str = f'''INSERT INTO `prediction`(`date`, `prediction`) VALUES (\'{date}\', {prediction});'''
    try:
        cursor.execute(sql_str)
    except Exception as err:
        print(f'{date}: {err.args}')


def get_unpredicted_data(db):
    sql_str = '''SELECT h.future, h.bitcoin_price, h.gold_price, h.oil_price 
        FROM `historical_data` as h 
        WHERE ( SELECT COUNT(1) FROM `result` as r WHERE h.future = r.date) = 0;'''
    data_row = pd.read_sql_query(sql_str, db)
    
    return data_row


# predict for all historical data table, use when recreate the prediction table
def prediction(db, cursor, model):

    raw_data = get_unpredicted_data(db=db)

    date_list = list(raw_data['future'])
    bitcoin_list = list(raw_data['bitcoin_price'])
    gold_list = list(raw_data['gold_price'])
    oil_list = list(raw_data['oil_price'])

    for i in range(len(date_list)):
        predict_data_list = [bitcoin_list[i], gold_list[i], oil_list[i]]
        prediction = predict(model=model, predict_data_list=predict_data_list)
        insert_prediction(cursor=cursor, date=date_list[i], prediction=prediction)


# predict from saved model
def predict(model, predict_data_list):
    n_steps = 1
    n_features = 3

    # # demonstrate prediction    
    x_input = array(predict_data_list)
    x_input = x_input.reshape((1, n_steps, n_features))
    yhat = model.predict(x_input, verbose=0)
    
    answer = yhat.flatten().tolist()
    ans = ''.join(str(x) for x in answer)

    return ans


def main():
    db, cursor = connect_database()
    model = load_model('model/7th_days.h5')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    prediction(db=db, cursor=cursor, model=model)

    cursor.close()
    print(f'{now}: Predict Done')
    db.close()


if __name__ == '__main__':
    main()