
### Yolov5 （2021）

> 没有特殊说明情况下，本文默认描述的是 P5 模型。

**数据处理**

- Mosaic(马赛克数据增强和透视)数据增强。Yolov5的输入端采用了和Yolov4一样的Mosaic数据增强的方式

  其中 Mosaic 数据增强概率为 1，表示一定会触发，而对于 small 和 nano 两个版本的模型不使用 MixUp，其他的 l/m/x 系列模型则采用了 0.1 的概率触发 MixUp。小模型能力有限，一般不会采用 MixUp 等强数据增强策略。

- HSV 增强：随机改变图像的色调、饱和度和值
- 随机水平翻转一种水平随机翻转图像的增强方法



**自适应锚框计算**

在Yolo算法中，针对不同的数据集，都会有初始设定长宽的锚框。

在网络训练中，网络在初始锚框的基础上输出预测框，进而和真实框groundtruth进行比对，计算两者差距，再反向更新，迭代网络参数。

```
  anchors: [[10, 13], [16, 30], [33, 23],   #  P3/8
            [30, 61], [62, 45], [59, 119],   # P4/16
            [116, 90], [156, 198], [373, 326]]  # P5/32  w,h
```

**SiLU 激活函数**

‌SiLU（Sigmoid Linear Unit）激活函数是一种结合了Sigmoid和线性变换的平滑非线性函数，其公式为SiLU(x)=x⋅σ(x)，其中σ(x)是Sigmoid函数。‌它被广泛应用于深度学习模型（如YOLOv5）中，因其平滑性、可微性和对负值的非零响应优于ReLU等传统激活函数


**架构图**

YOLOv5-P5模型: 3个输出层P3， P4， P5在步长(缩放倍数)8,16,32。输入尺寸为640

![](./imgs/200000324-70ae078f-cea7-4189-8baa-440656797dad.jpg)
<center>图 1：YOLOv5-l-P5 模型结构</center> 
<br>

YOLOv5-P6大尺度模型：4个输出层P3、P4、P5、P6，步长8,16,32,64。输入尺寸为1280

![](./imgs/211143533-1725c1b2-6189-4c3a-a046-ad968e03cb9d.jpg)
<p align="center">图 2：YOLOv5-l-P6 模型结构</p> 

如图 1 和 2 所示，YOLOv5 的 P5 和 P6 版本主要差异在于网络结构和图片输入分辨率。其他区别，如 anchors 个数和 loss 权重可详见配置文件。


![](./imgs/v2-ff8d2fd62484923f1cbc53605d3c7156_r.png)

**backbone**
主干网络 CSPDarkNet (Conv、C3、SPPF) 输入[4, 3, 640, 640] 返回其特征映射的阶段的索引 [2, 3, 4]


在最新的YOLOv5中(p5/p6)

- Stem Layer 是 1 个 （k=6, s=2, p=2） 的 ConvModule，相较于 v6.1 版本之前的 Focus 模块更加高效
- 新的SPPF(快速PPF。只有单个spp内核大小)层取代SPP层以减少操作
- 将P3骨干层C3重复次数从9次减少到6次，以提高速度
- 重新排序将SPPF置于主干的末端
- 在最后的C3骨干层重新引入shortcut 

YOLOv5 网络结构大小由 deepen_factor(depth_mult) 和 widen_factor(width_mult) 两个参数决定。其中 deepen_factor 控制网络结构深度，即 CSPLayer 中 DarknetBottleneck 模块堆叠的数量；widen_factor 控制网络结构宽度，即模块输出特征图的通道数。以 YOLOv5-l 为例，其 deepen_factor = widen_factor = 1.0 。P5 和 P6 的模型整体结构分别如图 1 和图 2 所示


- 除了最后一个 Stage Layer，其他均由 1 个 ConvModule 和 1 个 CSPLayer 组成。如上图 Details 部分所示。 其中 ConvModule 为 3x3的 Conv2d + BatchNorm + SiLU 激活函数。CSPLayer 即 YOLOv5 官方仓库中的 C3 模块，由 3 个 ConvModule + n 个 DarknetBottleneck(带残差连接) 组成。

- 最后一个 Stage Layer 在最后增加了 SPPF 模块。SPPF 模块是将输入串行通过多个 5x5 大小的 MaxPool2d 层，与 SPP 模块效果相同，但速度更快。

- P5 模型会在 Stage Layer 2-4 之后分别输出一个特征图进入 Neck 结构。以 640x640 输入图片为例，其输出特征为 (B,256,80,80)、(B,512,40,40) 和 (B,1024,20,20)，对应的 stride 分别为 8/16/32。

- P6 模型会在 Stage Layer 2-5 之后分别输出一个特征图进入 Neck 结构。以 1280x1280 输入图片为例，其输出特征为 (B,256,160,160)、(B,512,80,80)、(B,768,40,40) 和 (B,1024,20,20)，对应的 stride 分别为 8/16/32/64。


**neck**


CSP-PAN 

Neck 模块输出的特征图和 Backbone 完全一致。
即 
P5 模型为 (B,256,80,80)、 (B,512,40,40) 和 (B,1024,20,20)；
P6 模型为 (B,256,160,160)、(B,512,80,80)、(B,768,40,40) 和 (B,1024,20,20)


**head**

前面的 neck 依然是输出 3 个不同尺度的特征图，shape 为 (B,256,80,80)、 (B,512,40,40) 和 (B,1024,20,20)。 由于 YOLOv5 是非解耦输出，即分类和 bbox 检测等都是在同一个卷积的不同通道中完成。以 COCO 80 类为例：

- P5 模型在输入为 640x640 分辨率情况下，其 Head 模块输出的 shape 分别为 (B, 3x(4+1+80),80,80), (B, 3x(4+1+80),40,40) 和 (B, 3x(4+1+80),20,20)

- P6 模型在输入为 1280x1280 分辨率情况下，其 Head 模块输出的 shape 分别为 (B, 3x(4+1+80),160,160), (B, 3x(4+1+80),80,80), (B, 3x(4+1+80),40,40) 和 (B, 3x(4+1+80),20,20)

> 其中 3 表示 3 个 anchor，4 表示 bbox 预测分支，1 表示 obj 预测分支，80 表示 COCO 数据集类别预测分支。


#### 正负样本匹配策略


正负样本匹配策略的核心是确定预测特征图的所有位置中哪些位置应该是正样本，哪些是负样本，甚至有些是忽略样本。 匹配策略是目标检测算法的核心，一个好的匹配策略可以显著提升算法性能。

