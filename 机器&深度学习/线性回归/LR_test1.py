import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).parent

### 单变量线性回归

path =  BASE_DIR / 'ex1data1.txt'
data = pd.read_csv(path, header=None, names=['Population', 'Profit'])
print(data.head())



# data.plot(kind='scatter', x='Population', y='Profit', figsize=(12,8))
# plt.show()


# 计算代价
def computeCost(X, y, theta):
    inner = np.power(((X * theta.T) - y), 2)
    return np.sum(inner) / (2 * len(X))


# 让我们在训练集中添加一列，以便我们可以使用向量化的解决方案来计算代价和梯度。
data.insert(0, 'Ones', 1)


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



cols = data.shape[1]
X = data.iloc[:,0:cols-1]#X是所有行，去掉最后一列
y = data.iloc[:,cols-1:cols]#X是所有行，最后一列


print(X.head())
print(y.head())

# 代价函数是应该是numpy矩阵，所以我们需要转换X和Y，然后才能使用它们。 我们还需要初始化theta。

X = np.matrix(X.values)
y = np.matrix(y.values)
theta = np.matrix(np.array([0,1.19303364]))


# 计算代价函数 (theta初始值为0).
_cost = computeCost(X, y, theta)

print(_cost)


# 初始化一些附加变量 - 学习速率α和要执行的迭代次数
alpha = 0.01
iters = 1000

# 现在让我们运行梯度下降算法来将我们的参数θ适合于训练集
g, cost = gradientDescent(X, y, theta, alpha, iters)

print(g)

# 最后，我们可以使用我们拟合的参数计算训练模型的代价函数（误差）



_cost = computeCost(X, y, g)

print(_cost)

# 现在我们来绘制线性模型以及数据，直观地看出它的拟合。

x = np.linspace(data.Population.min(), data.Population.max(), 100)
f = g[0, 0] + (g[0, 1] * x)

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(x, f, 'r', label='Prediction')
ax.scatter(data.Population, data.Profit, label='Traning Data')
ax.legend(loc=2)
ax.set_xlabel('Population')
ax.set_ylabel('Profit')
ax.set_title('Predicted Profit vs. Population Size')
plt.show()





# 我们也可以使用scikit-learn的线性回归函数，而不是从头开始实现这些算法。 
# 我们将scikit-learn的线性回归算法应用于第1部分的数据，并看看它的表现
xx = np.array(X)[:, -1:]

yy = np.array(y)


from sklearn import linear_model

# 最小二乘法
model = linear_model.LinearRegression()
m = model.fit(xx, yy)

print(m.coef_, m.intercept_)   # 系数和截距

x = np.array(xx.reshape(xx.shape[0]))
f = model.predict(xx).flatten()

fig, ax = plt.subplots(figsize=(12,8))
ax.plot(x, f, 'r', label='Prediction')
ax.scatter(data.Population, data.Profit, label='Traning Data')
ax.legend(loc=2)
ax.set_xlabel('Population')
ax.set_ylabel('Profit')
ax.set_title('Predicted Profit vs. Population Size')
plt.show()