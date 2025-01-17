from pathlib import Path

import numpy as np
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense
from keras.losses import SparseCategoricalCrossentropy
from keras.optimizers import Adam
from scipy.io import loadmat

BASE_DIR = Path(__file__).parent.parent



# 多类分类

path =  BASE_DIR / '逻辑回归/ex3data1.mat'


data = loadmat(path)



X = data['X']
y = data['y']

print(X.shape, y.shape) #看下维度


# 我们也需要对我们的y标签进行一次one-hot 编码。 
# one-hot 编码将类标签n（k类）转换为长度为k的向量，其中索引n为“hot”（1），而其余为0。 Scikitlearn有一个内置的实用程序，我们可以使用这个


from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse_output=False)
y_onehot = encoder.fit_transform(y)
print(y_onehot.shape)


# 我们要为此练习构建的神经网络具有与我们的实例数据（400 +偏置单元）大小匹配的输入层，25个单位的隐藏层（带有偏置单元的26个），
# 以及一个输出层， 10个单位对应我们的一个one-hot编码类标签

# sigmoid 函数
def sigmoid(z):
    return 1 / (1 + np.exp(-z))


# 前向传播函数
# (400 + 1) -> (25 + 1) -> (10)

def forward_propagate(X, theta1, theta2):
    m = X.shape[0]
    
    a1 = np.insert(X, 0, values=np.ones(m), axis=1)
    z2 = a1 * theta1.T
    a2 = np.insert(sigmoid(z2), 0, values=np.ones(m), axis=1)
    z3 = a2 * theta2.T
    h = sigmoid(z3)
    
    return a1, z2, a2, z3, h


# 代价函数
def cost1(params, input_size, hidden_size, num_labels, X, y, learning_rate):
    m = X.shape[0]  # 5000
    X = np.matrix(X)
    y = np.matrix(y)  # 5000,10
    
    # reshape the parameter array into parameter matrices for each layer
    theta1 = np.matrix(np.reshape(params[:hidden_size * (input_size + 1)], (hidden_size, (input_size + 1))))
    theta2 = np.matrix(np.reshape(params[hidden_size * (input_size + 1):], (num_labels, (hidden_size + 1))))
    
    # run the feed-forward pass
    a1, z2, a2, z3, h = forward_propagate(X, theta1, theta2)
    
    # h 5000 * 10
    # compute the cost
    J = 0
    for i in range(m):
        first_term = np.multiply(-y[i,:], np.log(h[i,:]))
        second_term = np.multiply((1 - y[i,:]), np.log(1 - h[i,:]))
        J += np.sum(first_term - second_term)
    
    J = J / m
    
    return J
# 这个Sigmoid函数我们以前使用过。 前向传播函数计算给定当前参数的每个训练实例的假设。 它的输出形状应该与y的一个one-hot编码相同





# 初始化设置
input_size = 400
hidden_size = 25
num_labels = 10
learning_rate = 1

# 随机初始化完整网络参数大小的参数数组
params = (np.random.random(size=hidden_size * (input_size + 1) + num_labels * (hidden_size + 1)) - 0.5) * 0.25

m = X.shape[0]
X = np.matrix(X)
y = np.matrix(y)

# 将参数数组解开为每个层的参数矩阵
# 25 * 401
theta1 = np.matrix(np.reshape(params[:hidden_size * (input_size + 1)], (hidden_size, (input_size + 1))))

# 10 * 26
theta2 = np.matrix(np.reshape(params[hidden_size * (input_size + 1):], (num_labels, (hidden_size + 1))))

theta1.shape, theta2.shape


a1, z2, a2, z3, h = forward_propagate(X, theta1, theta2)

print(h.shape)

# 代价函数在计算假设矩阵h之后，应用代价函数来计算y和h之间的总误差

_cost1 = cost1(params, input_size, hidden_size, num_labels, X, y_onehot, learning_rate)

print(_cost1)


