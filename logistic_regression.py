
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from matplotlib.colors import ListedColormap

data = pd.read_csv('train.csv')

print(data.head())

print(data.describe())

data['Age'] = data['Age'].fillna(data['Age'].mean())

X = data.iloc[:, [2, 4, 5]].values
y = data.iloc[:, 1].values

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
label1 = LabelEncoder()
X[:, 1] = label1.fit_transform(X[:, 1])

onehot = OneHotEncoder(categorical_features = [0])
X = onehot.fit_transform(X).toarray()

print(len(X))

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

X_train = X_train.astype(np.float32)
X_test = X_test.astype(np.float32)

y_train = y_train.astype(np.float32)
y_test = y_test.astype(np.float32)

def regressor(features, labels, mode):
  
  m, n = features.shape
  n = tf.cast(n, dtype = tf.int32)
  #features = tf.cast(features, dtype = tf.float32)
  
  w = tf.Variable(tf.random_normal(shape = [n, 1]), dtype = tf.float32)
  b = tf.Variable(tf.random_normal(shape = [1, 1]), dtype = tf.float32)
  
  output = tf.add(tf.matmul(features, w), b)
  
  probability = tf.nn.sigmoid(output)
  
  prediction = tf.round(probability)
  
  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode = mode, predictions = prediction)
  
  cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels = labels, logits = output), name = 'loss_function')
  optimizer = tf.train.GradientDescentOptimizer(0.03)      
  train_op = optimizer.minimize(
      loss = cost,
      global_step = tf.train.get_global_step()
  )
  
  if mode == tf.estimator.ModeKeys.TRAIN:
    return tf.estimator.EstimatorSpec(mode = mode, loss = cost, train_op = train_op)
  
  eval_op = {
      'accuracy': tf.metrics.accuracy(labels = labels, predictions = prediction, name = 'acc')
  }
  
  return tf.estimator.EstimatorSpec(mode = mode, loss = cost, eval_metric_ops = eval_op)

tensor_to_hook = {
    'loss': 'loss_function'
}
tf.logging.set_verbosity(tf.logging.INFO)

tensorhook = tf.train.LoggingTensorHook(
    tensors = tensor_to_hook, every_n_iter = 100
)

classifier = tf.estimator.Estimator(model_fn = regressor)

training_input_fn = tf.estimator.inputs.numpy_input_fn(
    x = X_train,
    y = np.matrix(y_train).T,
    batch_size = 100,
    num_epochs = None,
    shuffle = True
)

eval_input_fn = tf.estimator.inputs.numpy_input_fn(
    x = X_test, 
    y = np.matrix(y_test).T, 
    num_epochs = 1,
    shuffle = False
)

classifier.train(
    input_fn = training_input_fn,
    steps = 1500,
    hooks = [tensorhook]
)

eval_result = classifier.evaluate(input_fn = eval_input_fn)
print('loss is {:5f} accuracy is {:5f}'.format(eval_result['loss'], eval_result['accuracy']))

pr = list(classifier.predict(input_fn = eval_input_fn))

pred = []
for i in pr:
  pred.append(i[0].astype(np.int32))

from sklearn.metrics import accuracy_score
acc = accuracy_score(y_test, pred)
print(acc)
