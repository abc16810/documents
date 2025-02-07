LeNet网络的实现代码如下

```python
class LeNet(paddle.nn.Layer):

    def __init__(self, num_classes=1):
        super(LeNet, self).__init__()

        # 创建卷积和池化层
        # 创建第1个卷积层
        self.conv1 = Conv2D(in_channels=1, out_channels=6, kernel_size=5)   # [N,1,28,28]  -> [N, 6, 24, 24]
        self.max_pool1 = MaxPool2D(kernel_size=2, stride=2)  #   [N, 6, 12, 12]
        # 尺寸的逻辑：池化层未改变通道数；当前通道数为6
        # 创建第2个卷积层
        self.conv2 = Conv2D(in_channels=6, out_channels=16, kernel_size=5)  # [N, 16, 8, 8]
        self.max_pool2 = MaxPool2D(kernel_size=2, stride=2)   # [N, 16, 4, 4]

        # 创建第3个卷积层
        self.conv3 = Conv2D(in_channels=16, out_channels=120, kernel_size=4)   # [N, 120, 1, 1]

        # 尺寸的逻辑：输入层将数据拉平[B,C,H,W] -> [B,C*H*W]
        # 输入size是[28,28]，经过三次卷积和两次池化之后，C*H*W等于120
        self.fc1 = Linear(in_features=120, out_features=64)   # [N, 64]
        # 创建全连接层，第一个全连接层的输出神经元个数为64， 第二个全连接层输出神经元个数为分类标签的类别数
        self.fc2 = Linear(in_features=64, out_features=num_classes)

    # 网络的前向计算过程
    def forward(self, x):
        x = self.conv1(x)
        # 每个卷积层使用Sigmoid激活函数，后面跟着一个2x2的池化
        x = F.sigmoid(x)
        x = self.max_pool1(x)
        x = F.sigmoid(x)
        x = self.conv2(x)
        x = self.max_pool2(x)
        x = self.conv3(x)
        # 尺寸的逻辑：输入层将数据拉平[B,C,H,W] -> [B,C*H*W]
        x = paddle.reshape(x, [x.shape[0], -1])
        x = self.fc1(x)
        x = F.sigmoid(x)
        x = self.fc2(x)
        return x
```

查看经过LeNet-5的每一层作用之后，输出数据的形状

```python
model = LeNet(num_classes=10)
params_info = paddle.summary(model, (3,1,28,28))
print(params_info)
```
```
---------------------------------------------------------------------------
 Layer (type)       Input Shape          Output Shape         Param #
===========================================================================
   Conv2D-1       [[3, 1, 28, 28]]      [3, 6, 24, 24]          156
  MaxPool2D-1     [[3, 6, 24, 24]]      [3, 6, 12, 12]           0
   Conv2D-2       [[3, 6, 12, 12]]      [3, 16, 8, 8]          2,416
  MaxPool2D-2     [[3, 16, 8, 8]]       [3, 16, 4, 4]            0
   Conv2D-3       [[3, 16, 4, 4]]       [3, 120, 1, 1]        30,840
   Linear-1          [[3, 120]]            [3, 64]             7,744
   Linear-2          [[3, 64]]             [3, 10]              650
===========================================================================
Total params: 41,806
Trainable params: 41,806
Non-trainable params: 0
```

定义训练过程

```python
# 设置迭代轮数
EPOCH_NUM = 10
# 设置优化器为Momentum，学习率为0.001
opt = paddle.optimizer.Momentum(learning_rate=0.001, momentum=0.9, parameters=model.parameters())

# 定义数据读取器
train_loader = paddle.io.DataLoader(MNIST(mode='train', transform=ToTensor()), batch_size=10, shuffle=True)
valid_loader = paddle.io.DataLoader(MNIST(mode='test', transform=ToTensor()), batch_size=10)

def train(model, opt, train_loader, valid_loader):
    # 开启0号GPU训练
    use_gpu = True
    paddle.device.set_device('gpu:0') if use_gpu else paddle.device.set_device('cpu')
    print('start training ... ')
    model.train()
    for epoch in range(EPOCH_NUM):
        for batch_id, data in enumerate(train_loader()):
            img = data[0]
            label = data[1] 
            # 计算模型输出
            logits = model(img)
            # 计算损失函数
            loss_func = paddle.nn.CrossEntropyLoss(reduction='none')
            loss = loss_func(logits, label)
            avg_loss = paddle.mean(loss)

            if batch_id % 2000 == 0:
                print("epoch: {}, batch_id: {}, loss is: {:.4f}".format(epoch, batch_id, float(avg_loss.numpy())))
            avg_loss.backward()
            opt.step()
            opt.clear_grad()

        model.eval()
        accuracies = []
        losses = []
        for batch_id, data in enumerate(valid_loader()):
            img = data[0]
            label = data[1] 
            # 计算模型输出
            logits = model(img)
            pred = F.softmax(logits)
            # 计算损失函数
            loss_func = paddle.nn.CrossEntropyLoss(reduction='none')
            loss = loss_func(logits, label)
            acc = paddle.metric.accuracy(pred, label)
            accuracies.append(acc.numpy())
            losses.append(loss.numpy())
        print("[validation] accuracy/loss: {:.4f}/{:.4f}".format(np.mean(accuracies), np.mean(losses)))
        model.train()

    # 保存模型参数
    paddle.save(model.state_dict(), 'mnist.pdparams')

# 启动训练过程
train(model, opt, train_loader, valid_loader)
```

```
start training ... 
epoch: 0, batch_id: 0, loss is: 2.4042
epoch: 0, batch_id: 2000, loss is: 2.2771
epoch: 0, batch_id: 4000, loss is: 2.2125
[validation] accuracy/loss: 0.6155/1.5107
epoch: 1, batch_id: 0, loss is: 1.6003
epoch: 1, batch_id: 2000, loss is: 0.4597
epoch: 1, batch_id: 4000, loss is: 0.3909
[validation] accuracy/loss: 0.8890/0.3828
epoch: 2, batch_id: 0, loss is: 0.1339
epoch: 2, batch_id: 2000, loss is: 0.1611
epoch: 2, batch_id: 4000, loss is: 0.4505
[validation] accuracy/loss: 0.9214/0.2609
epoch: 3, batch_id: 0, loss is: 0.1987
epoch: 3, batch_id: 2000, loss is: 0.1271
epoch: 3, batch_id: 4000, loss is: 0.0614
[validation] accuracy/loss: 0.9332/0.2176
epoch: 4, batch_id: 0, loss is: 0.2938
epoch: 4, batch_id: 2000, loss is: 0.0325
epoch: 4, batch_id: 4000, loss is: 0.1326
[validation] accuracy/loss: 0.9472/0.1776

```
通过运行结果可以看出，训练5轮LeNet在手写数字识别MNIST验证数据集上的准确率高达94%以上。