### 单阶段目标检测模型YOLOv3


YOLOv3算法基本思想可以分成两部分：

- 按一定规则在图片上产生一系列的候选区域，然后根据这些候选区域与图片上物体真实框之间的位置关系对候选区域进行标注。跟真实框足够接近的那些候选区域会被标注为正样本，同时将真实框的位置作为正样本的位置目标。偏离真实框较大的那些候选区域则会被标注为负样本，负样本不需要预测位置或者类别。
- 使用卷积神经网络提取图片特征并对候选区域的位置和类别进行预测。这样每个预测框就可以看成是一个样本，根据真实框相对它的位置和类别进行了标注而获得标签值，通过网络模型预测其位置和类别，将网络预测值和标签值进行比较，就可以建立起损失函数。

YOLOv3算法预测过程的流程图如 图1 所示，预测图片经过一系列预处理(resize、normalization等)输入到YOLOv3模型，根据预先设定的Anchor和提取到的图片特征得到目标预测框，最后通过非极大值抑制(NMS)消除重叠较大的冗余预测框，得到最终预测结果。

![](./imgs/e92ba2985c474efa8e83b17289b0534c8ffc616cb8c3441c8d268936d90bc571.png)


YOLOv3网络结构大致分为3个部分：Backbone、Neck、Head，如 图2 所示:

![](./imgs/682c9a2807ed4b34b5ef575e56d4c629623c5e2d86a442b6b49d32decd1f821c.jpg)


- Backbone：骨干网络，主要用于特征提取
- Neck：在Backbone和Head之间提取不同阶段中特征图
- Head：检测头，用于预测目标的类别和位置


#### 产生候选区域


如何产生候选区域，是检测模型的核心设计方案。目前大多数基于卷积神经网络的模型所采用的方式大体如下：

- 按一定的规则在图片上生成一系列位置固定的锚框，将这些锚框看作是可能的候选区域。
- 对锚框是否包含目标物体进行预测，如果包含目标物体，还需要预测所包含物体的类别，以及预测框相对于锚框位置需要调整的幅度。

#### 生成锚框

将原始图片划分成m×n个区域，如下图所示，原始图片高度H=640, 宽度W=480，如果我们选择小块区域的尺寸为32×32则m和n分别为：

```math
m = \frac{640}{32} = 20
```
```math
n = \frac{480}{32} = 15
```

将原始图像分成了20行15列小方块区域。

![](./imgs/2dd1cbeb53644552a8cb38f3f834dbdda5046a489465454d93cdc88d1ce65ca5.png)

> 最上面的行号是第0行，最左边的列号是第0列

YOLOv3算法会在每个区域的中心，生成一系列锚框。为了展示方便，我们先在图中第十行第四列的小方块位置附近画出生成的锚框，如 图4 所示。

![](./imgs/6dd42b9138364a379b6231ac2247d3cb449d612e17be4896986bca2703acbb29.png)
> 图4：在第10行第4列的小方块区域生成3个锚框 

如下展示在每个区域附近都生成3个锚框，很多锚框堆叠在一起可能不太容易看清楚，但过程跟上面类似，只是需要以每个区域的中心点为中心，分别生成3个锚框。

![](./imgs/0880c3b5ec2d40edb476f4fcbadd87aa9f37059cd24d4a1a9d37c627ce5f618a.png)


#### 生成预测框

在前面已经指出，锚框的位置都是固定好的，不可能刚好跟物体边界框重合，需要在锚框的基础上进行位置的微调以生成预测框。预测框相对于锚框会有不同的中心位置和大小，采用什么方式能得到预测框呢？我们先来考虑如何生成其中心位置坐标。

比如上面图中在第10行第4列的小方块区域中心生成的一个锚框，如绿色虚线框所示。以小方格的宽度为单位长度，

此小方块区域左上角的位置坐标是：

```math
c_x = 4, \\
c_y = 10
```

此锚框的区域中心坐标是：

```math
center_x=c_x​+0.5=4.5 \\ 
center_y=c_y​+0.5=10.5 
```

可以通过下面的方式生成预测框的中心坐标：

```math
b_x = c_x + \sigma(t_x)
```
```math
b_y = c_y + \sigma(t_y)
```
其中 $t_x$ ​和 $t_y$ ​为实数，σ(x)是我们之前学过的Sigmoid函数，其定义如下：

```math
\sigma(x) = \frac{1}{1 + exp(-x)}
```
由于Sigmoid的函数值在0∼1之间，因此由上面公式计算出来的预测框的中心点总是落在第十行第四列的小区域内部。

