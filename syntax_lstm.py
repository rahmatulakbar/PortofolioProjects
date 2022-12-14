# -*- coding: utf-8 -*-
"""syntax_LSTM

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xPO84VAecUBAM-QT3yif4AVTE472IxD1
"""

import pandas as pd
import numpy as np
from math import sqrt
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from numpy import array
from keras.preprocessing.sequence import TimeseriesGenerator
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_percentage_error

# input data
dataset = read_csv('/content/drive/MyDrive/data_temperatur.csv',  parse_dates={'datetime':[0]}, index_col=0)

dataset.head()

dataset.columns = ['Tavg', 'RH_avg','ss', 'ff_x','ddd_x','ff_avg','Tn','Tx']
dataset.index.name = 'datetime'
# mengganti missing value dengan nilai rata-rata
mean_Tavg=round(dataset['Tavg'].mean())
mean_RH=round(dataset['RH_avg'].mean())
mean_ss=round(dataset['ss'].mean())
mean_ff=round(dataset['ff_avg'].mean())
mean_ffx=round(dataset['ff_x'].mean())
mean_Tn=round(dataset['Tn'].mean())
mean_Tx=round(dataset['Tx'].mean())
mean_ddx=round(dataset['ddd_x'].mean())

dataset['Tavg'].fillna(mean_Tavg, inplace=True)
dataset['RH_avg'].fillna(mean_RH, inplace=True)
dataset['ss'].fillna(mean_ss, inplace=True)
dataset['ff_avg'].fillna(mean_ff, inplace=True)
dataset['ff_x'].fillna(mean_ffx, inplace=True)
dataset['Tn'].fillna(mean_Tn, inplace=True)
dataset['Tx'].fillna(mean_Tx, inplace=True)
dataset['ddd_x'].fillna(mean_ddx, inplace=True)

# save to file
dataset.to_csv('Tavg.csv')

#plot variabel
from pandas import read_csv
from matplotlib import pyplot
# load dataset
dataset = read_csv('Tavg.csv', header=0, index_col=0)
values = dataset.values
# specify columns to plot
groups = [0, 1, 2, 3,4,5,6,7,]
i = 1
# plot each column
pyplot.figure()
for group in groups:
	pyplot.subplot(len(groups),1, i)
	pyplot.plot(values[:, group])
	pyplot.title(dataset.columns[group], y=0.5, loc='right')
	i += 1
pyplot.show()

# convert series to supervised learning
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg
 
# load dataset
dataset = read_csv('Tavg.csv', header=0, index_col=0)
values = dataset.values
# merubah tipe data menjadi float
values = values.astype('float32')
# normalisasi data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
# frame as supervised learning
reframed = series_to_supervised(scaled, 14, 1)

reframed.shape

reframed.head()

reframed.drop(reframed.columns[[113,114,115,116,117,118,119]], axis=1, inplace=True)
print(reframed.head())

# pembagian data latih dan data test
values = reframed.values
train = values[:867, :]
test = values[867:, :]
# split into input and outputs
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]

# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

# konfigurasi model
from tensorflow import keras
import tensorflow as tf
window_size=1
def create_model(LSTM_unit=64):
    # create model
    model = Sequential()
    model.add(LSTM(units=LSTM_unit, input_shape=(window_size, 112)))
    model.add(Dense(16))
    model.add(Dense(1))
    # Compile model
    opt = tf.keras.optimizers.SGD(learning_rate=0.01)
    model.compile(loss='mse', optimizer= opt, metrics=['mae'])
    return model

from tensorflow.keras.layers import Dense, Dropout, LSTM
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from keras.wrappers.scikit_learn import KerasRegressor
from keras.callbacks import EarlyStopping

# Early Stopping
es = EarlyStopping(monitor = 'val_loss', mode = "min", patience = 5, verbose = 0)

# create model
model = KerasRegressor(build_fn=create_model, epochs=50, validation_split=0.1, callbacks=[es], batch_size=32,  verbose=1,shuffle=False)

# parameter  grid search 
LSTM_unit = [32]
epochs=[50]
batch_size=[32]
param_grid = dict(LSTM_unit=LSTM_unit,epochs=epochs,batch_size=batch_size)

cv=TimeSeriesSplit(n_splits=2)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1, cv=cv)

grid_result = grid.fit(train_X, train_y)

# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))
    
# Mengambil model terbaik
best_model = grid_result.best_estimator_.model

history = best_model.history

# grafik loss function MSE
import matplotlib.pyplot as plt

plt.plot(history.history['loss'], label='Training loss')
plt.plot(history.history['val_loss'], label='Validation loss')
plt.title('loss function MSE')
plt.ylabel('MSE')
plt.xlabel('Epoch')
plt.legend()

# grafik metric MAE

plt.plot(history.history['mae'], label='Training MAE')
plt.plot(history.history['val_mae'], label='Validation MAE')
plt.title('metric MAE')
plt.ylabel('MAE')
plt.xlabel('Epoch')
plt.legend()

yhat=best_model.predict(test_X)
yhat.shape

test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))

inv_yhat = concatenate((yhat, test_X[:, 105:]), axis=1)
# Prediksi data test
predict_test = scaler.inverse_transform(inv_yhat)
# invert scaling for forecast
predict_test = predict_test[:,0]

# invert scaling for actual
test_y = test_y.reshape((len(test_y), 1))
inv_y = concatenate((test_y, test_X[:, 105:]), axis=1)
true_test = scaler.inverse_transform(inv_y)
true_test = true_test[:,0]

#menghitung nilai MAPE
mean_absolute_percentage_error(true_test,predict_test)

# RMSE
rmse = sqrt(mean_squared_error(true_test, predict_test))
print('test RMSE: %.3f' % rmse)

plt.plot(true_test[:],label='Data Testing')
plt.plot(predict_test[:],label='Prediksi')
plt.legend()