# 正则 化的代价函数
def cost(params, input_size, hidden_size, num_labels, X, y, learning_rate):
    m = X.shape[0]
    X = np.matrix(X)
    y = np.matrix(y)
    
    # reshape the parameter array into parameter matrices for each layer
    theta1 = np.matrix(np.reshape(params[:hidden_size * (input_size + 1)], (hidden_size, (input_size + 1))))
    theta2 = np.matrix(np.reshape(params[hidden_size * (input_size + 1):], (num_labels, (hidden_size + 1))))
    
    # run the feed-forward pass
    a1, z2, a2, z3, h = forward_propagate(X, theta1, theta2)
    
    # compute the cost
    J = 0
    for i in range(m):
        first_term = np.multiply(-y[i,:], np.log(h[i,:]))
        second_term = np.multiply((1 - y[i,:]), np.log(1 - h[i,:]))
        J += np.sum(first_term - second_term)
    
    J = J / m
    
    # add the cost regularization term
    J += (float(learning_rate) / (2 * m)) * (np.sum(np.power(theta1[:,1:], 2)) + np.sum(np.power(theta2[:,1:], 2)))
    
    return J




_cost2 = cost(params, input_size, hidden_size, num_labels, X, y_onehot, learning_rate)

print(_cost2)


# 接下来是反向传播算法。 反向传播参数更新计算将减少训练数据上的网络误差。 
# 我们需要的第一件事是计算我们之前创建的Sigmoid函数的梯度的函数


def sigmoid_gradient(z):
    return np.multiply(sigmoid(z), (1 - sigmoid(z)))

# 现在我们准备好实施反向传播来计算梯度。 
# 由于反向传播所需的计算是代价函数中所需的计算过程，我们实际上将扩展代价函数以执行反向传播并返回代价和梯度

def backprop(params, input_size, hidden_size, num_labels, X, y, learning_rate):
    m = X.shape[0]
    X = np.matrix(X)
    y = np.matrix(y)
    
    # reshape the parameter array into parameter matrices for each layer
    theta1 = np.matrix(np.reshape(params[:hidden_size * (input_size + 1)], (hidden_size, (input_size + 1))))
    theta2 = np.matrix(np.reshape(params[hidden_size * (input_size + 1):], (num_labels, (hidden_size + 1))))
    
    # run the feed-forward pass
    a1, z2, a2, z3, h = forward_propagate(X, theta1, theta2)
    
    # initializations
    J = 0
    delta1 = np.zeros(theta1.shape)  # (25, 401)
    delta2 = np.zeros(theta2.shape)  # (10, 26)
    
    # compute the cost
    for i in range(m):
        first_term = np.multiply(-y[i,:], np.log(h[i,:]))
        second_term = np.multiply((1 - y[i,:]), np.log(1 - h[i,:]))
        J += np.sum(first_term - second_term)
    
    J = J / m
    
    # add the cost regularization term
    J += (float(learning_rate) / (2 * m)) * (np.sum(np.power(theta1[:,1:], 2)) + np.sum(np.power(theta2[:,1:], 2)))
    
    # perform backpropagation
    for t in range(m):   # 5000
        a1t = a1[t,:]  # (1, 401)   a1 5000*401
        z2t = z2[t,:]  # (1, 25)  za 5000*25
        a2t = a2[t,:]  # (1, 26)   a2 5000*26
        ht = h[t,:]  # (1, 10)   h    5000*10
        yt = y[t,:]  # (1, 10)
        
        d3t = ht - yt  # (1, 10)
        
        z2t = np.insert(z2t, 0, values=np.ones(1))  # (1, 26)
        d2t = np.multiply((theta2.T * d3t.T).T, sigmoid_gradient(z2t))  # (1, 26)
        
        delta1 = delta1 + (d2t[:,1:]).T * a1t
        delta2 = delta2 + d3t.T * a2t
        
    delta1 = delta1 / m
    delta2 = delta2 / m
    
    # 将梯度矩阵分解成单个数组
    grad = np.concatenate((np.ravel(delta1), np.ravel(delta2)))
    
    return J, grad




