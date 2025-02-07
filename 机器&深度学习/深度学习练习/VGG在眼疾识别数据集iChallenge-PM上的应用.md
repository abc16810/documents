iChallenge-PM是百度大脑和中山大学中山眼科中心联合举办的iChallenge比赛中，提供的关于病理性近视（Pathologic Myopia，PM）的医疗类数据集，包含1200个受试者的眼底视网膜图片，训练、验证和测试数据集各400张。下面我们详细介绍Vgg在iChallenge-PM上的训练过程。


```python
# 导入需要的包
import os
import random

import cv2
import numpy as np
import paddle
## 组网
import paddle.nn.functional as F
from paddle.nn import Conv2D, Dropout, Linear, MaxPool2D
from paddle.vision.datasets import MNIST
from paddle.vision.transforms import ToTensor

EPOCH_NUM = 10


# 定义vgg网络
class VGG(paddle.nn.Layer):
    def __init__(self, num_classes=1):
        super(VGG, self).__init__()

        in_channels = [3, 64, 128, 256, 512, 512]
         # 定义第一个block，包含两个卷积
        self.conv1_1 = Conv2D(in_channels=in_channels[0], out_channels=in_channels[1], kernel_size=3, padding=1, stride=1)
        self.conv1_2 = Conv2D(in_channels=in_channels[1], out_channels=in_channels[1], kernel_size=3, padding=1, stride=1)

        # 定义第二个block，包含两个卷积
        self.conv2_1 = Conv2D(in_channels=in_channels[1], out_channels=in_channels[2], kernel_size=3, padding=1, stride=1)
        self.conv2_2 = Conv2D(in_channels=in_channels[2], out_channels=in_channels[2], kernel_size=3, padding=1, stride=1)

        # 定义第三个block，包含三个卷积
        self.conv3_1 = Conv2D(in_channels=in_channels[2], out_channels=in_channels[3], kernel_size=3, padding=1, stride=1)
        self.conv3_2 = Conv2D(in_channels=in_channels[3], out_channels=in_channels[3], kernel_size=3, padding=1, stride=1)
        self.conv3_3 = Conv2D(in_channels=in_channels[3], out_channels=in_channels[3], kernel_size=3, padding=1, stride=1)

        # 定义第四个block，包含三个卷积
        self.conv4_1 = Conv2D(in_channels=in_channels[3], out_channels=in_channels[4], kernel_size=3, padding=1, stride=1)
        self.conv4_2 = Conv2D(in_channels=in_channels[4], out_channels=in_channels[4], kernel_size=3, padding=1, stride=1)
        self.conv4_3 = Conv2D(in_channels=in_channels[4], out_channels=in_channels[4], kernel_size=3, padding=1, stride=1)

        # 定义第五个block，包含三个卷积
        self.conv5_1 = Conv2D(in_channels=in_channels[4], out_channels=in_channels[5], kernel_size=3, padding=1, stride=1)
        self.conv5_2 = Conv2D(in_channels=in_channels[5], out_channels=in_channels[5], kernel_size=3, padding=1, stride=1)
        self.conv5_3 = Conv2D(in_channels=in_channels[5], out_channels=in_channels[5], kernel_size=3, padding=1, stride=1)


        # 使用Sequential 将全连接层和relu组成一个线性结构（fc + relu）
        # 当输入为224x224时，经过五个卷积块和池化层后，特征维度变为[512x7x7]
        self.fc1 = paddle.nn.Sequential(paddle.nn.Linear(512 * 7 * 7, 4096), paddle.nn.ReLU())
        self.drop1_ratio = 0.5
        self.dropout1 = paddle.nn.Dropout(self.drop1_ratio, mode='upscale_in_train')
        # 使用Sequential 将全连接层和relu组成一个线性结构（fc + relu）
        self.fc2 = paddle.nn.Sequential(paddle.nn.Linear(4096, 4096), paddle.nn.ReLU())

        self.drop2_ratio = 0.5
        self.dropout2 = paddle.nn.Dropout(self.drop2_ratio, mode='upscale_in_train')
        self.fc3 = paddle.nn.Linear(4096, 1)

        self.relu = paddle.nn.ReLU()
        self.pool = MaxPool2D(stride=2, kernel_size=2)
    
    def forward(self, x):
        x = self.relu(self.conv1_1(x))
        x = self.relu(self.conv1_2(x))
        x = self.pool(x)

        x = self.relu(self.conv2_1(x))
        x = self.relu(self.conv2_2(x))
        x = self.pool(x)

        x = self.relu(self.conv3_1(x))
        x = self.relu(self.conv3_2(x))
        x = self.relu(self.conv3_3(x))
        x = self.pool(x)

        x = self.relu(self.conv4_1(x))
        x = self.relu(self.conv4_2(x))
        x = self.relu(self.conv4_3(x))
        x = self.pool(x)

        x = self.relu(self.conv5_1(x))
        x = self.relu(self.conv5_2(x))
        x = self.relu(self.conv5_3(x))
        x = self.pool(x)

        x = paddle.flatten(x, 1, -1)
        x = self.dropout1(self.fc1(x))
        x = self.dropout2(self.fc2(x))
        x = self.fc3(x)
        return x


DATADIR = '/srv/data/palm/PALM-Training400/PALM-Training400'
# DATADIR = '/home/aistudio/work/palm/PALM-Training400/PALM-Training400'
DATADIR2 = '/srv/data/palm/PALM-Validation400'
# DATADIR2 = '/home/aistudio/work/palm/PALM-Validation400'
CSVFILE = '/srv/data/palm/labels.csv'

# 对读入的图像数据进行预处理
def transform_img(img):
    # 将图片尺寸缩放道 224x224
    img = cv2.resize(img, (224, 224))
    # 读入的图像数据格式是[H, W, C]
    # 使用转置操作将其变成[C, H, W]
    img = np.transpose(img, (2,0,1))
    img = img.astype('float32')
    # 将数据范围调整到[-1.0, 1.0]之间
    img = img / 255.
    img = img * 2.0 - 1.0
    return img


# 定义训练集数据读取器
def data_loader(datadir, batch_size=10, mode = 'train'):
    # 将datadir目录下的文件列出来，每条文件都要读入
    filenames = os.listdir(datadir)
    def reader():
        if mode == 'train':
            # 训练时随机打乱数据顺序
            random.shuffle(filenames)
        batch_imgs = []
        batch_labels = []
        for name in filenames:
            filepath = os.path.join(datadir, name)
            img = cv2.imread(filepath)
            img = transform_img(img)
            if name[0] == 'H' or name[0] == 'N':
                # H开头的文件名表示高度近似，N开头的文件名表示正常视力
                # 高度近视和正常视力的样本，都不是病理性的，属于负样本，标签为0
                label = 0
            elif name[0] == 'P':
                # P开头的是病理性近视，属于正样本，标签为1
                label = 1
            else:
                raise('Not excepted file name')
            # 每读取一个样本的数据，就将其放入数据列表中

            # 每读取一个样本的数据，就将其放入数据列表中
            batch_imgs.append(img)
            batch_labels.append(label)
            if len(batch_imgs) == batch_size:
                # 当数据列表的长度等于batch_size的时候，
                # 把这些数据当作一个mini-batch，并作为数据生成器的一个输出
                imgs_array = np.array(batch_imgs).astype('float32')
                labels_array = np.array(batch_labels).astype('float32').reshape(-1, 1)
                yield imgs_array, labels_array
                batch_imgs = []
                batch_labels = []

        if len(batch_imgs) > 0:
            # 剩余样本数目不足一个batch_size的数据，一起打包成一个mini-batch
            imgs_array = np.array(batch_imgs).astype('float32')
            labels_array = np.array(batch_labels).astype('float32').reshape(-1, 1)
            yield imgs_array, labels_array
    return reader



# 定义验证集数据读取器
def valid_data_loader(datadir, csvfile, batch_size=10, mode='valid'):
    # 训练集读取时通过文件名来确定样本标签，验证集则通过csvfile来读取每个图片对应的标签
    # 请查看解压后的验证集标签数据，观察csvfile文件里面所包含的内容
    # csvfile文件所包含的内容格式如下，每一行代表一个样本，
    # 其中第一列是图片id，第二列是文件名，第三列是图片标签，
    # 第四列和第五列是Fovea的坐标，与分类任务无关
    # ID,imgName,Label,Fovea_X,Fovea_Y
    # 1,V0001.jpg,0,1157.74,1019.87
    # 2,V0002.jpg,1,1285.82,1080.47
    # 打开包含验证集标签的csvfile，并读入其中的内容
    filelists = open(csvfile).readlines()
    def reader():
        batch_imgs = []
        batch_labels = []
        for line in filelists[1:]:
            line = line.strip().split(',')
            name = line[1]
            label = int(line[2])
            # 根据图片文件名加载图片，并对图像数据作预处理
            filepath = os.path.join(datadir, name)
            img = cv2.imread(filepath)
            img = transform_img(img)
            # 每读取一个样本的数据，就将其放入数据列表中
            batch_imgs.append(img)
            batch_labels.append(label)
            if len(batch_imgs) == batch_size:
                # 当数据列表的长度等于batch_size的时候，
                # 把这些数据当作一个mini-batch，并作为数据生成器的一个输出
                imgs_array = np.array(batch_imgs).astype('float32')
                labels_array = np.array(batch_labels).astype('float32').reshape(-1, 1)
                yield imgs_array, labels_array
                batch_imgs = []
                batch_labels = []

        if len(batch_imgs) > 0:
            # 剩余样本数目不足一个batch_size的数据，一起打包成一个mini-batch
            imgs_array = np.array(batch_imgs).astype('float32')
            labels_array = np.array(batch_labels).astype('float32').reshape(-1, 1)
            yield imgs_array, labels_array

    return reader



# 定义训练过程
def train(model, optimizer):
    # 开启0号GPU训练
    paddle.device.set_device('gpu:0')
    print('start training ... ')
    model.train()
    
    # 定义数据读取器，训练数据读取器和验证数据读取器
    train_loader = data_loader(DATADIR, batch_size=10, mode='train')
    valid_loader = valid_data_loader(DATADIR2, CSVFILE)

    for epoch in range(EPOCH_NUM):
        for batch_id, data in enumerate(train_loader()):
            x_data, y_data = data
            img = paddle.to_tensor(x_data)
            label = paddle.to_tensor(y_data)
            # 计算模型输出
            logits = model(img)
            # 计算损失函数
            loss = F.binary_cross_entropy_with_logits(logits, label)
            avg_loss = paddle.mean(loss)
            if batch_id % 20 == 0:
                print("epoch: {}, batch_id: {}, loss is: {:.4f}".format(epoch, batch_id, float(avg_loss.numpy())))
            # 反向传播，更新权重，清除梯度
            avg_loss.backward()
            optimizer.step()
            optimizer.clear_grad()


        model.eval()
        accuracies = []
        losses = []

        for batch_id, data in enumerate(valid_loader()):
            x_data, y_data = data
            img = paddle.to_tensor(x_data)
            label = paddle.to_tensor(y_data)
            # 运行模型前向计算，得到预测值
            logits = model(img)
            # 二分类，sigmoid计算后的结果以0.5为阈值分两个类别
            # 计算sigmoid后的预测概率，进行loss计算
            pred = F.sigmoid(logits)
            loss = F.binary_cross_entropy_with_logits(logits, label)
            # 计算预测概率小于0.5的类别
            pred2 = pred * (-1.0) + 1.0
            # 得到两个类别的预测概率，并沿第一个维度级联
            pred = paddle.concat([pred2, pred], axis=1)
            acc = paddle.metric.accuracy(pred, paddle.cast(label, dtype='int64'))

            accuracies.append(acc.numpy())
            losses.append(loss.numpy())

        print("[validation] accuracy/loss: {:.4f}/{:.4f}".format(np.mean(accuracies), np.mean(losses)))

        model.train()
        paddle.save(model.state_dict(), 'palm.pdparams')
        paddle.save(optimizer.state_dict(), 'palm.pdopt')


# 查看数据形状

train_loader = data_loader(DATADIR, 
                           batch_size=10, mode='train')
data_reader = train_loader()
data = next(data_reader)
print(data[0].shape, data[1].shape)

eval_loader = data_loader(DATADIR, 
                           batch_size=10, mode='eval')
data_reader = eval_loader()
data = next(data_reader)
print(data[0].shape, data[1].shape)



# 创建模型
model = VGG()
# opt = paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters())
opt = paddle.optimizer.Momentum(learning_rate=0.001, momentum=0.9, parameters=model.parameters())

# 启动训练过程
train(model, opt)
```

