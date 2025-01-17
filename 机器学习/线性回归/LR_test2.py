from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 多变量线性回归

BASE_DIR = Path(__file__).parent


path =  BASE_DIR / 'ex1data2.txt'
data2 = pd.read_csv(path, header=None, names=['Size', 'Bedrooms', 'Price'])
print(data2.head())

# 对于此任务，我们添加了另一个预处理步骤 - 特征归一化。 这个对于pandas来说很简单
data2 = (data2 - data2.mean()) / data2.std()
print(data2.head())

# 用sklearn类似如下
# from sklearn import preprocessing
# from sklearn import preprocessing
# X_scaled = preprocessing.scale(data2)
# print(X_scaled)


# 计算代价
def computeCost(X, y, theta):
    inner = np.power(((X * theta.T) - y), 2)
    return np.sum(inner) / (2 * len(X))



# 批量梯度下降
def gradientDescent(X, y, theta, alpha, iters):
    temp = np.matrix(np.zeros(theta.shape))
    parameters = int(theta.ravel().shape[1])
    cost = np.zeros(iters)
    
    for i in range(iters):
        error = (X * theta.T) - y
        
        for j in range(parameters):
            term = np.multiply(error, X[:,j])
            temp[0,j] = theta[0,j] - ((alpha / len(X)) * np.sum(term))
            
        theta = temp
        cost[i] = computeCost(X, y, theta)
        
    return theta, cost


# 初始化一些附加变量 - 学习速率α和要执行的迭代次数
alpha = 0.01
iters = 1000

# add ones column
data2.insert(0, 'Ones', 1)

# set X (training data) and y (target variable)
cols = data2.shape[1]
X2 = data2.iloc[:,0:cols-1]
y2 = data2.iloc[:,cols-1:cols]


# convert to matrices and initialize theta
X2 = np.matrix(X2.values)
y2 = np.matrix(y2.values)
theta2 = np.matrix(np.array([0,0,0]))

# perform linear regression on the data set
g2, cost2 = gradientDescent(X2, y2, theta2, alpha, iters)

# print(g2)
# [[-1.10898288e-16  8.78503652e-01 -4.69166570e-02]]
# get the cost (error) of the model
_cost = computeCost(X2, y2, g2)


# 我们也可以快速查看这一个的训练进程， 检查梯度是否收敛
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(np.arange(iters), cost2, 'r')
ax.set_xlabel('Iterations')
ax.set_ylabel('Cost')
ax.set_title('Error vs. Training Epoch')
plt.show()


# 使用scikit-learn的线性回归函数
from sklearn import linear_model

model = linear_model.LinearRegression()

X2 = data2.iloc[:,0:cols-1]
y2 = data2.iloc[:,cols-1:cols]
m = model.fit(X2, y2)


print(m.coef_, m.intercept_)   # 系数和截距

# [[ 0.          0.88476599 -0.05317882]] [-1.15685754e-16]

# 正规方程
def normalEqn(X, y):
    theta = np.linalg.inv(X.T@X)@X.T@y#X.T@X等价于X.T.dot(X)
    return theta



final_theta2=normalEqn(X2, y2) #感觉和批量梯度下降的theta的值有点差距
print(final_theta2)
# 0 -1.075529e-16
# 1  8.847660e-01
# 2 -5.317882e-02

# 从输出 可以看出scikit-learn 使用的就是正规方程


