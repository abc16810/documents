iChallenge-PM是百度大脑和中山大学中山眼科中心联合举办的iChallenge比赛中，提供的关于病理性近视（Pathologic Myopia，PM）的医疗类数据集，包含1200个受试者的眼底视网膜图片，训练、验证和测试数据集各400张。下面我们详细介绍LeNet在iChallenge-PM上的训练过程。


#### 数据集准备

- training.zip：包含训练中的图片和标签
- validation.zip：包含验证集的图片
- valid_gt.zip：包含验证集的标签 

解压后

```
训练图片目录：./PALM-Training400/PALM-Training400
验证图片目录：./PALM-Validation400
验证标签文件：./labels.csv
```

> valid_gt.zip文件解压缩之后，需要将PALM-Validation-GT/目录下的PM_Label_and_Fovea_Location.xlsx文件转存成csv格式，本节代码示例中已经提前转成文件labels.csv


#### 查看数据集图片

iChallenge-PM中既有病理性近视患者的眼底图片，也有非病理性近视患者的图片，命名规则如下：
- 病理性近视（PM）：文件名以P开头
- 非病理性近视（non-PM）
    - 高度近似（high myopia）：文件名以H开头
    - 正常眼睛（normal）：文件名以N开头

我们将病理性患者的图片作为正样本，标签为1； 非病理性患者的图片作为负样本，标签为0。从数据集中选取两张图片，通过LeNet提取特征，构建分类器，对正负样本进行分类，并将图片显示出来。代码如下所示：

```python
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    %matplotlib inline
    from PIL import Image
    DATADIR = '/home/aistudio/work/palm/PALM-Training400/PALM-Training400'
    # 文件名以N开头的是正常眼底图片，以P开头的是病变眼底图片
    file1 = 'N0012.jpg'
    file2 = 'P0095.jpg'
    # 读取图片
    img1 = Image.open(os.path.join(DATADIR, file1))
    img1 = np.array(img1)
    img2 = Image.open(os.path.join(DATADIR, file2))
    img2 = np.array(img2)
    # 画出读取的图片
    plt.figure(figsize=(16, 8))
    f = plt.subplot(121)
    f.set_title('Normal', fontsize=20)
    plt.imshow(img1)
    f = plt.subplot(122)
    f.set_title('PM', fontsize=20)
    plt.imshow(img2)
    plt.show()
```

![](https://static.sitestack.cn/projects/paddlepaddle-tutorials/d0407c759ba94fa9d3a5b299a22f897b.png)

```
# 查看图片形状
print(img1.shape, img2.shape)
```
(2056, 2124, 3) (2056, 2124, 3)



#### 定义数据读取器


使用OpenCV从磁盘读入图片，将每张图缩放到224*224大小，并且将像素值调整到[-1,1]之间，代码如下所示：

```python
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
```

#### 查看数据形状

```python
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
```
```
(10, 3, 224, 224), (10, 1)
(10, 3, 224, 224), (10, 1)
```

#### 定义网络

```python
class LeNet(paddle.nn.Layer):

    def __init__(self, num_classes=1):
        super(LeNet, self).__init__()

     
        # 创建卷积和池化层块，每个卷积层使用Sigmoid激活函数，后面跟着一个2x2的池化
        self.conv1 = Conv2D(in_channels=3, out_channels=6, kernel_size=5)  # [N,3,h,w]  -> [N, 6, h, w]
        self.max_pool1 = MaxPool2D(kernel_size=2, stride=2)   #   [N, 6, h/2, w/2]

        self.conv2 = Conv2D(in_channels=6, out_channels=16, kernel_size=5)
        self.max_pool2 = MaxPool2D(kernel_size=2, stride=2)   

        # 创建第3个卷积层
        self.conv3 = Conv2D(in_channels=16, out_channels=120, kernel_size=4)   # [N, 120, 1, 1]

        # 尺寸的逻辑：输入层将数据拉平[B,C,H,W] -> [B,C*H*W]
        # 输入size是[50,50]，经过三次卷积和两次池化之后，C*H*W等于120
        # 创建全连接层，第一个全连接层的输出神经元个数为64
        self.fc1 = Linear(in_features=300000, out_features=64)
        # 第二个全连接层输出神经元个数为分类标签的类别数
        self.fc2 = Linear(in_features=64, out_features=num_classes)


    # 网络的前向计算过程
    def forward(self, x, label=None):
        x = self.conv1(x)
        # 每个卷积层使用Sigmoid激活函数，后面跟着一个2x2的池化
        x = F.sigmoid(x)
        x = self.max_pool1(x)
        x = F.sigmoid(x)
        x = self.conv2(x)
        x = self.max_pool2(x)
        x = self.conv3(x)
        x = F.sigmoid(x)

        # 尺寸的逻辑：输入层将数据拉平[B,C,H,W] -> [B,C*H*W]
        x = paddle.reshape(x, [x.shape[0], -1])
        x = self.fc1(x)
        x = F.sigmoid(x)
        x = self.fc2(x)
        if label is not None:
            if self.num_classes == 1:
                pred = F.sigmoid(x)
                pred = paddle.concat([1.0 - pred, pred], axis=1)

                acc = paddle.metric.accuracy(pred, paddle.cast(label, dtype='int64'))
            else:
                acc = paddle.metric.accuracy(x, paddle.cast(label, dtype='int64'))
            return x, acc

        else:
            return x

        return x
```

#### 定义训练过程

```python

DATADIR = '/srv/data/palm/PALM-Training400/PALM-Training400'
# DATADIR = '/home/aistudio/work/palm/PALM-Training400/PALM-Training400'
DATADIR2 = '/srv/data/palm/PALM-Validation400'
# DATADIR2 = '/home/aistudio/work/palm/PALM-Validation400'
CSVFILE = '/srv/data/palm/labels.csv'

EPOCH_NUM = 10

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
            print(pred, label)
            acc = paddle.metric.accuracy(pred, paddle.cast(label, dtype='int64'))

            accuracies.append(acc.numpy())
            losses.append(loss.numpy())

        print("[validation] accuracy/loss: {:.4f}/{:.4f}".format(np.mean(accuracies), np.mean(losses)))

        model.train()
        paddle.save(model.state_dict(), 'palm.pdparams')
        paddle.save(optimizer.state_dict(), 'palm.pdopt')


# 创建模型
model = LeNet(num_classes=1)
# 启动训练过程
opt = paddle.optimizer.Momentum(learning_rate=0.001, momentum=0.9, parameters=model.parameters())
train(model, optimizer=opt)
```