打印网络参数

```
----------------------------------------------------------------------------
 Layer (type)        Input Shape          Output Shape         Param #    
============================================================================
   Conv2D-1      [[10, 3, 224, 224]]   [10, 64, 224, 224]       1,792     
    ReLU-3          [[10, 4096]]           [10, 4096]             0       
   Conv2D-2     [[10, 64, 224, 224]]   [10, 64, 224, 224]      36,928     
  MaxPool2D-1    [[10, 512, 14, 14]]    [10, 512, 7, 7]           0       
   Conv2D-3     [[10, 64, 112, 112]]  [10, 128, 112, 112]      73,856     
   Conv2D-4     [[10, 128, 112, 112]] [10, 128, 112, 112]      147,584    
   Conv2D-5      [[10, 128, 56, 56]]   [10, 256, 56, 56]       295,168    
   Conv2D-6      [[10, 256, 56, 56]]   [10, 256, 56, 56]       590,080    
   Conv2D-7      [[10, 256, 56, 56]]   [10, 256, 56, 56]       590,080    
   Conv2D-8      [[10, 256, 28, 28]]   [10, 512, 28, 28]      1,180,160   
   Conv2D-9      [[10, 512, 28, 28]]   [10, 512, 28, 28]      2,359,808   
   Conv2D-10     [[10, 512, 28, 28]]   [10, 512, 28, 28]      2,359,808   
   Conv2D-11     [[10, 512, 14, 14]]   [10, 512, 14, 14]      2,359,808   
   Conv2D-12     [[10, 512, 14, 14]]   [10, 512, 14, 14]      2,359,808   
   Conv2D-13     [[10, 512, 14, 14]]   [10, 512, 14, 14]      2,359,808   
   Linear-1         [[10, 25088]]          [10, 4096]        102,764,544  
    ReLU-1          [[10, 4096]]           [10, 4096]             0       
   Dropout-1        [[10, 4096]]           [10, 4096]             0       
   Linear-2         [[10, 4096]]           [10, 4096]        16,781,312   
    ReLU-2          [[10, 4096]]           [10, 4096]             0       
   Dropout-2        [[10, 4096]]           [10, 4096]             0       
   Linear-3         [[10, 4096]]            [10, 1]             4,097     
============================================================================
Total params: 134,264,641
Trainable params: 134,264,641
Non-trainable params: 0
----------------------------------------------------------------------------
Input size (MB): 5.74
Forward/backward pass size (MB): 1037.70
Params size (MB): 512.18
Estimated Total Size (MB): 1555.62
```

