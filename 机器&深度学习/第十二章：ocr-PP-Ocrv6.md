
**PP-OCRv6** 是 PP-OCR 最新一代通用文字识别解决方案。PP-OCRv6 基于全新设计的 PPLCNetV4 统一骨干网络，提供 tiny、small、medium 三档模型，分别面向端侧/IoT、移动端/桌面端、服务端场景。PP-OCRv6 在语言覆盖方面实现重大突破，medium/small 档单一模型统一支持简体中文、繁体中文、英文、日文及 46 种拉丁语系语言共 50 种语言（tiny 档支持 49 种，不含日文）。在内部多场景综合评估集上，PP-OCRv6_medium 相比 PP-OCRv5_server 识别精度提升 5.1%、检测精度提升 4.6%，同时 GPU 推理速度提升 2.37×；以仅 34.5M 参数的规模，精度超越 Qwen3-VL-235B、GPT-5.5 等大型视觉语言模型。

PP-OCRv6 的主要贡献如下：

- 统一可扩展的模型族：提供覆盖 1.5M 至 34.5M 参数的三档完整 OCR 模型族。medium 档达到 86.2% 检测 Hmean 和 83.2% 识别准确率，可作为工业部署和大规模数据管线的高效生产级基础设施。
- 面向 OCR 的轻量级架构创新：提出一系列专为 OCR 任务定制的轻量级架构组件——(i) LCNetV4：集成结构重参数化的 MetaFormer 风格轻量骨干；(ii) RepLKFPN：利用膨胀可重参数化深度卷积实现大感受野的检测颈部；(iii) EncoderWithLightSVTR：基于局部-全局注意力和加性跳跃连接的识别颈部。
- 广泛的多语言与多场景泛化：单一模型扩展至支持 50 种语言和多种挑战性工业场景（如数码显示屏、点阵字符、轮胎印字等），显著提升了传统通用视觉语言模型难以覆盖的专业场景 OCR 性能。


#### 主干网络

PPLCNetV4

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr/PP-OCRv6/backbone.png)

```
    x = self.stem(x)
    o1 = self.blocks_s1(x)
    o2 = self.blocks_s2(o1)
    o3 = self.blocks_s3(o2)
    o4 = self.blocks_s4(o3)
    return [o1, o2, o3, o4]
```

##### StemBlock

StemBlock 的设计灵感主要来源于 Inception-v4 和 DSOD 等网络。它的核心思想是在网络初期，以较低的计算成本，有效地提取图像的基础特征，如边缘、纹理、颜色等信息

- 入口卷积层 (Entry Convolution)：首先使用一个步长（stride）为2的卷积层（如 3x3 卷积）对输入进行快速降维和下采样
- 双分支处理 (Two-branch Processing)：将上一步的输出送入两个并行的分支，这是该模块的核心
    - 通过2个 2x2 卷积  2x2 的局部卷积，这样做的好处是能在降维/升维的同时融入更多的空间局部信息 
    - 池化层（k=2, s=1）：在 保持分辨率不变 的前提下，提取每个 2x2 邻域内的最强响应，增强特征的平移不变性并抑制噪声
- 将两个分支的输出在通道维度上拼接（Concatenate） 起来，再通过步长为2的 3x3 卷积进行特征提取和下采样，再通过1x1 卷积在这里负责跨通道的信息融合，将特征映射回高维空间

#### 检测模块升级

- RepLKFPN：轻量级大核特征金字塔，使用 DilatedReparamBlock（7×7 深度卷积 + 膨胀分支），相比 PP-OCRv5 的 RSEFPN 参数减少 31%（118K vs 172K），同时感受野从 3×3 扩大到 7×7。
- 辅助深度监督：在 P2、P3、P4 层级添加预测头，训练时提供更强梯度信号。
- DiceBCE Loss：组合 DiceLoss + Focal Loss，对小目标和密集文本提供更好的逐像素监督。

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr/PP-OCRv6/ppocrv6_det_pip_ori.png)



https://www.paddleocr.ai/latest/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html



#### 识别模块


- EncoderWithLightSVTR 颈部：局部上下文建模（1×7 深度卷积）+ 全局自注意力（1-2 层 Transformer），通过加性跳跃连接（而非 PP-OCRv5 的拼接）减少参数。
- 多头解码器：CTCHead 用于高效并行推理，NRTRHead 用于训练时辅助监督（推理时移除）。
- Tiny 模型特殊设计：无颈部（直接 reshape + FC），使用 medium 模型蒸馏训练。
- 多语言统一：字典扩展约 200 个带变音符号字符，实现单模型 48 语言覆盖。

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr/PP-OCRv6/rec.png)



##### EncoderWithLightSVTR

- **局部上下文建模 (Local Context Modeling)**：使用 1×7 的深度可分离卷积 (Depthwise Conv) 来捕捉文字中相邻笔画或字符的局部细节

- **全局自注意力 (Global Self-Attention)**：通过 1-2 层 Transformer 层来捕捉整个文本行中长距离的依赖关系，理解单词的整体语境

- **加法跳跃连接 (Additive Skip Connections)**：与PP-OCRv5中使用的拼接（Concat）方式不同，v6版本采用了加法来融合不同层的特征。这种设计能在不牺牲性能的前提下，有效减少模型参数

    ```
    skip = self.skip_conv(x)  # 1*1  dims=192
    ...
    z = z + skip
    return z
    ```


```
if self.use_guide: # 是否冻结主干网络梯度
    x = x.clone()
    x.stop_gradient = True

skip = self.skip_conv(x)
z = self.conv_reduce(x)  # 减少维度到dims
z = z + self.local_conv(z)  # 局部上下文建模
B, C, H, W = z.shape
z = z.flatten(2).transpose([0, 2, 1]) # [batch, C,H,W] -> [batch,C,H*W] -> [batch,H*W,C]
for blk in self.svtr_block:  # block 层数为depth=2
    z = blk(z)
z = self.norm(z)
z = z.reshape([0, H, W, C]).transpose([0, 3, 1, 2])
z = z + skip   # 加法跳跃连接
return z
```