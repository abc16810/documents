
import traceback
from pathlib import Path

import numpy as np
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense
from keras.losses import SparseCategoricalCrossentropy
from keras.optimizers import Adam
from keras.regularizers import L2
from scipy.io import loadmat

BASE_DIR = Path(__file__).parent.parent



# 多类分类

path =  BASE_DIR / '逻辑回归/ex3data1.mat'


data = loadmat(path)



X = data['X'][:4000]

y = data['y'][:4000] - 1

print(y)
print(y - 1)

print(X.shape, y.shape)




model = Sequential([
    Dense(units=25, activation='relu'),
    Dense(units=15, activation='relu'),
    Dense(units=10, activation='softmax')
])



# kernel_regularizer 正则化
# 正则化器允许您在优化期间对层参数或层活动应用惩罚。这些惩罚被求和到网络优化的损失函数中
# 0.01 就是 lambda 的值 
# tf 允许为不同的层设置不同的值
# Dense(units=25, activation='relu', kernel_regularizer=L2(0.01))

model.compile(loss=SparseCategoricalCrossentropy(from_logits=False), optimizer=Adam(learning_rate=1e-3))


m = model.fit(X, y, epochs=100)

d = model.predict(data['X'][4000:])

f_x = d



h_argmax = np.argmax(f_x, axis=1)
print(h_argmax)
    # 因为我们的数组是零索引的，所以我们需要为真正的标签预测添加1
h_argmax = h_argmax + 1

print(h_argmax, h_argmax.shape)



correct = [1 if a == b else 0 for (a, b) in zip(h_argmax, data['y'][4000:])]
accuracy = (sum(map(int, correct)) / float(len(correct)))
print ('accuracy = {0}%'.format(accuracy * 100))