当 $t_x=t_y=0$ 时， $b_x = c_x + 0.5，b_y = c_y + 0.5$ ，预测框中心与锚框中心重合，都是小区域的中心。

锚框的大小是预先设定好的，在模型中可以当作是超参数，下图中画出的锚框尺寸是

```math
p_h = 350 \\
p_w = 250
```
通过下面的公式生成预测框的大小：

```math
b_h = p_h e^{t_h} \\
b_w = p_w e^{t_w}
```

如果 $t_x=t_y=0, t_h=t_w=0$ ，则预测框跟锚框重合。

如果给 $t_x, t_y, t_h, t_w$ ​随机赋值如下

```math
t_x = 0.2,  t_y = 0.3, t_w = 0.1, t_h = -0.12
```

则可以得到预测框的坐标是(145.59, 338.33, 276.29, 310.42)(这里坐标采用xywh的格式。)，如 图6 中蓝色框所示

![](.//imgs/f4b33522eb5a45f0804b94a5c66b76a0a2d13345d6de499399580a031b6ccc74.png)

这里我们会问：当 $t_x, t_y, t_w, t_h$ ​取值为多少的时候，预测框能够跟真实框重合？为了回答问题，只需要将上面预测框坐标中的 $b_x, b_y, b_h, b_w$ ​设置为真实框的位置，即可求解出ttt的数值

令：

```math
\sigma(t^*_x) + c_x = gt_x
```
```math
\sigma(t^*_y) + c_y = gt_y
```
```math
p_w e^{t^*_w} = gt_w
```
```math
p_h e^{t^*_h} = gt_h
```
可以求解出：$(t^*_x, t^*_y, t^*_w, t^*_h)$ 

如果t是网络预测的输出值，将 $t^*$ 作为目标值，以他们之间的差距作为损失函数，则可以建立起一个回归问题，通过学习网络参数，使得t足够接近 $t^*$ ，从而能够求解出预测框的位置坐标和大小。

预测框可以看作是在锚框基础上的一个微调，每个锚框会有一个跟它对应的预测框，我们需要确定上面计算式中的 $t_x, t_y, t_w, t_h$ ​，从而计算出与锚框对应的预测框的位置和形状


#### 对候选区域进行标注

每个区域可以产生3种不同形状的锚框，每个锚框都是一个可能的候选区域，对这些候选区域我们需要了解如下几件事情：

- 锚框是否包含物体，这可以看成是一个二分类问题，使用标签objectness来表示。当锚框包含了物体时，objectness=1，表示预测框属于正类；当锚框不包含物体时，设置objectness=0，表示锚框属于负类。
- 如果锚框包含了物体，那么它对应的预测框的中心位置和大小应该是多少，或者说上面计算式中的 $t_x, t_y, t_w, t_h$ ​应该是多少，使用location标签
- 如果锚框包含了物体，那么具体类别是什么，这里使用变量label来表示其所属类别的标签。

选取任意一个锚框对它进行标注，也就是需要确定其对应的objectness,  $(t_x, t_y, t_w, t_h)$ 和label，下面将分别讲述如何确定这三个标签的值。

**标注锚框是否包含物体**

这里一共有3个目标，以最左边的人像为例，其真实框是(133.96,328.42,186.06,374.63) 。

![](./imgs/f21679e68d2b496698ed788a16d4ea2e5bc6f82b253a44ef9508b6a4fc9b6be4.png)

> 选出与真实框中心位于同一区域的锚框 

真实框的中心点坐标是：

```math
center_x=133.96 \\
center_y=328.42
```

```math
i=133.96/32=4.18625 \\
j=328.42/32=10.263125
```
它落在了第10行第4列的小方块内，如上图所示。此小方块区域可以生成3个不同形状的锚框，其在图上的编号和大小分别是 $A_1(116, 90), A_2(156, 198), A_3(373, 326)$ 。

用这3个不同形状的锚框跟真实框计算IoU，选出IoU最大的锚框。这里为了简化计算，只考虑锚框的形状，不考虑其跟真实框中心之间的偏移，具体计算结果如下图所示。

![](./imgs/3008337ea66c44068042c670db54368edc56b1e43ced4b6b811bdc95b64ca3d5.png)

> 选出与真实框与锚框的IoU 

其中跟真实框IoU最大的是锚框 $A_3$ ​，形状是(373,326)，将它所对应的预测框的objectness标签设置为1，其所包括的物体类别就是真实框里面的物体所属类别。

依次可以找出其他几个真实框对应的IoU最大的锚框，然后将它们的预测框的objectness标签也都设置为1。这里一共有20×15×3=900个锚框，只有3个预测框会被标注为正。

由于每个真实框只对应一个objectness标签为正的预测框，如果有些预测框跟真实框之间的IoU很大，但并不是最大的那个，那么直接将其objectness标签设置为0当作负样本，可能并不妥当。为了避免这种情况，YOLOv3算法设置了一个IoU阈值iou_threshold，当预测框的objectness不为1，但是其与某个真实框的IoU大于iou_threshold时，就将其objectness标签设置为-1，不参与损失函数的计算。

所有其他的预测框，其objectness标签均设置为0，表示负类。

对于objectness=1的预测框，需要进一步确定其位置和包含物体的具体分类标签，但是对于objectness=0或者-1的预测框，则不用管他们的位置和类别。

**标注预测框的位置坐标标签**

当锚框objectness=1时，需要确定预测框位置相对于它微调的幅度，也就是锚框的位置标签。

在前面我们已经问过这样一个问题：当 $t_x, t_y, t_w, t_h$ ​取值为多少的时候，预测框能够跟真实框重合？其做法是将预测框坐标中的 $b_x, b_y, b_h, b_w$ ​设置为真实框的坐标，即可求解出ttt的数值。

令：

```math
\sigma(t^*_x) + c_x = gt_x
```
```math
\sigma(t^*_y) + c_y = gt_y
```
```math
p_w e^{t^*_w} = gt_w
```
```math
p_h e^{t^*_h} = gt_h
```

对于 $t_x^*$ ​和 $t_y^*$ ​，由于Sigmoid的反函数不好计算，我们直接使用 $\sigma(t^*_x)$ 和 $\sigma(t^*_y)$ 作为回归的目标。

```math
d_x^* = \sigma(t^*_x) = gt_x - c_x
```
```math
d_y^* = \sigma(t^*_y) = gt_y - c_y
```
```math
t^*_w = log(\frac{gt_w}{p_w})
```
```math
t^*_h = log(\frac{gt_h}{p_h})

```


如果 $(t_x, t_y, t_h, t_w)$ 是网络预测的输出值，将         $(d_x^*, d_y^*, t_w^*, t_h^*)$  作为 $(\sigma(t_x) , \sigma(t_y), t_h, t_w)$ 的目标值，以它们之间的差距作为损失函数，则可以建立起一个回归问题，通过学习网络参数，使得t足够接近 $t^*$ ，从而能够求解出预测框的位置。


**标注锚框包含物体类别的标签**

对于objectness=1的锚框，需要确定其具体类别。正如上面所说，objectness标注为1的锚框，会有一个真实框跟它对应，该锚框所属物体类别，即是其所对应的真实框包含的物体类别。这里使用one-hot向量来表示类别标签label。比如一共有10个分类，而真实框里面包含的物体类别是第2类，则label为(0,1,0,0,0,0,0,0,0,0)

对上述步骤进行总结，标注的流程如 图15 所示。 

![](./imgs/3b914be0c6274916bc7abe4922d4d0fb75be340172764f7096af5be0c2737c57.png)


通过这种方式，我们在每个小方块区域都生成了一系列的锚框作为候选区域，并且根据图片上真实物体的位置，标注出了每个候选区域对应的objectness标签、位置需要调整的幅度以及包含的物体所属的类别。位置需要调整的幅度由4个变量描述 $(t_x, t_y, t_w, t_h)$ ，objectness标签需要用一个变量描述objobjobj，描述所属类别的变量长度等于类别数C。

对于每个锚框，模型需要预测输出 $(t_x, t_y, t_w, t_h, P_{obj}, P_1, P_2,... , P_C)$ ，其中 $P_{obj}$ ​是锚框是否包含物体的概率， $P_1, P_2,... , P_C$ ​则是锚框包含的物体属于每个类别的概率。

#### Backbone(特征提取)

YOLOv3算法使用的骨干网络是Darknet53。Darknet53网络的具体结构如 图3 所示，在ImageNet图像分类任务上取得了很好的成绩。在检测任务中，将图中C0后面的平均池化、全连接层和Softmax去掉，保留从输入到C0部分的网络结构，作为检测模型的基础网络结构，也称为骨干网络。YOLOv3模型会在骨干网络的基础上，再添加检测相关的网络模块。

![](./imgs/d5cb1e88d3f44259be1427a90ee454a57738ee8083ad40269f5485988526f30d.png)

下面的程序是Darknet53骨干网络的实现代码，这里将上图中C0、C1、C2所表示的输出数据取出，并查看它们的形状分别是，C0[1,1024,20,20]，C1[1,512,40,40]，C2[1,256,80,80]。

特征图的步幅(stride)

在提取特征的过程中通常会使用步幅大于1的卷积或者池化，导致后面的特征图尺寸越来越小，特征图的步幅等于输入图片尺寸除以特征图尺寸。例如：C0的尺寸是20×20，原图尺寸是640×640，则C0的步幅是 $\frac{640}{20}=32$ 。同理，C1的步幅是16，C2的步幅是8。

```python
import paddle
import paddle.nn.functional as F
import numpy as np

class ConvBNLayer(paddle.nn.Layer):
    def __init__(self, ch_in, ch_out, 
                 kernel_size=3, stride=1, groups=1,
                 padding=0, act="leaky"):
        super(ConvBNLayer, self).__init__()
    
        self.conv = paddle.nn.Conv2D(
            in_channels=ch_in,
            out_channels=ch_out,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            groups=groups,
            weight_attr=paddle.ParamAttr(
                initializer=paddle.nn.initializer.Normal(0., 0.02)),
            bias_attr=False)
    
        self.batch_norm = paddle.nn.BatchNorm2D(
            num_features=ch_out,
            weight_attr=paddle.ParamAttr(
                initializer=paddle.nn.initializer.Normal(0., 0.02),
                regularizer=paddle.regularizer.L2Decay(0.)),
            bias_attr=paddle.ParamAttr(
                initializer=paddle.nn.initializer.Constant(0.0),
                regularizer=paddle.regularizer.L2Decay(0.)))
        self.act = act

        
    def forward(self, inputs):
        out = self.conv(inputs)
        out = self.batch_norm(out)
        if self.act == 'leaky':
            out = F.leaky_relu(x=out, negative_slope=0.1)
        return out
    
class DownSample(paddle.nn.Layer):
    # 下采样，图片尺寸减半，具体实现方式是使用stirde=2的卷积
    def __init__(self,
                 ch_in,
                 ch_out,
                 kernel_size=3,
                 stride=2,
                 padding=1):

        super(DownSample, self).__init__()

        self.conv_bn_layer = ConvBNLayer(
            ch_in=ch_in,
            ch_out=ch_out,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding)
        self.ch_out = ch_out
    def forward(self, inputs):
        out = self.conv_bn_layer(inputs)
        return out

class BasicBlock(paddle.nn.Layer):
    """
    基本残差块的定义，输入x经过两层卷积，然后接第二层卷积的输出和输入x相加
    """
    def __init__(self, ch_in, ch_out):
        super(BasicBlock, self).__init__()

        self.conv1 = ConvBNLayer(
            ch_in=ch_in,
            ch_out=ch_out,
            kernel_size=1,
            stride=1,
            padding=0
            )
        self.conv2 = ConvBNLayer(
            ch_in=ch_out,
            ch_out=ch_out*2,
            kernel_size=3,
            stride=1,
            padding=1
            )
    def forward(self, inputs):
        conv1 = self.conv1(inputs)
        conv2 = self.conv2(conv1)
        out = paddle.add(x=inputs, y=conv2)
        return out

     
class LayerWarp(paddle.nn.Layer):
    """
    添加多层残差块，组成Darknet53网络的一个层级
    """
    def __init__(self, ch_in, ch_out, count, is_test=True):
        super(LayerWarp,self).__init__()

        self.basicblock0 = BasicBlock(ch_in,
            ch_out)
        self.res_out_list = []
        for i in range(1, count):
            # 使用add_sublayer添加子层
            res_out = self.add_sublayer("basic_block_%d" % (i), 
                BasicBlock(ch_out*2,
                    ch_out))
            self.res_out_list.append(res_out)

    def forward(self,inputs):
        y = self.basicblock0(inputs)
        for basic_block_i in self.res_out_list:
            y = basic_block_i(y)
        return y

# DarkNet 每组残差块的个数，来自DarkNet的网络结构图
DarkNet_cfg = {53: ([1, 2, 8, 8, 4])}

class DarkNet53_conv_body(paddle.nn.Layer):
    def __init__(self):
        super(DarkNet53_conv_body, self).__init__()
        self.stages = DarkNet_cfg[53]
        self.stages = self.stages[0:5]

        # 第一层卷积
        self.conv0 = ConvBNLayer(
            ch_in=3,
            ch_out=32,
            kernel_size=3,
            stride=1,
            padding=1)

        # 下采样，使用stride=2的卷积来实现
        self.downsample0 = DownSample(
            ch_in=32,
            ch_out=32 * 2)

        # 添加各个层级的实现
        self.darknet53_conv_block_list = []
        self.downsample_list = []
        for i, stage in enumerate(self.stages):
            conv_block = self.add_sublayer(
                "stage_%d" % (i),
                LayerWarp(32*(2**(i+1)),
                32*(2**i),
                stage))
            self.darknet53_conv_block_list.append(conv_block)
        # 两个层级之间使用DownSample将尺寸减半
        for i in range(len(self.stages) - 1):
            downsample = self.add_sublayer(
                "stage_%d_downsample" % i,
                DownSample(ch_in=32*(2**(i+1)),
                    ch_out=32*(2**(i+2))))
            self.downsample_list.append(downsample)

    def forward(self,inputs):
        out = self.conv0(inputs)
        #print("conv1:",out.numpy())
        out = self.downsample0(out)
        #print("dy:",out.numpy())
        blocks = []
        #依次将各个层级作用在输入上面
        for i, conv_block_i in enumerate(self.darknet53_conv_block_list): 
            out = conv_block_i(out)
            blocks.append(out)
            if i < len(self.stages) - 1:
                out = self.downsample_list[i](out)
        return blocks[-1:-4:-1] # 将C0, C1, C2作为返回值
```

```
# 查看Darknet53网络输出特征图
import numpy as np
backbone = DarkNet53_conv_body()
x = np.random.randn(1, 3, 640, 640).astype('float32')
x = paddle.to_tensor(x)
C0, C1, C2 = backbone(x)
print(C0.shape, C1.shape, C2.shape)
```

```
[1, 1024, 20, 20] [1, 512, 40, 40] [1, 256, 80, 80]
```

上面这段示例代码，指定输入数据的形状是(1,3,640,640)(，则3个层级的输出特征图的形状分别是C0(1,1024,20,20)，C1(1,512,40,40)和C2(1,256,80,80)

#### Neck（多尺度检测）

如果只在在特征图P0的基础上进行的，它的步幅stride=32。特征图的尺寸比较小，像素点数目比较少，每个像素点的感受野很大，具有非常丰富的高层级语义信息，可能比较容易检测到较大的目标。为了能够检测到尺寸较小的那些目标，需要在尺寸较大的特征图上面建立预测输出。如果我们在C2或者C1这种层级的特征图上直接产生预测输出，可能面临新的问题，它们没有经过充分的特征提取，像素点包含的语义信息不够丰富，有可能难以提取到有效的特征模式。在目标检测中，解决这一问题的方式是，将高层级的特征图尺寸放大之后跟低层级的特征图进行融合，得到的新特征图既能包含丰富的语义信息，又具有较多的像素点，能够描述更加精细的结构。

具体的网络实现方式如 图4 所示

![](./imgs/b6d3b425644342e48bd0a50ebde90d882fd10717e0e44a53a44e98225bbb6df8.png)

> upsample 上采样是通过`F.interpolate`线性插值方法
> 生成多层级的输出特征图P0、P1、P2 


YOLOv3在每个区域的中心位置产生3个锚框，在3个层级的特征图上产生锚框的大小分别为P2 [(10×13),(16×30),(33×23)]，P1 [(30×61),(62×45),(59× 119)]，P0[(116 × 90), (156 × 198), (373 × 326]。越往后的特征图上用到的锚框尺寸也越大，能捕捉到大尺寸目标的信息；越往前的特征图上锚框尺寸越小，能捕捉到小尺寸目标的信息。

#### 检测头设计(计算预测框位置和类别)


YOLOv3中对每个预测框计算逻辑如下：
- 预测框是否包含物体。也可理解为objectness=1的概率是多少，可以用网络输出一个实数 $x$ 。 可以用Sigmoid(x)表示objectness为正的概率 $P_{obj}$ 
- 预测物体位置和形状。物体位置和形状 $t_x, t_y, t_w, t_h$ ,​可以用网络输出4个实数来表示 $t_x, t_y, t_w, t_h$ 。
- 预测物体类别。预测图像中物体的具体类别是什么，或者说其属于每个类别的概率分别是多少。总的类别数为C，需要预测物体属于每个类别的概率 $(P_1, P_2, ..., P_C)$ ，可以用网络输出C个实数 $(x_1, x_2, ..., x_C)$ ，对每个实数分别求Sigmoid函数，让   $P_i = Sigmoid(x_i)$ ，则可以表示出物体属于每个类别的概率。


对于一个预测框，网络需要输出(5+C)个实数来表征它是否包含物体、位置和形状尺寸以及属于每个类别的概率

由于我们在每个小方块区域都生成了K个预测框，则所有预测框一共需要网络输出的预测值数目是：

```math
[K(5+C)]×m×n
```

还有更重要的一点是网络输出必须要能区分出小方块区域的位置来，不能直接将特征图连接一个输出大小为 $[K(5 + C)] \times m \times n$ 的全连接层


**建立输出特征图与预测框之间的关联**


现在观察特征图，经过多次卷积核池化之后，其步幅stride=32，640×480大小的输入图片变成了20×15的特征图；而小方块区域的数目正好是20×15，也就是说可以让特征图上每个像素点分别跟原图上一个小方块区域对应。这也是为什么我们最开始将小方块区域的尺寸设置为32的原因，这样可以巧妙的将小方块区域跟特征图上的像素点对应起来，解决了空间位置的对应关系。

![](./imgs/59bd2592dd9f4f4dada8333307198888e667b15969ce434eb52c0232d9608a62.png)

> 特征图C0与小方块区域形状对比 

下面需要将像素点(i,j)与第i行第j列的小方块区域所需要的预测值关联起来，每个小方块区域产生K个预测框，每个预测框需要)(5+C)个实数预测值，则每个像素点相对应的要有K(5+C)个实数。为了解决这一问题，对特征图进行多次卷积，并将最终的输出通道数设置为K(5+C)，即可将生成的特征图与每个预测框所需要的预测值巧妙的对应起来。当然，这种对应是为了将骨干网络提取的特征对接输出层来形成Loss。实际中，这几个尺寸可以随着任务数据分布的不同而调整，只要保证特征图输出尺寸（控制卷积核和下采样）和输出层尺寸（控制小方块区域的大小）相同即可。

骨干网络的输出特征图是C0，下面的程序是对C0进行多次卷积以得到跟预测框相关的特征图P0。

```python
class YoloDetectionBlock(paddle.nn.Layer):
    # define YOLOv3 detection head
    # 使用多层卷积和BN提取特征
    def __init__(self,ch_in,ch_out,is_test=True):
        super(YoloDetectionBlock, self).__init__()

        assert ch_out % 2 == 0, \
            "channel {} cannot be divided by 2".format(ch_out)

        self.conv0 = ConvBNLayer(
            ch_in=ch_in,
            ch_out=ch_out,
            kernel_size=1,
            stride=1,
            padding=0)
        self.conv1 = ConvBNLayer(
            ch_in=ch_out,
            ch_out=ch_out*2,
            kernel_size=3,
            stride=1,
            padding=1)
        self.conv2 = ConvBNLayer(
            ch_in=ch_out*2,
            ch_out=ch_out,
            kernel_size=1,
            stride=1,
            padding=0)
        self.conv3 = ConvBNLayer(
            ch_in=ch_out,
            ch_out=ch_out*2,
            kernel_size=3,
            stride=1,
            padding=1)
        self.route = ConvBNLayer(
            ch_in=ch_out*2,
            ch_out=ch_out,
            kernel_size=1,
            stride=1,
            padding=0)
        self.tip = ConvBNLayer(
            ch_in=ch_out,
            ch_out=ch_out*2,
            kernel_size=3,
            stride=1,
            padding=1)
    def forward(self, inputs):
        out = self.conv0(inputs)
        out = self.conv1(out)
        out = self.conv2(out)
        out = self.conv3(out)
        route = self.route(out)
        tip = self.tip(route)
        return route, tip
```

```
NUM_ANCHORS = 3
NUM_CLASSES = 7
num_filters=NUM_ANCHORS * (NUM_CLASSES + 5)

backbone = DarkNet53_conv_body()
detection = YoloDetectionBlock(ch_in=1024, ch_out=512)
conv2d_pred = paddle.nn.Conv2D(in_channels=1024, out_channels=num_filters, kernel_size=1)

x = np.random.randn(1, 3, 640, 640).astype('float32')
x = paddle.to_tensor(x)
C0, C1, C2 = backbone(x)
route, tip = detection(C0)
P0 = conv2d_pred(tip)

print(P0.shape)
```

```
[1, 36, 20, 20]
```

如上面的代码所示，可以由特征图C0生成特征图P0，P0的形状是[1,36,20,20]。每个小方块区域生成的锚框或者预测框的数量是3，物体类别数目是7，每个区域需要的预测值个数是3×(5+7)=36，正好等于P0的输出通道数

将P0[t,0:12,i,j]与输入的第t张图片上小方块区域(i,j)第1个预测框所需要的12个预测值对应，P0[t,12:24,i,j]与输入的第t张图片上小方块区域(i,j)第2个预测框所需要的12个预测值对应，P0[t,24:36,i,j]与输入的第t张图片上小方块区域(i,j)第3个预测框所需要的12个预测值对应

P0[t,0:4,i,j]与输入的第t张图片上小方块区域(i,j)第1个预测框的位置对应，P0[t,4,i,j]与输入的第t张图片上小方块区域(i,j)第1个预测框的objectness对应，P0[t,5:12,i,j]与输入的第t张图片上小方块区域(i,j)第1个预测框的类别对应。

如 图6 所示，通过这种方式可以巧妙的将网络输出特征图，与每个小方块区域生成的预测框对应起来了。

![](./imgs/9ea44b2c11f74f1484ab2bdc93be4008008cdee0b8d34dcb97bc9f89af935d1c.png)

> 特征图P0与候选区域的关联 


#### 计算预测框是否包含物体的概率

根据前面的分析，P0[t,4,i,j]与输入的第t张图片上小方块区域(i,j)第1个预测框的objectness对应，P0[t,4+12,i,j]与第2个预测框的objectness对应，…，则可以使用下面的程序将objectness相关的预测取出，并使用paddle.nn.functional.sigmoid计算输出概率

```python
NUM_ANCHORS = 3
NUM_CLASSES = 7
num_filters=NUM_ANCHORS * (NUM_CLASSES + 5)

backbone = DarkNet53_conv_body()
detection = YoloDetectionBlock(ch_in=1024, ch_out=512)
conv2d_pred = paddle.nn.Conv2D(in_channels=1024, out_channels=num_filters,  kernel_size=1)

x = np.random.randn(1, 3, 640, 640).astype('float32')
x = paddle.to_tensor(x)
C0, C1, C2 = backbone(x)
route, tip = detection(C0)
P0 = conv2d_pred(tip)

reshaped_p0 = paddle.reshape(P0, [-1, NUM_ANCHORS, NUM_CLASSES + 5, P0.shape[2], P0.shape[3]])
pred_objectness = reshaped_p0[:, :, 4, :, :]
pred_objectness_probability = F.sigmoid(pred_objectness)
print(pred_objectness.shape, pred_objectness_probability.shape)
```

```
[1, 3, 20, 20] [1, 3, 20, 20]
```
上面的输出程序显示，预测框是否包含物体的概率pred_objectness_probability，其数据形状是[1, 3, 20, 20]，与我们上面提到的预测框个数一致，数据大小在0～1之间，表示预测框为正样本的概率


#### 计算预测框位置坐标

P0[t,0:4,i,j]与输入的第ttt张图片上小方块区域(i,j)第1个预测框的位置对应，P0[t,12:16,i,j]与第2个预测框的位置对应，依此类推，则使用下面的程序可以从P0P0P0中取出跟预测框位置相关的预测值

```python
NUM_ANCHORS = 3
NUM_CLASSES = 7
num_filters=NUM_ANCHORS * (NUM_CLASSES + 5)

backbone = DarkNet53_conv_body()
detection = YoloDetectionBlock(ch_in=1024, ch_out=512)
conv2d_pred =  paddle.nn.Conv2D(in_channels=1024, out_channels=num_filters,  kernel_size=1)

x = np.random.randn(1, 3, 640, 640).astype('float32')
x = paddle.to_tensor(x)
C0, C1, C2 = backbone(x)
route, tip = detection(C0)
P0 = conv2d_pred(tip)


reshaped_p0 = paddle.reshape(P0, [-1, NUM_ANCHORS, NUM_CLASSES + 5, P0.shape[2], P0.shape[3]])
pred_objectness = reshaped_p0[:, :, 4, :, :]
pred_objectness_probability = F.sigmoid(pred_objectness)

pred_location = reshaped_p0[:, :, 0:4, :, :]
print(pred_location.shape)
```
```
[1, 3, 4, 20, 20]
```

网络输出值是(tx,ty,tw,th)，还需要将其转化为(x1,y1,x2,y2)这种形式的坐标表示。使用飞桨`paddle.vision.ops.yolo_box `API可以直接计算出结果，但为了给读者更清楚的展示算法的实现过程，我们使用Numpy来实现这一过程。


#### 计算物体属于每个类别概率

P0[t,5:12,i,j]与输入的第ttt张图片上小方块区域(i,j)第1个预测框包含物体的类别对应，P0[t,17:24,i,j]与第2个预测框的类别对应，依此类推，则使用下面的程序可以从P0P0P0中取出那些跟预测框类别相关的预测值。

```python
NUM_ANCHORS = 3
NUM_CLASSES = 7
num_filters=NUM_ANCHORS * (NUM_CLASSES + 5)

backbone = DarkNet53_conv_body()
detection = YoloDetectionBlock(ch_in=1024, ch_out=512)
conv2d_pred = paddle.nn.Conv2D(in_channels=1024, out_channels=num_filters,  kernel_size=1)

x = np.random.randn(1, 3, 640, 640).astype('float32')
x = paddle.to_tensor(x)
C0, C1, C2 = backbone(x)
route, tip = detection(C0)
P0 = conv2d_pred(tip)

reshaped_p0 = paddle.reshape(P0, [-1, NUM_ANCHORS, NUM_CLASSES + 5, P0.shape[2], P0.shape[3]])
# 取出与objectness相关的预测值
pred_objectness = reshaped_p0[:, :, 4, :, :]
pred_objectness_probability = F.sigmoid(pred_objectness)
# 取出与位置相关的预测值
pred_location = reshaped_p0[:, :, 0:4, :, :]
# 取出与类别相关的预测值
pred_classification = reshaped_p0[:, :, 5:5+NUM_CLASSES, :, :]
pred_classification_probability = F.sigmoid(pred_classification)
print(pred_classification.shape)
```

```
[1, 3, 7, 20, 20]
```
上面的程序通过P0P0P0计算出了预测框包含的物体所属类别的概率，pred_classification_probability的形状是[1,3,7,20,20]，数值在0~1之间

了解了检测模型的backbone、neck、head3个部分，接下来定义YOLOv3的模型，同时添加模型预测代码get_pred，通过网络输出计算出预测框位置和所属类别的得分，推荐大家直接使用`paddle.vision.ops.yolo_box`获得P0、P1、P2三个层级的特征图对应的预测框和得分，并将他们拼接在一块，即可得到所有的预测框及其属于各个类别的得分，关键参数含义如下

> paddle.vision.ops.yolo_box(x, img_size, anchors, class_num, conf_thresh, downsample_ratio, clip_bbox=True, name=None, scale_x_y=1.0)


- x，网络输出特征图，例如上面提到的P0或者P1、P2。
- img_size，输入图片尺寸。
- anchors，使用到的anchor的尺寸，如[10, 13, 16, 30, 33, 23, 30, 61, 62, 45, 59, 119, 116, 90, 156, 198, 373, 326]
- class_num，物体类别数。
- conf_thresh, 置信度阈值，得分低于该阈值的预测框位置数值不用计算直接设置为0.0。
- downsample_ratio, 特征图的下采样比例，例如P0是32，P1是16，P2是8。
- name=None，名字，例如’yolo_box’，一般无需设置，默认值为None。

返回值包括两项，boxes和scores，其中boxes是所有预测框的坐标值，scores是所有预测框的得分。


预测框得分的定义是所属类别的概率乘以其预测框是否包含目标物体的objectness概率，即

```math
score = P_{obj} \cdot P_{classification}
```

#### 损失函数

上面从概念上将输出特征图上的像素点与预测框关联起来了，那么要对神经网络进行求解，还必须从数学上将网络输出和预测框关联起来，也就是要建立起损失函数跟网络输出之间的关系。下面讨论如何建立起YOLOv3的损失函数。

对于每个预测框，YOLOv3模型会建立三种类型的损失函数：

- 表征是否包含目标物体的损失函数，通过pred_objectness和label_objectness计算。

```
 loss_obj = paddle.nn.fucntional.binary_cross_entropy_with_logits(pred_objectness, label_objectness)
```

- 表征物体位置的损失函数，通过pred_location和label_location计算。

```
  pred_location_x = pred_location[:, :, 0, :, :]
  pred_location_y = pred_location[:, :, 1, :, :]
  pred_location_w = pred_location[:, :, 2, :, :]
  pred_location_h = pred_location[:, :, 3, :, :]
  loss_location_x = paddle.nn.fucntional.binary_cross_entropy_with_logits(pred_location_x, label_location_x)
  loss_location_y = paddle.nn.fucntional.binary_cross_entropy_with_logits(pred_location_y, label_location_y)
  loss_location_w = paddle.abs(pred_location_w - label_location_w)
  loss_location_h = paddle.abs(pred_location_h - label_location_h)
  loss_location = loss_location_x + loss_location_y + loss_location_w + loss_location_h
```

- 表征物体类别的损失函数，通过pred_classification和label_classification计算。

```
loss_obj = paddle.nn.fucntional.binary_cross_entropy_with_logits(pred_classification, label_classification)
```