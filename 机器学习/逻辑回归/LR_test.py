from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).parent

### 逻辑回归

path =  BASE_DIR / 'ex2data1.txt'
data = pd.read_csv(path, header=None, names=['Exam 1', 'Exam 2', 'Admitted'])
print(data.head())

# 让我们创建两个分数的散点图，并使用颜色编码来可视化，如果样本是正的（被接纳）或负的（未被接纳）

positive = data[data['Admitted'].isin([1])]
negative = data[data['Admitted'].isin([0])]

print(positive, negative)


# fig, ax = plt.subplots(figsize=(12,8))
# ax.scatter(positive['Exam 1'], positive['Exam 2'], s=50, c='b', marker='o', label='Admitted')
# ax.scatter(negative['Exam 1'], negative['Exam 2'], s=50, c='r', marker='x', label='Not Admitted')
# ax.legend()
# ax.set_xlabel('Exam 1 Score')
# ax.set_ylabel('Exam 2 Score')
# plt.show()


# 定义假设函数
def sigmoid(z):
    return 1 / (1 + np.exp(-z))


# nums = np.arange(-10, 10, step=1)

# fig, ax = plt.subplots(figsize=(12,8))
# ax.plot(nums, sigmoid(nums), 'r')
# plt.show()


def cost(theta, X, y):
    theta = np.matrix(theta)
    X = np.matrix(X)
    y = np.matrix(y)
    first = np.multiply(-y, np.log(sigmoid(X * theta.T)))
    second = np.multiply((1 - y), np.log(1 - sigmoid(X * theta.T)))
    return np.sum(first - second) / (len(X))


# 加上一列-这使得矩阵乘法运算更容易
data.insert(0, 'Ones', 1)


# set X (training data) and y (target variable)
cols = data.shape[1]
X = data.iloc[:,0:cols-1]
y = data.iloc[:,cols-1:cols]

# convert to numpy arrays and initalize the parameter array theta
X = np.array(X.values)
y = np.array(y.values)
theta = np.zeros(3)

print(X.shape, y.shape, theta)


# 让我们计算初始化参数的代价函数(theta为0)。
_cost = cost(theta, X, y)
print(_cost)


def gradient(theta, X, y):
    theta = np.matrix(theta)
    X = np.matrix(X)
    y = np.matrix(y)
    
    parameters = int(theta.ravel().shape[1])
    grad = np.zeros(parameters)
    
    error = sigmoid(X * theta.T) - y
    
    for i in range(parameters):
        term = np.multiply(error, X[:,i])
        grad[i] = np.sum(term) / len(X)
    
    return grad


res = gradient(theta, X, y)
print(res)


# 现在可以用SciPy's truncated newton（TNC）实现寻找最优参数
import scipy.optimize as opt

result = opt.fmin_tnc(func=cost, x0=theta, fprime=gradient, args=(X, y))
print(result)


print(cost(result[0], X, y))


# 预测
def predict(theta, X):
    probability = sigmoid(X * theta.T)
    return [1 if x >= 0.5 else 0 for x in probability]


theta_min = np.matrix(result[0])
predictions = predict(theta_min, X)
correct = [1 if ((a == 1 and b == 1) or (a == 0 and b == 0)) else 0 for (a, b) in zip(predictions, y)]
accuracy = (sum(map(int, correct)) % len(correct))
print ('accuracy = {0}%'.format(accuracy))
# accuracy = 89%

# 我们的逻辑回归分类器预测正确，如果一个学生被录取或没有录取，达到89%的精确度。
# 不坏！记住，这是训练集的准确性。我们没有保持住了设置或使用交叉验证得到的真实逼近，
# 所以这个数字有可能高于其真实值（这个话题将在以后说明）





