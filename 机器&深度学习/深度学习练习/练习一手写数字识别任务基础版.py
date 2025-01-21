# 任务输入：一系列手写数字图片，其中每张图片都是28x28的像素矩阵
# 任务输出：经过了大小归一化和居中处理，输出对应的0~9的数字标签
# 50000个训练样本，10000个测试样本
# https://aistudio.baidu.com/projectdetail/8772620

#######
# MNIST数据集是从NIST的Special Database 3（SD-3）和Special Database 1（SD-1）构建而来。Yann LeCun等人从SD-1和SD-3中各取一半数据作为MNIST训练集和测试集，其中训练集来自250位不同的标注员，且训练集和测试集的标注员完全不同。
# MNIST数据集的发布，吸引了大量科学家训练模型。1998年，LeCun分别用单层线性分类器、多层感知器（Multilayer Perceptron, MLP）和多层卷积神经网络LeNet进行实验，使得测试集的误差不断下降（从12%下降到0.7%）。在研究过程中，LeCun提出了卷积神经网络（Convolutional Neural Network，CNN），大幅度地提高了手写字符的识别能力，也因此成为了深度学习领域的奠基人之一。
# 如今在深度学习领域，卷积神经网络占据了至关重要的地位，从最早LeCun提出的简单LeNet，到如今ImageNet大赛上的优胜模型VGGNet、GoogLeNet、ResNet等，人们在图像分类领域，利用卷积神经网络得到了一系列惊人的结果。
# 手写数字识别的模型是深度学习中相对简单的模型，非常适用初学者。正如学习编程时，我们输入的第一个程序是打印“Hello World！”一样。 在飞桨的入门教程中，我们选取了手写数字识别模型作为启蒙教材，以便更好的帮助读者快速掌握飞桨平台的使用。
#######

####
# python 3.8.10
# paddle 2.6.0 
####


import os

import matplotlib.pyplot as plt
import numpy as np
import paddle
import paddle.nn.functional as F
from paddle.nn import Linear

# # 设置数据读取器，API自动读取MNIST数据训练集
# train_dataset = paddle.vision.datasets.MNIST(mode='train') # 60000


# # 打印第一个数据及标签
# train_data_0 = np.array(train_dataset[0][0])
# train_label_0 = np.array(train_dataset[0][1])

# import matplotlib.pyplot as plt

# plt.figure("Image") # 图像窗口名称
# plt.figure(figsize=(2,2))
# plt.imshow(train_data_0, cmap=plt.cm.binary)
# plt.axis('on') # 关掉坐标轴为 off
# plt.title('image') # 图像题目
# plt.show()

# print("图像数据形状和对应数据为:", train_data_0.shape)
# print("图像标签形状和对应数据为:", train_label_0.shape, train_label_0)
# print("\n打印第一个batch的第一个图像，对应标签数字为{}".format(train_label_0))

# 确保从paddle.vision.datasets.MNIST中加载的图像数据是np.ndarray类型
paddle.vision.set_image_backend('cv2')

#### 模型设计
# 在房价预测深度学习任务中，我们使用了单层且没有非线性变换的模型，取得了理想的预测效果。在手写数字识别中，我们依然使用这个模型预测输入的图形数字值。
# 其中，模型的输入为784维（28×2828\times 2828×28）数据，输出为1维数据。
# 输入像素的位置排布信息对理解图像内容非常重要（如将原始尺寸为28×2828\times 2828×28图像的像素按照7×1127\times 1127×112的尺寸排布，那么其中的数字将不可识别），
# 因此网络的输入设计为28×2828\times 2828×28的尺寸，而不是1×7841\times 7841×784，以便于模型能够正确处理像素之间的空间信息。

# 定义mnist数据识别网络结构，同房价预测网络
class MNIST(paddle.nn.Layer):
    def __init__(self):
        super(MNIST, self).__init__()
        
        # 定义一层全连接层，输出维度是1
        self.fc = paddle.nn.Linear(in_features=784, out_features=1)
        
    # 定义网络结构的前向计算过程
    def forward(self, inputs):
        outputs = self.fc(inputs)
        return outputs

