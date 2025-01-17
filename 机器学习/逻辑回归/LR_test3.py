
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat

# 对于此练习，我们将使用逻辑回归来识别手写数字（0到9）。 我们将扩展我们在练习2中写的逻辑回归的实现，并将其应用于一对一的分类。 
# 让我们开始加载数据集。 它是在MATLAB的本机格式，所以要加载它在Python，我们需要使用一个SciPy工具

BASE_DIR = Path(__file__).parent



# 多类分类

path =  BASE_DIR / 'ex3data1.mat'
data = loadmat(path)

print(data['X'].shape, data['y'].shape)

# 好的，我们已经加载了我们的数据。图像在martix X中表示为400维向量（其中有5,000个）。
#  400维“特征”是原始20 x 20图像中每个像素的灰度强度。类标签在向量y中作为表示图像中数字的数字类。

# 第一个任务是将我们的逻辑回归实现修改为完全向量化（即没有“for”循环）。
# 这是因为向量化代码除了简洁外，还能够利用线性代数优化，并且通常比迭代代码快得多。
# 但是，如果从练习2中看到我们的代价函数已经完全向量化实现了，所以我们可以在这里重复使用相同的实现

# sigmoid 函数
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# 代价函数
def cost(theta, X, y, learningRate):
    theta = np.matrix(theta)
    X = np.matrix(X)
    y = np.matrix(y)
    first = np.multiply(-y, np.log(sigmoid(X * theta.T)))
    second = np.multiply((1 - y), np.log(1 - sigmoid(X * theta.T)))
    reg = (learningRate / (2 * len(X))) * np.sum(np.power(theta[:,1:theta.shape[1]], 2))
    return np.sum(first - second) / len(X) + reg


# 以下是原始代码是使用for循环的梯度函数
def gradient_with_loop(theta, X, y, learningRate):
    theta = np.matrix(theta)
    X = np.matrix(X)
    y = np.matrix(y)
    
    parameters = int(theta.ravel().shape[1])
    grad = np.zeros(parameters)
    
    error = sigmoid(X * theta.T) - y
    
    for i in range(parameters):
        term = np.multiply(error, X[:,i])
        
        if (i == 0):
            grad[i] = np.sum(term) / len(X)
        else:
            grad[i] = (np.sum(term) / len(X)) + ((learningRate / len(X)) * theta[:,i])
    
    return grad


# 向量化的梯度函数
def gradient(theta, X, y, learningRate):
    theta = np.matrix(theta)
    X = np.matrix(X)
    y = np.matrix(y)
    
    parameters = int(theta.ravel().shape[1])
    error = sigmoid(X * theta.T) - y
    
    grad = ((X.T * error) / len(X)).T + ((learningRate / len(X)) * theta)
    
    # 截距梯度没有正则化
    grad[0, 0] = np.sum(np.multiply(error, X[:,0])) / len(X)
    
    return np.array(grad).ravel()


    # 现在我们已经定义了代价函数和梯度函数，现在是构建分类器的时候了。 对于这个任务，我们有10个可能的类，
    # 并且由于逻辑回归只能一次在2个类之间进行分类，我们需要多类分类的策略。 
    # 在本练习中，我们的任务是实现一对一全分类方法，其中具有k个不同类的标签就有k个分类器，
    # 每个分类器在“类别 i”和“不是 i”之间决定。 我们将把分类器训练包含在一个函数中，
    # 该函数计算10个分类器中的每个分类器的最终权重，并将权重返回为k X（n + 1）数组，其中n是参数数量。

from scipy.optimize import minimize


def one_vs_all(X, y, num_labels, learning_rate):
    rows = X.shape[0]
    params = X.shape[1]
    
    # k X (n + 1) array for the parameters of each of the k classifiers
    all_theta = np.zeros((num_labels, params + 1))
    
    # 在截距项的开头插入一列1
    X = np.insert(X, 0, values=np.ones(rows), axis=1)
    
    # 标签以1为索引，而不是以0为索引
    for i in range(1, num_labels + 1):
        theta = np.zeros(params + 1)
        y_i = np.array([1 if label == i else 0 for label in y])
        y_i = np.reshape(y_i, (rows, 1))
        
        # 最小化目标函数
        fmin = minimize(fun=cost, x0=theta, args=(X, y_i, learning_rate), method='TNC', jac=gradient)
        all_theta[i-1,:] = fmin.x
    
    return all_theta


rows = data['X'].shape[0]
params = data['X'].shape[1]

all_theta = np.zeros((10, params + 1))

X = np.insert(data['X'], 0, values=np.ones(rows), axis=1)

theta = np.zeros(params + 1)

print(data['y'].shape)

y_0 = np.array([1 if label == 0 else 0 for label in data['y']])
y_0 = np.reshape(y_0, (rows, 1))


print(rows, params, theta.shape, y_0.shape, all_theta.shape, X.shape)

# 注意，theta是一维数组，因此当它被转换为计算梯度的代码中的矩阵时，它变为（1×401）矩阵。 
# 我们还检查y中的类标签，以确保它们看起来像我们想象的一致
print(np.unique(data['y']))

# 让我们确保我们的训练函数正确运行，并且得到合理的输出

all_theta = one_vs_all(data['X'], data['y'], 10, 1)



# 我们现在准备好最后一步 - 使用训练完毕的分类器预测每个图像的标签。 
# 对于这一步，我们将计算每个类的类概率，对于每个训练样本（使用当然的向量化代码），并将输出类标签为具有最高概率的类

def predict_all(X, all_theta):
    rows = X.shape[0]    # 5000
    params = X.shape[1]   # 400
    num_labels = all_theta.shape[0]   # 10
    
    # same as before, insert ones to match the shape
    X = np.insert(X, 0, values=np.ones(rows), axis=1)    # 5000,401
    
    # convert to matrices
    X = np.matrix(X)
    all_theta = np.matrix(all_theta)
    
    # 计算每个训练实例上每个类的类概率
    h = sigmoid(X * all_theta.T)
    print(h)
    # 以最大概率创建索引数组
    h_argmax = np.argmax(h, axis=1)
    print(h_argmax)
    # 因为我们的数组是零索引的，所以我们需要为真正的标签预测添加1
    h_argmax = h_argmax + 1
    
    return h_argmax


y_pred = predict_all(data['X'], all_theta)
correct = [1 if a == b else 0 for (a, b) in zip(y_pred, data['y'])]
accuracy = (sum(map(int, correct)) / float(len(correct)))
print ('accuracy = {0}%'.format(accuracy * 100))


from keras.losses import BinaryCrossentropy


