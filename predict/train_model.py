# train a model to predict the next 7th day

# multivariate lstm example
from numpy import array
from numpy import hstack
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
import config as conf
import pandas as pd


def train_model(dataset, n_steps):
    # convert into input/output
    X, y = split_sequences(dataset=dataset, n_steps=n_steps)

    # the dataset knows the number of features, e.g. 2
    n_features = X.shape[2]

    # define model
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # fit model
    model.fit(X, y, epochs=200, verbose=0)

    return model, n_features


# generate training dataset from raw data
def prepare_data(raw_data):
    # define input sequence
    bitcoin_in = array(list(raw_data['bitcoin_price']))
    gold_in = array(list(raw_data['gold_price']))
    oil_in = array(list(raw_data['oil_price']))

    # out_seq = array([in_seq1[i]+in_seq2[i] for i in range(len(in_seq1))])
    future_seq = array(list(raw_data['future_price']))

    # convert to [rows, columns] structure
    bitcoin_in = bitcoin_in.reshape((len(bitcoin_in), 1))
    gold_in = gold_in.reshape((len(gold_in), 1))
    oil_in = oil_in.reshape((len(oil_in), 1))
    future_seq = future_seq.reshape((len(future_seq), 1))

    # horizontally stack columns
    dataset = hstack((bitcoin_in, gold_in, oil_in, future_seq))

    return dataset


# generate training raw data
def get_dataset(db, start_date_str, end_date_str):
    sql_str = f'''SELECT h.bitcoin_price, h.gold_price, h.oil_price, h.future_price FROM `historical_data` \
        as h WHERE h.date BETWEEN \'{start_date_str}\' AND \'{end_date_str}\';'''

    raw_data = pd.read_sql_query(sql_str, db)
    return raw_data


# split a multivariate sequence into samples
def split_sequences(dataset, n_steps):
	X, y = list(), list()

	for i in range(len(dataset)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the dataset
		if end_ix > len(dataset):
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = dataset[i:end_ix, :-1], dataset[end_ix-1, -1]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)
 

def main(start_date_str, end_date_str):
    db, cursor = conf.connect_database()
    raw_data = get_dataset(db=db, start_date_str=start_date_str, end_date_str=end_date_str)
    dataset = prepare_data(raw_data=raw_data)

    # choose a number of time steps
    n_steps = 1

    model, n_features = train_model(dataset=dataset, n_steps=n_steps)

    model.save('model/7th_days.h5')

    # demonstrate prediction
    x_input = array([29562.4, 1846.2, 114.03])
    x_input = x_input.reshape((1, n_steps, n_features))
    yhat = model.predict(x_input, verbose=0)
    
    # real price is 29799.1
    print(yhat)


if __name__ == '__main__':
    '''
    start date、end date training dataset period, format: 2015-05-01
    '''
    start_date = '2015-10-01'
    end_date = '2022-05-31'
    main(start_date_str=start_date, end_date_str=end_date)