#### 训练配置
# 训练配置需要先生成模型实例（设为“训练”状态），再设置优化算法和学习率（使用随机梯度下降，学习率设置为0.001），实现方法如下所示

# 声明网络结构
model = MNIST()

# 图像归一化函数，将数据范围为[0, 255]的图像归一化到[0, 1]
def norm_img(img):
    # 验证传入数据格式是否正确，img的shape为[batch_size, 28, 28]
    assert len(img.shape) == 3
    batch_size, img_h, img_w = img.shape[0], img.shape[1], img.shape[2]
    # 归一化图像数据
    img = img / 255
    # 将图像形式reshape为[batch_size, 784]
    img = paddle.reshape(img, [batch_size, img_h*img_w])
    
    return img

def train(model):
    # 启动训练模式
    model.train()
    # 加载训练集 batch_size 设为 16
    train_loader = paddle.io.DataLoader(paddle.vision.datasets.MNIST(mode='train'), 
                                        batch_size=16, 
                                        shuffle=True)
    # 定义优化器，使用随机梯度下降SGD优化器，学习率设置为0.001
    opt = paddle.optimizer.SGD(learning_rate=0.001, parameters=model.parameters())

    EPOCH_NUM = 10
    loss_list = []
    for epoch in range(EPOCH_NUM):
        for batch_id, data in enumerate(train_loader()):
            images = norm_img(data[0]).astype('float32')
            labels = data[1].astype('float32')
            #前向计算的过程
            predicts = model(images)
            # 计算损失
            loss = F.square_error_cost(predicts, labels)
            
            avg_loss = paddle.mean(loss)

            #每训练了1000批次的数据，打印下当前Loss的情况
            if batch_id % 1000 == 0:
                loss = avg_loss.numpy()
                loss_list.append(loss)
                print("epoch_id: {}, batch_id: {}, loss is: {}".format(epoch, batch_id, loss))
            
            #后向传播，更新参数的过程
            avg_loss.backward()
            opt.step()
            opt.clear_grad()

    return loss_list         



def plot(loss_list):
    plt.figure(figsize=(10,5))
    
    freqs = [i for i in range(len(loss_list))]
    # 绘制训练损失变化曲线
    plt.plot(freqs, loss_list, color='#e4007f', label="Train loss")
    
    # 绘制坐标轴和图例
    plt.ylabel("loss", fontsize='large')
    plt.xlabel("freq", fontsize='large')
    plt.legend(loc='upper right', fontsize='x-large')
    
    plt.show()

# loss_list = train(model)
# paddle.save(model.state_dict(), './mnist.pdparams')
# plot(loss_list)


#### 模型测试
from PIL import Image


# 读取一张本地的样例图片，转变成模型输入的格式
def load_image(img_path):
    # 从img_path中读取图像，并转为灰度图
    im = Image.open(img_path).convert('L')
    # print(np.array(im))
    im = im.resize((28, 28), 4)
    im = np.array(im).reshape(1, -1).astype(np.float32)
    # 图像归一化，保持和数据集的数据范围一致
    im = 1 - im / 255
    return im

# 定义预测过程
model = MNIST()
params_file_path = 'mnist.pdparams'
img_path = './tests/imgs/example_6.jpg'
# 加载模型参数
param_dict = paddle.load(params_file_path)
model.load_dict(param_dict)
# 灌入数据
model.eval()
tensor_img = load_image(img_path)
result = model(paddle.to_tensor(tensor_img))
print('result',result)
#  预测输出取整，即为预测的数字，打印结果
print("本次预测的数字是", result.numpy().astype('int32'))

#### 从打印结果来看，
# 模型预测出的数字是与实际输出的图片的数字不一致。这里只是验证了一个样本的情况，
# 如果我们尝试更多的样本，可发现许多数字图片识别结果是错误的。因此完全复用房价预测的实验并不适用于手写数字识别任务！
# 接下来我们会对手写数字识别实验模型进行逐一改进，直到获得令人满意的结果。

