# -*- coding: utf-8 -*-
"""Credit_Card _Fraud_Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14Ga2Qa8eXvmyez3AC7TA_9FwODSTa4wG
"""

# Load the Drive helper and mount
from google.colab import drive

# This will prompt for authorization.
drive.mount('/content/drive')

# After executing the cell above, Drive
# files will be present in "/content/drive/My Drive".
!ls "/content/drive/My Drive/ANN"

#Data base description 
#https://www.kaggle.com/mlg-ulb/creditcardfraud/home

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 19:20:56 2018

@author: Sanjeev Jha
"""
#Importing the library

import pandas as pd
import numpy as np
import tensorflow as tf
import time

##################---------------EDA-----------######################
#IMPORT AND STORE THE DATA SET

credit_card_data=pd.read_csv("/content/drive/My Drive/ANN/creditcard.csv")
#with open("/content/drive/My Drive/ANN/creditcard.csv") as f:
 #   credit_card_data = f.read()

##########-------------------SPLITTING DATA INTO 2 TUPPLE OF TRAING ANG AND TEST SET(DATA PREPROCESSING) -------------------######

#1. Shuffle and randomizethe data to remove the baise 
shuffled_data=credit_card_data.sample(frac=1)


#2. One-hot encoding for change Class columns into class_0([1,0] for legit data) and class_1([0,1] for fraudlent data)
one_hot_data=pd.get_dummies(shuffled_data, columns=["Class"])

#3 . Normalize the data by changeing all the value in between zero and one 
normalized_data=(one_hot_data - one_hot_data.min())/(one_hot_data.max() - one_hot_data.min())

#4. Splitting up the data into data frmae X(Input)/y(target) columns V1 through V28 in df_X and columns Class_0 and Class_1 in df_y
df_X=normalized_data.drop(["Class_0", "Class_1"], axis=1)
df_y=normalized_data[["Class_0", "Class_1"]]

#5. Convert data frame into numpy array format (float 32)
arr_X, arr_y= np.asarray(df_X.values, dtype="float32"), np.asarray(df_y.values, dtype="float32")

#5. Allocate first 80% shuffle data in training tupple and next 20 % data into test tupple
train_size=int(0.8 * len(arr_X))
(raw_X_train, raw_y_train) = (arr_X[:train_size], arr_y[:train_size])
(raw_X_test, raw_y_test)=(arr_X[train_size:], arr_y[train_size:]) 

# 6. We have to much baise in our target data so we need to remove the basie by multiplaying with weight 
count_legit, count_fraud= np.unique(credit_card_data['Class'], return_counts=True)[1]

fraud_ratio=float(count_fraud/(count_legit + count_fraud)) 
weighting = 1/fraud_ratio
raw_y_train[:, 1]= raw_y_train[:, 1] * weighting 

# 7. We have 30 cells for input and 2 cells for output 
input_dimesions=arr_X.shape[1]
ouput_dimensions=arr_y.shape[1]

#8. Number of cells in 2 hidden layers
num_layers_1_cells=100
num_layers_2_cells=150

#We will use these placeholder as input to use at when it come time to train it at run time
X_train_node=tf.placeholder(tf.float32, [None, input_dimesions], name="X_train")
y_train_node=tf.placeholder(tf.float32, [None, ouput_dimensions], name="y_train")

# we will use these input at test tim e
X_test_node=tf.constant(raw_X_test, name="X_test")
y_test_node=tf.constant(raw_y_test, name="y_test")

#First layers of weight and baises
weight_1_node=tf.Variable(tf.zeros([input_dimesions,num_layers_1_cells]), name="weight_1") 
biases_1_node=tf.Variable(tf.zeros([num_layers_1_cells]), name="biases_1") 

#Second layers of weight and baises
weight_2_node=tf.Variable(tf.zeros([num_layers_1_cells, num_layers_2_cells]), name="weight_2") 
biases_2_node=tf.Variable(tf.zeros([num_layers_2_cells]), name="biases_2") 

#Output layers of weight and baises
weight_3_node=tf.Variable(tf.zeros([num_layers_2_cells, ouput_dimensions]), name="weight_3") 
biases_3_node=tf.Variable(tf.zeros([ouput_dimensions]), name="biases_3") 

#Function to run the input from three layers(2 hidden layers, one output layers)

def network(input_tensor):
    #if you will draw the graph between target and input then you can see Sigmoid will fit 
    layer1=tf.nn.sigmoid(tf.add(tf.matmul(input_tensor, weight_1_node), biases_1_node))
    #Droput will prevenyt model to become lazzy and over confident
    layer2=tf.nn.dropout(tf.nn.sigmoid(tf.add(tf.matmul(layer1, weight_2_node),biases_2_node)), 0.85) 
    #Softmax work very well with with one hot encoding and multiple output
    layer3=tf.nn.softmax(tf.add(tf.matmul(layer2, weight_3_node), biases_3_node))
    return layer3

# Used to predict what result has been given traing and testing data, just fir reminder x_TRAIN_nODE IS PLACE HOLDER NAD WE WILL ENTER THE RESULTS AT TRAING TIMER
y_train_predection = network(X_train_node)
y_test_predection = network(X_test_node)

#Cross entropy loss function mesure difference between actula output and predicted output 
cross_entropy=tf.losses.softmax_cross_entropy(y_train_node, y_train_predection)

#Adamn Optimizer(Momentum and RMSpROP) funcion will try to minimize the cross entropy loss function BUT IT WILL CHNGE THE LERNING RATE VALUE OF ALL THREE LAYERS BY 0.005

optimizer=tf.train.AdamOptimizer(0.005).minimize(cross_entropy)

#Functions to cal culate accuracy of actual results and predicted results 

def calculate_accuracy(actual, predicted):
    actual = np.argmax(actual, 1)
    predicted = np.argmax(predicted, 1) 
    return (100*np.sum(np.equal(predicted, actual))/predicted.shape[0])
    

#Train the model 
num_epochs=100

with tf.Session() as session:
    tf.global_variables_initializer().run()
    for epoch in range(num_epochs):
        start_time=time.time()
        _, cross_entroppy_score= session.run([optimizer, cross_entropy], 
                                             feed_dict={X_train_node: raw_X_train, y_train_node: raw_y_train})
        if epoch % 10 == 0:
            timer=time.time() - start_time
            print('Epoch: {}'.format(epoch), 'Current loss:{0:.4f}'.format(cross_entroppy_score), 'Ellasped Time: {0:.2f} seconds'.format(timer))
            final_y_test = y_test_node.eval()
            final_y_test_predection = y_test_predection.eval()
            final_accurecy = calculate_accuracy(final_y_test, final_y_test_predection)
            #print the accuracy on over all data sets 
            print('Current Accuracy: {0:.2f}%'.format(final_accurecy))
    final_y_test = y_test_node.eval()
    final_y_test_predection = y_test_predection.eval()
    final_accurecy = calculate_accuracy(final_y_test, final_y_test_predection)
    #print the accuracy on over all data sets 
    print('Final Accuracy: {0:.2f}%'.format(final_accurecy))
            
#Prediction specific to fraud 

final_fraud_y_test= final_y_test[final_y_test[:, 1] == 1]
final_fraud_y_test_prediction= final_y_test_predection[final_y_test[:, 1] == 1]
final_fraud_accuracy=calculate_accuracy(final_fraud_y_test, final_fraud_y_test)           
print('Final fraud specific  Accuracy: {0:.2f}%'.format(final_fraud_accuracy))