```
epoch: 0, batch_id: 0, loss is: 0.9093
epoch: 0, batch_id: 20, loss is: 0.7046
[validation] accuracy/loss: 0.9275/0.3187
epoch: 1, batch_id: 0, loss is: 0.5495
epoch: 1, batch_id: 20, loss is: 0.3793
[validation] accuracy/loss: 0.9175/0.2538
epoch: 2, batch_id: 0, loss is: 0.2757
epoch: 2, batch_id: 20, loss is: 0.3980
[validation] accuracy/loss: 0.9075/0.2623
epoch: 3, batch_id: 0, loss is: 0.4037
epoch: 3, batch_id: 20, loss is: 0.2500
[validation] accuracy/loss: 0.8950/0.2655
epoch: 4, batch_id: 0, loss is: 0.2320
epoch: 4, batch_id: 20, loss is: 0.3638
[validation] accuracy/loss: 0.9275/0.1923
epoch: 5, batch_id: 0, loss is: 0.0989
epoch: 5, batch_id: 20, loss is: 0.3965
[validation] accuracy/loss: 0.9300/0.1830
epoch: 6, batch_id: 0, loss is: 0.1715
epoch: 6, batch_id: 20, loss is: 0.2450
[validation] accuracy/loss: 0.9350/0.1575
epoch: 7, batch_id: 0, loss is: 0.1271
epoch: 7, batch_id: 20, loss is: 0.6238
[validation] accuracy/loss: 0.9400/0.1615
...
```

通过运行结果可以发现，在眼疾筛查数据集iChallenge-PM上使用VGG，loss能有效的下降，经过7个epoch的训练，在验证集上的准确率可以达到94%左右