YOLOV5 的匹配策略简单总结为：**采用了 anchor 和 gt_bbox 的 shape 匹配度作为划分规则，同时引入跨邻域网格策略来增加正样本**。 其主要包括如下两个核心步骤：

- 对于任何一个输出层，抛弃了常用的基于 Max IoU 匹配的规则，而是直接采用 shape 规则匹配，也就是该 GT Bbox 和当前层的 Anchor 计算宽高比，如果宽高比例大于设定阈值，则说明该 GT Bbox 和 Anchor 匹配度不够，将该 GT Bbox 暂时丢掉，在该层预测中该 GT Bbox 对应的网格内的预测位置认为是负样本

- 对于剩下的 GT Bbox(也就是匹配上的 GT Bbox)，计算其落在哪个网格内，同时利用四舍五入规则，找出最近的两个网格，将这三个网格都认为是负责预测该 GT Bbox 的，可以粗略估计正样本数相比之前的 YOLO 系列，至少增加了三倍


**生成Anchor**
在yolo系列模型中，大多数情况下使用默认的anchor设置即可, 你也可以运行`tools/anchor_cluster.py`来得到适用于你的数据集Anchor，使用方法如下：
``` bash
python tools/anchor_cluster.py -c configs/ppyolo/ppyolo.yml -n 9 -s 608 -m v2 -i 1000
```
目前`tools/anchor_cluster.py`支持的主要参数配置如下表所示：

|    参数    |    用途    |    默认值    |    备注    |
|:------:|:------:|:------:|:------:|
| -c/--config | 模型的配置文件 | 无默认值 | 必须指定 |
| -n/--n | 聚类的簇数 | 9 | Anchor的数目 |
| -s/--size | 图片的输入尺寸 | None | 若指定，则使用指定的尺寸，如果不指定, 则尝试从配置文件中读取图片尺寸 |
|  -m/--method  |  使用的Anchor聚类方法  |  v2  |  目前只支持yolov2的聚类算法  |
|  -i/--iters  |  kmeans聚类算法的迭代次数  |  1000  | kmeans算法收敛或者达到迭代次数后终止 |

**Bbox 编解码过程**

在 Anchor-based 算法中，预测框通常会基于 Anchor 进行变换，然后预测变换量，这对应 GT Bbox 编码过程，而在预测后需要进行 Pred Bbox 解码，还原为真实尺度的 Bbox，这对应 Pred Bbox 解码过程。

在 YOLOv3 中，回归公式为:

```math
\begin{split}b_x=\sigma(t_x)+c_x  \\
b_y=\sigma(t_y)+c_y  \\
b_w=a_w\cdot e^{t_w} \\
b_h=a_h\cdot e^{t_h} \\\end{split}
```

> $a_w$ 代表 Anchor 的宽度, $c_x$ 代表 Grid 所处的坐标, $\sigma$ 代表 Sigmoid 公式。

而在 YOLOv5 中，回归公式为:

```math
\begin{split}b_x=(2\cdot\sigma(t_x)-0.5)+c_x   \\
b_y=(2\cdot\sigma(t_y)-0.5)+c_y   \\
b_w=a_w\cdot(2\cdot\sigma(t_w))^2   \\
b_h=a_h\cdot(2\cdot\sigma(t_h))^2\end{split}
```

改进之处主要有以下两点
- 中心点坐标范围从 (0, 1) 调整至 (-0.5, 1.5)
- 宽高范围从 $(0，+\infty)$  调整至 $(0，4a_{wh})$

这个改进具有以下好处：

新的中心点设置能更好的预测到 0 和 1。这有助于更精准回归出 box 坐标

![](./imgs/190546778-83001bac-4e71-4b9a-8de8-bd41146495af.png)


宽高回归公式中 exp(x) 是无界的，这会导致梯度失去控制，造成训练不稳定。YOLOv5 中改进后的宽高回归公式优化了此问题。

![](./imgs/190546793-5364d6d3-7891-4af3-98e3-9f06970f3163.png)


**匹配策略**

无论网络是 Anchor-based 还是 Anchor-free，**我们统一使用 prior 称呼 Anchor**


正样本匹配包含以下两步：

- **“比例”比较**

将 GT Bbox 的 WH 与 Prior 的 WH 进行“比例”比较。

```math
r_w = w_{gt} / w_{pt} \\
r_h = h_{gt} / h_{pt}  \\
r_w^{max}=max(r_w, 1/r_w)  \\
r_h^{max}=max(r_h, 1/r_h)  \\
r^{max}=max(r_w^{max}, r_h^{max})  \\
if  r_{max} < prior-match-thr:   match!
``` 

此处我们用一个 GT Bbox 与 P3 特征图的 Prior 进行匹配的案例进行讲解和图示：

![](./imgs/190547195-60d6cd7a-b12a-4c6f-9cc8-13f48c8ab1e0.png)

prior1 匹配失败的原因是 $h\_{gt}\ /\ h\_{prior}\ =\ 4.8\ >\ priormatchthr$

- **为步骤 1 中 match 的 GT 分配对应的正样本**

依然沿用上面的例子：

GT Bbox (cx, cy, w, h) 值为 (26, 37, 36, 24)，

Prior WH 值为 [(15, 5), (24, 16), (16, 24)]，在 P3 特征图上，stride 为 8。通过计算，prior2 和 prior3 能够 match。

计算过程如下：

将 GT Bbox 的中心点坐标对应到 P3 的 grid 上

```math
GT_x^{center\_grid}=26/8=3.25  
```
```math
GT_y^{center\_grid}=37/8=4.625
```

![](./imgs/190549304-020ec19e-6d54-4d40-8f43-f78b8d6948aa.png)


将 GT Bbox 中心点所在的 grid 分成四个象限，由于中心点落在了左下角的象限当中，那么会将物体的左、下两个 grid 也认为是正样本

![](./imgs/190549310-e5da53e3-eae3-4085-bd0a-1843ac8ca653.png)

下图展示中心点落到不同位置时的正样本分配情况：

![](./imgs/190549613-eb47e70a-a2c1-4729-9fb7-f5ce7007842b.png)