# 反向传播计算的最难的部分（除了理解为什么我们正在做所有这些计算）是获得正确矩阵维度。 
# 顺便说一下，你容易混淆了A * B与np.multiply（A，B）使用。 基本上前者是矩阵乘法，
# 后者是元素乘法（除非A或B是标量值，在这种情况下没关系）。 无论如何，让我们测试一下，以确保函数返回我们期望的。




# J, grad = backprop(params, input_size, hidden_size, num_labels, X, y_onehot, learning_rate)
# print(J, grad.shape)


# 我们还需要对反向传播函数进行一个修改，即将梯度计算加正则化。 最后的正式版本如下

def backprop(params, input_size, hidden_size, num_labels, X, y, learning_rate):
    m = X.shape[0]
    X = np.matrix(X)
    y = np.matrix(y)
    
    # reshape the parameter array into parameter matrices for each layer
    theta1 = np.matrix(np.reshape(params[:hidden_size * (input_size + 1)], (hidden_size, (input_size + 1))))
    theta2 = np.matrix(np.reshape(params[hidden_size * (input_size + 1):], (num_labels, (hidden_size + 1))))
    
    # run the feed-forward pass
    a1, z2, a2, z3, h = forward_propagate(X, theta1, theta2)
    
    # initializations
    J = 0
    delta1 = np.zeros(theta1.shape)  # (25, 401)
    delta2 = np.zeros(theta2.shape)  # (10, 26)
    
    # compute the cost
    for i in range(m):
        first_term = np.multiply(-y[i,:], np.log(h[i,:]))
        second_term = np.multiply((1 - y[i,:]), np.log(1 - h[i,:]))
        J += np.sum(first_term - second_term)
    
    J = J / m
    
    # add the cost regularization term
    J += (float(learning_rate) / (2 * m)) * (np.sum(np.power(theta1[:,1:], 2)) + np.sum(np.power(theta2[:,1:], 2)))
    
    # perform backpropagation
    for t in range(m):
        a1t = a1[t,:]  # (1, 401)
        z2t = z2[t,:]  # (1, 25)
        a2t = a2[t,:]  # (1, 26)
        ht = h[t,:]  # (1, 10)
        yt = y[t,:]  # (1, 10)
        
        d3t = ht - yt  # (1, 10)
        
        z2t = np.insert(z2t, 0, values=np.ones(1))  # (1, 26)
        d2t = np.multiply((theta2.T * d3t.T).T, sigmoid_gradient(z2t))  # (1, 26)
        
        delta1 = delta1 + (d2t[:,1:]).T * a1t
        delta2 = delta2 + d3t.T * a2t
        
    delta1 = delta1 / m
    delta2 = delta2 / m
    
    # add the gradient regularization term
    delta1[:,1:] = delta1[:,1:] + (theta1[:,1:] * learning_rate) / m
    delta2[:,1:] = delta2[:,1:] + (theta2[:,1:] * learning_rate) / m
    
    # unravel the gradient matrices into a single array
    grad = np.concatenate((np.ravel(delta1), np.ravel(delta2)))
    
    return J, grad




J, grad = backprop(params, input_size, hidden_size, num_labels, X, y_onehot, learning_rate)
print(J, grad.shape)

# 我们终于准备好训练我们的网络，并用它进行预测。 这与以往的具有多类逻辑回归的练习大致相似




from scipy.optimize import minimize

# minimize the objective function
fmin = minimize(fun=backprop, x0=params, args=(input_size, hidden_size, num_labels, X, y_onehot, learning_rate), 
                method='TNC', jac=True)


print(fmin)





# 让我们使用它找到的参数，并通过网络前向传播以获得预测
X = np.matrix(X)
theta1 = np.matrix(np.reshape(fmin.x[:hidden_size * (input_size + 1)], (hidden_size, (input_size + 1))))
theta2 = np.matrix(np.reshape(fmin.x[hidden_size * (input_size + 1):], (num_labels, (hidden_size + 1))))

a1, z2, a2, z3, h = forward_propagate(X, theta1, theta2)
y_pred = np.array(np.argmax(h, axis=1) + 1)
y_pred