```
    ...
    gxy = t[:, 2:4]  # grid xy
    gxi = gain[[2, 3]] - gxy  # inverse
    # j 表示x小于0.5 gt样本左边grid可以选择为正样本（pos）
    # k 表示小于0.5，gt样本上边grid可以选择为正样本（pos）
    j, k = ((gxy % 1 < g) & (gxy > 1)).T  
    # 反转后的坐标
    # l 表示gt样本右边grid可以选择为正样本（pos）
    # m 表示gt样本下边grid可以选择为正样本（pos）
    l, m = ((gxi % 1 < g) & (gxi > 1)).T
    # gt bbox 所在的中心、及选取的左、上、右、下 grid 
    j = np.stack((np.ones_like(j), j, k, l, m))
    t = np.tile(t, [5, 1, 1])[j]
    offsets = (np.zeros_like(gxy)[None] + self.off[:, None])[j]
  else:
    t = targets_labels[0]
    offsets = 0  

  # Define
  b, c = t[:, :2].astype(np.int64).T  # image, class
  gxy = t[:, 2:4]  # grid xy
  gwh = t[:, 4:6]  # grid wh
  gij = (gxy - offsets).astype(np.int64)
  gi, gj = gij.T  # grid xy indices




# self.off  偏移量
array([[ 0. ,  0. ],
       [ 0.5,  0. ],
       [ 0. ,  0.5],
       [-0.5,  0. ],
       [ 0. , -0.5]], dtype=float32)
```

那么 YOLOv5 的 Assign 方式具体带来了哪些改进？
- 一个 GT Bbox 能够匹配多个 Prior
- 一个 GT Bbox 和一个Prior 匹配时，能分配 1-3 个正样本
- 以上策略能适度缓解目标检测中常见的正负样本不均衡问题。


而 YOLOv5 中的回归方式，和 Assign 方式是相互呼应的：

1、中心点回归方式

![](./imgs/190549684-21776c33-9ef8-4818-9530-14f750a18d63.png)

2、WH 回归方式：

![](./imgs/190549696-3da08c06-753a-4108-be47-64495ea480f2.png)


#### loss

YOLOv5 中总共包含 3 个 Loss，分别为：

- Classes loss：使用的是 BCE loss
- Objectness loss：使用的是 BCE loss
- Location loss：使用的是 CIoU loss


BCEWithLogitsLoss (sigmoid + BCELoss)


```
>>> logit = paddle.to_tensor([5.0, 1.0, 3.0], dtype="float32")
>>> label = paddle.to_tensor([1.0, 0.0, 1.0], dtype="float32")
>>> bce_logit_loss = paddle.nn.BCEWithLogitsLoss()
>>> output = bce_logit_loss(logit, label)
>>> print(output)
Tensor(shape=[], dtype=float32, place=Place(cpu), stop_gradient=True,
0.45618808)
# 计算过程
s = paddle.nn.Sigmoid()
>>> s(logit)
Tensor(shape=[3], dtype=float32, place=Place(gpu:0), stop_gradient=True,
   [0.99330717, 0.73105854, 0.95257413])
o1 = 1*math.log(0.99330717) + (1-1)* ln(1-0.99330717) = -0.42159449003804794
o2 = 0*ln(0.73105854) + (1-0)*math.log(1-0.73105854) = -1.313261543880988
o3 = 1*math.log(0.95257413) + (1-1)* ln(1-0.95257413) = -0.04858734823797353
out = -(o1+o2+o3) /3 = 0.45618807318093607
```


三个 loss 按照一定比例汇总：

```math
Loss=\lambda_1L_{cls}+\lambda_2L_{obj}+\lambda_3L_{loc}
```

P3、P4、P5 层对应的 Objectness loss 按照不同权重进行相加，默认的设置是
```
obj_level_weights=[4., 1., 0.4]
```

```math
L_{obj}=4.0\cdot L_{obj}^{small}+1.0\cdot L_{obj}^{medium}+0.4\cdot L_{obj}^{large}
```

####  yolov5u
YOLOv5结构使用YOLOv8的head和loss，是Anchor Free的检测方案

####  yolov5_seg (2022.11)

yolov5_seg 是yolov5 7.0 版本的一个实例分割模型


### yolov6(2022)

YOLOv6 是美团视觉智能部研发的一款目标检测框架，致力于工业应用。

官方论文:

- [YOLOv6 v3.0: A Full-Scale Reloading （2023） 🔥](https://arxiv.org/abs/2301.05586)
- [YOLOv6: A Single-Stage Object Detection Framework for Industrial Applications](https://arxiv.org/abs/2209.02976)


**骨干网络**

![](./imgs/yolov6_x2.png)
> YOLOv6 框架（显示了 N 和 S）。对于 M/L，RepBlocks 被替换为 CSPStackRep
- 在Backbone方面，YOLOv6在小规模模型（n/t/s模型）采用RepBlock进行构建(EfficientRep)；对于大规模模型（m/l模型）采用CSPStackRepBlock进行构建；
- 在Neck方面，YOLOv6延续了YOLOv4与YOLOv5的设计思想，依旧使用的是PAN-FPN架构，同时采用RepBlock（n/t/s模型）与CSPStackRepBlock（m/l模型）并相应调整宽度和深度。YOLOv6 的颈部被称为 Rep-PAN。
- 在Head方面，对Decoupled Head进行改进，最终使用Efficient Decouple Head；
- YOLOv6 l 模型默认激活函数为silu(Conv 与 SiLU 在精度上表现最佳)，其余 n s m 模型则默认为relu(RepConv 与 ReLU 的组合实现了更好的权衡)。我们选择在 YOLOv6-N/T/S/M 中使用 RepConv/ReLU 组合以获得更高的推理速度，并在大型模型 YOLOv6-L 中使用 Conv/SiLU 组合以加速训练并提升性能
- YOLOv6 n t模型训练默认使用siou loss，其余s m l模型则默认使用giou loss

![](./imgs/20250611113816.png)

> (a) RepBlock 由带有 ReLU 激活的 RepVGG 块堆叠组成。
> (b) 在推理时，RepVGG 块转换为 RepConv。
> (c) CSPStackRep Block 包含三个 1 × 1 卷积层，以及 ReLU 激活后的双 RepConv 子块堆叠，并带有残差连接

SPP

![](./imgs/20250611180426.png)

> 依次是SPP, SPPF,以及SimSPPF

**Efficient decoupled head**

YOLOv5 的检测头是一个参数在分类和定位分支之间共享的耦合头，而 FCOS[41]和 YOLOX[7]中的对应部分则将两个分支解耦，并在每个分支中引入了两个 3x3 卷积层来提升性能

在 YOLOv6 中，我们采用混合通道策略来构建一个更高效的解耦头。具体来说，我们将中间的3×3卷积层减少到仅 1 个。头的宽度由骨干网络和颈部的宽度倍数共同缩放。这些修改进一步降低了计算成本，实现了更低的推理延迟。

**Probability Loss 概率损失**

分布焦点损失 (DFL) 将框位置的基本连续分布简化为离散概率分布。它考虑了数据中的模糊性和不确定性，而未引入任何其他强先验，这有助于提高框定位精度，尤其是在真实框的边界模糊时。基于 DFL，DFLv2 [19] 开发了一个轻量级子网络，以利用分布统计与实际定位质量之间的紧密相关性，从而进一步提升检测性能。然而，DFL 通常比一般框回归输出多 17 个回归值，导致显著的额外开销。额外的计算成本严重阻碍了小模型的训练。而 DFLv2 由于额外的子网络，进一步增加了计算负担。在我们的实验中，DFLv2 在我们的模型上带来的性能提升与 DFL 相似。因此，我们在 YOLOv6-M/L 中仅采用 DFL。

![](./imgs/20250612151922.png)


#### 正负样本匹配与损失函数

**TaskAligned样本匹配**

在YOLOv6的早期版本中使用了SimOTA作为标签分配方法。SimOTA 减少了额外的超参数并保持了性能，但是在实践中发现引入SimOTA会减慢训练过程。同时可能会使训练陷入不稳定。 之后，YOLOv6最新版本找到一个替代SimOTA的匹配方法，TaskAlign。

任务对齐学习（TAL）最初在 TOOD [ 5]中被提出，其中设计了一种统一的分类分数和预测框质量的度量标准。IoU 被该度量标准取代，用于分配对象标签。在一定程度上，任务错位（分类和bbox回归）的问题得到了缓解。

TOOD 的另一个主要贡献是关于任务对齐头（T-head）。T-head 堆叠卷积层来构建交互特征，在此基础上使用任务对齐预测器（TAP）。PP-YOLOE [ 45] 通过用轻量级的 ESE 注意力机制替换 T-head 中的层注意力机制来改进 T-head，形成了 ET-head。然而，我们发现 ET-head 会降低我们模型的推理速度，并且没有带来精度提升。因此，我们保留了我们高效解耦头的设计。

此外，我们观察到 TAL 能够比 SimOTA 带来更多的性能提升，并稳定训练。因此，我们在 YOLOv6 中采用 TAL 作为默认的标签分配策略

此外，TOOD [ 5] 的实现采用 ATSS [ 51] 作为早期训练 epoch 中的预热标签分配策略。我们也保留了预热策略，并对其进行了进一步的探索。
```math
t = s^{\alpha} \times u^{\beta} 
```
> s 是分类得分，u是定位精度iou （pred_bboxes与gt_bboxes）
>  $\alpha$ 和 $\beta$ 为权重超参

- 计算所有pred bbox（所有金字塔级别的bbox）和gt之间的对齐度量（alignment metric）
    ```
    alpha: 1.0
    beta: 6.0
    # compute alignment metrics, [B, n, L]
    alignment_metrics = bbox_cls_scores.pow(self.alpha) * ious.pow(
            self.beta)
    ```
- 选择top-k alignment metrics bbox作为每个gt的候选项
- 将阳性样品的中心（anchor_points）限制在gt bbox中（因为无锚检测器）只能预测正距离)
- 如果一个锚框被分配给多个gts，则具有最高的分数将被选中。

**VFL Loss 分类损失函数**

```math

VFL(p,q) = \left\{ 
    \begin{matrix} 
    -q(qlog(p) + (1-q)log(1-p))&& q >0 \\
    -{\alpha}p^{\gamma}log(1-p) && q=0 \\
    \end{matrix} \right\}
```

q是label，正样本时候q为bbox和gt的IoU，负样本时候q=0，当为正样本时候其实没有采用FL，而是普通的BCE，只不过多了一个自适应IoU加权，用于突出主样本。而为负样本时候就是标准的FL了。可以明显发现VFL比QFL更加简单，主要特点是正负样本非对称加权、突出正样本为主样本。

```
weight = alpha * pred_score.pow(gamma) * (1 - label) + gt_score * label
loss = F.binary_cross_entropy(
    pred_score, gt_score, weight=weight, reduction='sum')
return loss
```

- pred_score 为预测相关anchor是相关类别的得分
- gt_score   对于训练中的正样本，设置为生成的bbox和gt box之间的IoU（gt IoU）。而对于训练中的负样本，所有类别的训练目标均为0
- label 类别one_hot编码


**SIOU 损失**

IOU: 预测框与目标框之间的重叠程度
GIOU: 在IOU的基础上通过引入预测框和真实框的最小外接矩形。（不仅关注重叠区域，还关注其他的非重合区域）
DIOU: DIOU在IoU的基础上直接回归两个框中心点的欧式距离,DIOU的惩罚项是基于中心点的距离和对角线距离(同时包含预测框和真实框的最小闭包区域的对角线距离)的比值.
CIOU: 在DIOU的基础上添加了长宽比的惩罚项

SIoU 损失函数通过引入了所需回归之间的向量角度，重新定义了距离损失，有效降低了回归的自由度，加快了网络模型的收敛，并且在小规模模型（n/t/s模型）上可以一定程度上提升精度。

YOLOv6对小模型采用SIoU损失，大模型采用GIoU损失。


**DFL损失**

这里的DFL（Distribution Focal Loss），其主要是将框的位置建模成一个 general distribution，让网络快速的聚焦于和目标位置距离近的位置的分布。

![](./imgs/3dafec3f7d834cc89b0b5557a6e4d1c6.png)

```math
DFL(S_i, S_{i+1}) = -((y_{i+1}-y)log(S_i) + (y-y_i)log(S_{i+1}))
```

> yi和 yi+1是浮点值 y 的左右整数值，S是输出分布，长度为17；
> DFL 能够让网络更快地聚焦于目标 y 附近的值，增大它们的概率；
> DFL的含义是以交叉熵的形式去优化与标签y最接近的一左一右2个位置的概率，从而让网络更快的聚焦到目标位置的邻近区域的分布；
> 也就是说学出来的分布理论上是在真实浮点坐标的附近，并且以线性插值的模式得到距离左右整数坐标的权重。

![](./imgs/f6f0b72ca825491987f5324a95e5ebed.png)

**YOLOv6 v3.0的主要贡献简述如下**
- 对检测器的Neck部件进行了翻新：引入BiC(Bi-directional Concatenation)提供更精确的定位信息；将SPPF简化为SimCSPSPPF，牺牲较少的速度提升更多的性能。（SimCSPSPPF 模块被引入 YOLOv6-N/S。对于 YOLOv6-M/L，采用 SimSPPF 模块。）
- 提出一种AAT(Anchor-aided training)策略，在不影响推理效率的情况下同时受益于Anchor-basedAnchor-free设计理念。
- 对YOLOv6的Backbone与Neck进行加深，在更高分辨率输入下达成新的SOTA性能
- 提出一种新的自蒸馏策略提升YOLOv6小模型的性能，训练阶段采用更大的DFL作为增强版辅助回归分支。

![](./imgs/x2.png)
![](./imgs/yolov6_x3.png)

> (a) YOLOv6 的颈部结构（N 和 S 所示）。注意对于 M/L，RepBlocks 被替换为 CSPStackRep
> (b) 使用双向拼接（BiC）模块更新检测器的颈部，以提供更精确的位置信号
> (c) SPPF [ 5] 被简化为 SimCSPSPPF 模块，该模块在几乎不降低速度的情况下带来了性能提升。 
> SimCSPSPPF的激活函数为relu, CSPSPPF的激活函数为silu

**网络设置**

在实际应用中，多尺度特征融合已被证明是目标检测中关键且有效的组成部分。
特征金字塔网络（FPN）通过自顶向下的路径聚合高层语义特征和低层特征，从而提供更精确的位置定位。随后，出现了多项关于双向 FPN 的研究，旨在增强层次化特征表示能力。
PANet在 FPN 基础上增加了一条额外的自底向上路径，以缩短低层和高层特征的信息路径，从而促进从低层特征传播精确信号。
BiFPN引入了可学习的权重用于不同输入特征，并简化了 PAN，以实现高效的高性能。
PRB-FPN通过并行 FP 结构实现双向融合及相关改进，保留了高质量特征以实现精确位置定位。

受上述工作的启发，我们设计了一种增强型 PAN 作为我们的检测颈。为了在不引入过多计算负担的情况下增强定位信号，我们提出了一种双向拼接（BiC）模块，用于整合三个相邻层的特征图，将骨干网络 $c_{i-1}$的一个额外低级特征融合到 $p_i$  中（图 2）。**在这种情况下，可以保留更精确的定位信号，这对小物体的定位非常重要**


**Anchor-Aided Training （基于锚点的训练）**

YOLOv6 是一种无锚点检测器，旨在追求更高的推理速度。然而，我们通过实验发现，与无锚点检测器相比，在相同设置下，基于锚点的范式为 YOLOv6-N 带来了额外的性能提升，如表 1 所示。此外，基于锚点的 ATSS [ 18]被用作 YOLOv6 早期版本中的预热标签分配策略，从而稳定了训练。

![](./imgs/20250611085053.png)


基于此，我们提出了辅助锚点训练（AAT），其中引入了基于锚点的辅助分支，以结合基于锚点和无锚点范式的优势。这些辅助分支应用于分类头和回归头。图 3 展示了带辅助分支的检测头。

![](./imgs/20250611085302.png)

> 训练期间带基于锚点的辅助分支的检测头。推理时移除辅助分支。‘af’和‘ab’分别代表‘无锚点’和‘基于锚点’。

在训练阶段，辅助分支和锚点无关分支从独立的损失中学习，同时信号被整体传播。因此，辅助分支的额外嵌入引导信息被整合到主要的锚点无关头部中。值得一提的是，在推理时移除了辅助分支，这提升了准确率性能而不降低速度。


**Self-distillation (自我蒸馏)**


在 YOLOv6 的早期版本中，自我蒸馏仅在大型模型（即 YOLOv6-M/L）中引入，通过最小化教师模型和学生模型在类别预测之间的 KL 散度来应用原味知识蒸馏技术。同时，采用 DFL 作为回归损失，对边界框回归进行自我蒸馏。

知识蒸馏损失的表达式为：

```math
L_{KD} = KL(p_t^{cls} || p_s^{cls}) + KL(p_t^{reg} || p_s^{reg}) \\
L_{total} = L_{det} + \alpha L_{KD}

```

其中 $p_t^{cls}$ 和 $p_s^{cls}$ 分别是教师模型和学生模型的类别预测，相应地 $p_t^{reg}$ 和 $p_s^{reg}$ 是边界框回归预测

其中 $L_{det}$ 是使用预测和标签计算出的检测损失。引入超参数 
α来平衡两种损失。在训练的早期阶段，教师生成的软标签更容易学习。随着训练的进行，学生的性能将匹配教师，因此硬标签将更有助于学生。基于此，我们对 α 应用余弦权重衰减，以动态调整来自硬标签和教师软标签的信息。 
α 的公式为：

```math
\alpha=-0.99*((1-cos(\pi*E_{i}/E_{max}))/2)+1,
```

![](./imgs/a_1.png)

> 其中 $E_i$ 表示当前训练的轮次， $E_{max}$ 代表最大训练轮次

由于DFL会对回归分支引入额外的参数，极大程度影响小模型的推理速度。因此，作者针对小模型设计了一种DLD(Decoupled Localization Distillation)以提升性能且不影响推理速度。具体来说，在小模型中插入一个增强版回归分支作为辅助。在自蒸馏阶段，小模型受普通回归分支与增强回归分支加持，老师模型近使用辅助分支。需要注意：普通分支仅采用硬标签进行训练，而辅助分支则用硬标签与源自老师模型的软标签进行训练。完成蒸馏后，仅普通分支保留，辅助分支被移除。这种训练策略又是一种加量不加价的"赠品"。



### yolov7（2022）

Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors


YOLOV7 是 YOLOV4 的原班人马于 2022 年提出的最新的 YOLO 版本。 YOLOv7 的在速度和精度上的表现也优于 YOLOR、YOLOX、Scaled-YOLOv4、YOLOv5、DETR 等多种目标检测器

![](./imgs/78f12a93ddae30aa52221b4fecc37208.jpg)


**YOLOV7 整体网络结构**
YOLOV7 跟 V4、V5 的结构差不多，依然是 Backbone+Neck+Head

![](./imgs/c4b4ca6c334d1f45ea3c052fa0d79d3e.png)

在 Backbone 中，输入的图像会先经过 4 个普通卷积 CBS (Conv2D+BatchNorm+SiLu)，这 4 个 CBS 都是 3*3 的卷积核，它们的不同在于橙色的 CBS 步长为 1，不会改变特征图的尺寸；而褐色的 CBS 步长为 2，会进行下采样；YOLOV5 只有两个普通卷积 CBS

#### ELAN
YOLOV5 在进一步的 Backbone 中使用的是 CSPLayer（C3） 结构，V7 中改成了 ELAN 结构 + MP 结构

扩展高效层聚合网络(efficient layer aggregation networks,ELAN) ELAN 结构

![](./imgs/6214fa2ec5eccf514d246f506749722b.png)

![](./imgs/20250616171133.png)

> Extended efficient layer aggregation networks, E-ELAN

通过控制最短最长的梯度路径，更深的网络可以有效地学习和收敛。ELAN 由多个 CBS 构成，其输入输出特征大小保持不变，通道数在开始的两个 CBS 会有变化， 后面的几个输入通道都是和输出通道保持一致的，经过最后一个 CBS 输出为需要的通道。上图中粉色的 CBS 是 1*1 的卷积核，橙色的 CBS 是 3*3 的卷积核。经过 concat 输出的是 2c。

#### MP-1 结构

![](./imgs/03bcf1dd5339d6db561b0a63b26df1e5.png)

这里就是使用了最大池化 (上层) 和步长为 2 的 CBS (下层) 同时进行降采样，通道数通过 concat 合并后 MP1 前后保持不变

#### SPPCSPC 结构

YOLOV7 的 Backbone 最深层的网络输出的特征图会经过一个叫 SPPCSPC 的结构再输入到 Neck 中，YOLOV5 中则是 SPPF 的结构

![](./imgs/2599ec281dfe4aef97f66461c49a76cd.png)

上图中首先会通过两个 1x1 的 CBS 分成两个通路，上面的通路会再接一个 3x3 的 CBS，再 1x1 的 CBS。YOLOV5 的 SPPF 中只有一个 CBS 就接最大池化了。YOLOV7 的最大池化改回了 YOLOV4 的结构，使用的是最大池化核数 5、9、13 并行的结构，而 YOLOV5 的 SPPF 使用的是 5x5 的最大池化串行的结构


**Neck 部分**

YOLOV7 依然是一个分层输出的特征金字塔结构。Backbone 在第 2、3、4 个 ELAN 后进行特征分层输出。Neck 部分依然采用的是 PAN 的双向特征融合，从深层到浅层进行上采样，再从浅层到深层进行下采样。PAN 的上采样部分主要有 CBS 普通卷积，UpSample 反卷积和 ELAN-W 的结构

PAN 的下采样部分包括 ELAN-W 和 MP-2 两种结构
#### ELAN-W 结构

![](./imgs/aa8bcc6cb4ec53362fbe831d936ca983.png)

LAN-W 跟 ELAN 基本上是一样的，但是它的 concat 合并是 6 层合并，ELAN 是 4 层合并

MP-2 结构和 MP-1 结构是一样的，它们的区别在于输出通道数不同，MP-2 的输出通道数是 MP-1 的 2 倍

**Head 部分**

YOLOV7 的 Head 部分也是三个检测头，对不同尺度的特征图进行坐标预测和分类。

相比于 YOLOV5 的 PAN 每一层的直接输出，YOLOV7 用到了现今比较流行的重参的 REP 结构。

#### REP 结构

![](./imgs/ede598b28f47049e9bec421eb325bb9f.png)


REP 在部署和训练的时候结构不同。在训练的时候，如果输入输出通道数相同，则包含了第三层 BN 的直连通道，否则只有第一层的 1*1 卷积 + BN 以及第二层的 3*3 卷积 + BN，上面虽然画的是 CBS，但其实这里是没有激活函数 SiLu 的，只有三层相加才会被最后激活。在部署时，为了方便部署，会将分支的参数重参数化到主分支上，取 3*3 的主分支卷积输出，但这里是没有 BN 的，只有激活。所以上面这个图是存在歧义的，需要指出

#### 辅助训练模块(aux)

深度监督是一种常用于训练深度网络的技术，其主要概念是在网络的中间层增加额外的辅助头，以及在辅助损失为指导的浅层网络权重。即使对于像 ResNet 和 DenseNet 这样收敛效果好的网络结构，深度监督仍然可以显著提高模型在许多任务上的性能。

深度监督 (Deep Supervision) 又称为中继监督 (intermediate supervision），就是在深度神经网络的某些中间隐藏层加了一个辅助的分类器作为一种网络分支来对主干网络进行监督的技巧，其实就是在网络的中间部分添加了额外的 loss，跟多任务是有区别的，多任务有不同的 ground truth 计算不同的 loss，而深度监督的 ground truth 都是同一个 ground truth，不同位置的 loss 按系数求和。深度监督的目的是为了浅层能够得到更加充分的训练，解决深度神经网络训练梯度消失和收敛速度过慢等问题。

无论辅助head或lead head的情况如何，都需要针对目标进行深度监督训练。在开发软标签分配器相关技术的过程中，我们意外发现了一个新的衍生问题，即"如何将软标签分配给辅助head和lead head？"据我们所知，到目前为止，相关文献尚未探讨这一问题。目前最流行方法的结果如Fig5(c)所示，即分离辅助head和lead head，，然后使用它们各自的预测结果和gt来执行标签分配。本文所提方法是一种新的标签分配方法，通过lead head预测来指导辅助head和lead head。换句话说，我们使用lead head预测作为指导来生成从粗到细的分层标签，这些标签分别用于辅助head和lead head学习。Fig5(d)和(e)分别显示了两种所提深度监督标签分配策略。

![](./imgs/20250623100725.png)

上图中 a 是常见的目标检测网络结构，不包含深度监督。b 是包含了深度监督的目标检测器架构，这里最终输出的头称为引导头，用于辅助训练的头称为辅助头。在标签分配的问题中，过去在深度网络的训练中，标签分配通常直接指的是 ground truth，并根据指定的规则生成 hard label。近年来，研究者经常利用网络预测的质量分布来结合 ground truth，使用一些计算和优化方法来生成可靠的软标签 (soft label)。在本文中，作者将网络预测结果与 ground truth 一起考虑后再分配软标签的机制称为 "标签分配器"。无论辅助头或引导头，都需要对目标进行深度监督。进行软标签分配的方法如上图中 c 所示，将辅助头和引导头分离，然后利用它们各自的预测结果和 ground truth 执行标签分配。通过引导头的预测来引导辅助头以及自身。换句话说，首先使用引导头的 prediction 作为指导，生成从粗到细的层次标签，分别作用于辅助头和引导头的学习。


Coarse-to-fine lead guided label assigner (粗到细引导标签分配器):Coarse-to-fine 引导头使用到了自身的 prediction 和 ground truth 来生成软标签，引导标签进行分配。然而在这个过程中，作者生成了两组不同的软标签，即粗标签和细标签。其中细标签与引导头在标签分配器上生成的软标签相同，粗标签是通过降低正样本分配的约束，允许更多的网络作为正目标。原因是一个辅助头的学习能力并不需要强大的引导头，为了避免丢失信息，作者将专注于优化样本召回的辅助头。对于引导头的输出，可以从查准率中过滤出高精度值的结果作为最终输出。然而，值得注意的是，如果粗标签的附加权值接近细标签的附加权值，则可能会在最终预测时产生错误的先验结果

#### dynamic k estimation

每个GT应该分配多少个对应的positive anchors呢？YOLOV8采用的分配策略会为每个GT分配固定个数的positive anchors，但直观上为每个GT分配的positive anchors数目应该是不一样的。每个GT分配的情况可能会根据目标的大小、遮蔽情況而有所不同，如何动态決定这个数值呢？可以使用dynamic k estimation的方法


首先，需要算出每个GT与每个anchor的IOU值，得出一个pairwise IOU矩阵；随后，需要將top-q个最大的IOU值加起來，再取整作为每个GT应该分配的anchor个数。

如下面的例子，top-q=10；不足10的部分则全部取：

![](./imgs/v2-a1237e46d7ec1028c93f4213b7c9887d_1440w.jpg)

由与s的和必須和d的和一致，故不足的部分会用background代替，成本可以表示为和背景的损失函數，最后依然套用Sinkhorn-Knopp算法求解：

![](./imgs/v2-ab14d1eaba9fd5679ff3288cb8c5a8c7_1440w.jpg)

#### simOTA方法

Sinkhorn-Knopp算法增加了25%的花銷，为了节省时间，提取了simOTA算法，得到了类似效果。主要思想如下：

1、为每个GT选择dynamic k个成本最小的positive anchors;

![](./imgs/v2-e43c73da778be4dd65470c5558f5eebc_1440w.jpg)

2、一旦发生ambiguous anchors的问题，则只会保留最小的cost：

![](./imgs/v2-403533ec244b2f9dec2408fc16d27c8d_1440w.jpg)



1、拆分head_outs输出从[b,c,h,w]到[b,na,c//na,h,w]

```
[8, 27, 80, 80] -> [8,3,80,80,9]
```
2、从gt_targets（dict）中生成targets_labels [nt,6]

```
# 第一个值是批量索引
# 第二个值是类别
# 第3到6是坐标(x,y,w,h)
```
3、构建目标

```
1、基于批量进行ancher匹配（按照yolov5的匹配方式分配对应的正样本）【b,a,gj,gi】。
2、基于批量进行预测样本匹配 [0,1,2,...8] batch=8
    不同的缩放级别的预测样本匹配 （8、16、32）pi[b,a,gj,gi]
      px,py 按照中心点回归方式
      pw,ph 回归方式
    计算gt与pre bbox 直接的IOU 即pairwise IOU 矩阵，并计算IOU损失 pairwise_iou_loss = -paddle.log(pairwise_ious + 1e-5)
    动态k估计 min_topk默认为10。 每个GT（每行）选择cost最小的min(min_topk, pair_wise_iou.shape[1])个anchor
    找出应该給每个GT框分配多少个(dynamic_ks)anchors; dynamic_ks 最小必须为1
    #（cls_preds_）求出最終的类別confidence = 预测概率 x objectness
    # 开根号，避免值太小 cls_preds_.sqrt_() ->[0,1)
    为了符合logits值，取sigmoid函數的逆運算: log(y / (1 - y) + 1e-5) (0,1) -> (-6.9, 6.9) 如下图
    计算成本矩阵  cost = (pairwise_cls_loss + 3.0 * pairwise_iou_loss)

    每个GT应该分配那个anchors,相应位置标记为1 （相应的cost最少）matching_matrix
    按列求和；每列应该为1，否则ambiguous anchors，如果出现ambiguous anchors情况，找出cost最小的行设为1
    根据正负样本标记筛选anchor
    按照不同的输出层生成最終的标签
   

```

![](./imgs/20250625171753.png)
np.log(y/(1-y)) 图

**loss**

yolov7的损失函数基本上和yolov5的损失函数如出一辙：
- class loss采用二元交叉熵
- box loss采用CIOU LOSS
- object loss采用IOU LOSS 作为软标签 进行BCE
同時，box loss针对P3,P4,P5三个prediction层各自有不同的权重，也加大对小目标的检测力度。



YOLOv7 的 W6、E6、D6 和 E6E 模型是官方发布的一系列高性能变体，专门针对高分辨率输入（1280x1280）设计。这些模型在原始 YOLOv7 基础上进行了深度和宽度的扩展，显著提升了检测精度。


模型架构对比
模型|	参数量|	GFLOPs|	层级深度|	特征金字塔|	适用场景
---|---|---|---|---|---
W6|	≈70M|	180|	中等|	P3-P8|	通用高精度
E6|	≈97M|	250|	最深|	P3-P8|	服务器端/最高精度
D6|	≈80M|	210|	较深|	P3-P8|	精度-速度平衡
E6E|	≈115M|	300|	最深|	P3-P8|	极限精度/研究

> 所有模型均支持 1280x1280 输入分辨率，使用 6 级特征金字塔（P3-P8）

> https://zhuanlan.zhihu.com/p/670643999

### yolov8 (2023)

‌YOLOv8是Ultralytics团队于2023年1月推出的目标检测模型，作为YOLO系列的最新版本，它在速度、精度和灵活性方面均有显著提升，支持目标检测、实例分割、姿态估计等多种任务

YOLOv8 是一个 SOTA 模型，它建立在以前 YOLO 版本的成功基础上，并引入了新的功能和改进，以进一步提升性能和灵活性。具体创新包括一个新的骨干网络、一个新的 Ancher-Free 检测头和一个新的损失函数，可以在从 CPU 到 GPU 的各种硬件平台上运行

![](./imgs/d238933c62901e9b4e06ac3b8cb22df4.jpg)

![](./imgs/yolov8.png)

YOLOv8是Ultralytics公司推出的YOLO的最新版本。作为一款尖端、最先进的（SOTA）车型，YOLOv8在之前版本的成功基础上，引入了新的功能和改进，以增强性能、灵活性和效率。YOLOv8支持全方位的视觉AI任务，包括检测、分割、姿态估计、跟踪和分类。这种多功能性允许用户在不同的应用程序和域中利用YOLOv8的功能

Ultralytics为YOLO模型发布了一个全新的存储库。它被构建为 用于训练对象检测、实例分割和图像分类模型的统一框架。

- 提供了一个全新的 SOTA 模型，包括 P5 640 和 P6 1280 分辨率的目标检测网络和基于 YOLACT 的实例分割模型。和 YOLOv5 一样，基于缩放系数也提供了 N/S/M/L/X 尺度的不同大小模型，用于满足不同场景需求
- 骨干网络和 Neck 部分可能参考了 YOLOv7 ELAN 设计思想，将 YOLOv5 的 C3 结构换成了梯度流更丰富的 C2f 结构，并对不同尺度模型调整了不同的通道数，属于对模型结构精心微调，不再是无脑一套参数应用所有模型，大幅提升了模型性能。不过这个 C2f 模块中存在 Split 等操作对特定硬件部署没有之前那么友好了
- Head 部分相比 YOLOv5 改动较大，换成了目前主流的解耦头结构，将分类和检测头分离，同时也从 Anchor-Based 换成了 Anchor-Free
- Loss 计算方面采用了 TaskAlignedAssigner 正样本分配策略，并引入了 Distribution Focal Loss
- 训练的数据增强部分引入了 YOLOX 中的最后 10 epoch 关闭 Mosiac 增强的操作，可以有效地提升精度

YOLOv8 还高效灵活地支持多种导出格式，并且该模型可以在 CPU 和 GPU 上运行。YOLOv8 模型的每个类别中有五个模型用于检测、分割和分类。YOLOv8 Nano 是最快和最小的，而 YOLOv8 Extra Large (YOLOv8x) 是其中最准确但最慢的


**骨干网络**

YOLOv8 CSPDarkNet骨干区别于YOLOv5 CSPDarkNet
1. self.stem 在YOLOv8的内核大小3，而在 在YOLOv5为6
2. 使用c2player在YOLOv8，在YOLOv5使用CSPLayer
3. num_blocks在YOLOv8中为[3,6,6,3]，而在YOLOv5中为[3,6,9,3] 
4. M/L/X最后阶段的通道 

**neck**
YOLOv8 使用的 YOLOv8 CSP-PAN FPN 不同于YOLOv5 CSP-PAN FPN
- 没有横向conv
- 使用c2player在YOLOv8而在YOLOv5中使用CSPLayer


具体改进如下：

1. Backbone：使用的依旧是CSP的思想，不过YOLOv5中的C3模块被替换成了C2f模块，实现了进一步的轻量化，同时YOLOv8依旧使用了YOLOv5等架构中使用的SPPF模块；
2. PAN-FPN：毫无疑问YOLOv8依旧使用了PAN的思想，不过通过对比YOLOv5与YOLOv8的结构图可以看到，YOLOv8将YOLOv5中PAN-FPN上采样阶段中的卷积结构删除了，同时也将C3模块替换为了C2f模块；
3. Decoupled-Head：是不是嗅到了不一样的味道？是的，YOLOv8走向了Decoupled-Head；
4. Anchor-Free：YOLOv8抛弃了以往的Anchor-Base，使用了Anchor-Free的思想；
5. 损失函数：YOLOv8使用VFL Loss作为分类损失，使用DFL Loss+CIOU Loss作为分类损失；
6. 样本匹配：YOLOv8抛弃了以往的IOU匹配或者单边比例的分配方式，而是使用了Task-Aligned Assigner匹配方式。


#### C3 Vs C2f

![](./imgs/c3.png)

针对C3模块，其主要是借助CSPNet提取分流的思想，同时结合残差结构的思想，设计了所谓的C3 Block，这里的CSP主分支梯度模块为BottleNeck模块，也就是所谓的残差模块。同时堆叠的个数由参数n来进行控制，也就是说不同规模的模型，n的值是有变化的。

其实这里的梯度流主分支，可以是任何之前你学习过的模块，比如，美团提出的YOLOv6中就是用来重参模块RepVGGBlock来替换BottleNeck Block来作为主要的梯度流分支，而百度提出的PP-YOLOE则是使用了RepResNet-Block来替换BottleNeck Block来作为主要的梯度流分支。而YOLOv7则是使用了ELAN Block来替换BottleNeck Block来作为主要的梯度流分支。

![](./imgs/c2f.png)

C2f模块就是参考了C3模块以及ELAN的思想进行的设计，让YOLOv8可以在保证轻量化的同时获得更加丰富的梯度流信息。


#### PAN-FPN改进

YOLOv5的Neck部分的结构图如下：

<div align="center"><img src='./imgs/v5FPN.png' width=300px height=300px /></div>


YOLOv6的Neck部分的结构图如下:

<div align="center"><img src='./imgs/v6FPN.png' width=330px height=350px /></div>


YOLOv8的结构图：


<div align="center"><img src='./imgs/v8FPN.png' width=330px height=350px /></div>


可以看到，相对于YOLOv5或者YOLOv6，YOLOv8将C3模块以及RepBlock替换为了C2f，同时细心可以发现，相对于YOLOv5和YOLOv6，YOLOv8选择将上采样之前的1×1卷积去除了，将Backbone不同阶段输出的特征直接送入了上采样操作


#### Head部分

先看一下YOLOv5本身的Head（Coupled-Head）：

<div align="center"><img src='./imgs/v5head.png' width=430px height=250px /></div>


而YOLOv8则是使用了Decoupled-Head，回归头的通道数也变成了4*reg_max的形式：

<div align="center"><img src='./imgs/v8head.png' width=380px height=450px /></div>


#### 正负样本的匹配

标签分配是目标检测非常重要的一环，在YOLOv5的早期版本中使用了MaxIOU作为标签分配方法。然而，在实践中发现直接使用边长比也可以达到一样的效果。而YOLOv8则是抛弃了Anchor-Base方法使用Anchor-Free方法，找到了一个替代边长比例的匹配方法: TaskAligned。为与NMS搭配，训练样例的Anchor分配需要满足以下两个规则：


- 正常对齐的Anchor应当可以预测高分类得分，同时具有精确定位；
- 不对齐的Anchor应当具有低分类得分，并在NMS阶段被抑制。

基于上述两个目标，TaskAligned设计了一个新的Anchor alignment metric 来在Anchor level 衡量Task-Alignment的水平。并且，Alignment metric 被集成在了 sample 分配和 loss function里来动态的优化每个 Anchor 的预测。

> Anchor alignment metric：

分类得分和 IoU表示了这两个任务的预测效果，所以，TaskAligned使用分类得分和IoU的高阶组合来衡量Task-Alignment的程度。使用下列的方式来对每个实例计算Anchor-level 的对齐程度： $ t=s^{\alpha}+\mu^{\beta} $  s 和 u 分别为分类得分和 IoU 值，α 和 β 为权重超参。从上边的公式可以看出来，t 可以同时控制分类得分和IoU 的优化来实现 Task-Alignment，可以引导网络动态的关注于高质量的Anchor。