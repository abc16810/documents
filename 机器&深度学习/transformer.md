

https://mp.weixin.qq.com/s/XFniIyQcrxambld5KmXr6Q

#### 回顾

首先我们先回顾一下Transformer原理。宏观层面，Transformer可以看成是一个黑箱操作的序列到序列（seq2seq）模型。例如，在机器翻译中，输入一种语言，经Transformer输出翻译后的另一种语言。

拆开这个黑箱，可以看到模型本质就是一个Encoders-Decoders结构。

- 每个Encoders中分别由6层Encoder组成。(所有Encoder结构完全相同，但是训练参数不同，每个参数是独立训练的，循环执行6次Encode，而不是只训练了一个Encoder然后复制5份)。
- Decoders同理。
- 这里每个Encoders包含6层Encoder，只是论文中Nx=6，实际可以自定义。

![](./imgs/1640.webp)

Transformer整体架构如下图所示。

![](./imgs/t640.webp)

其中，

- 编码端：经过词向量层（Input Embedding）和位置编码层（Positional Encoding），得到最终输入，流经自注意力层（Multi-Head Attention）、残差和层归一化（Add&Norm）、前馈神经网络层（Feed Forward）、残差和层归一化（Add&Norm），得到编码端的输出（后续会和解码端进行交互）。
- 解码端：经过词向量层（Output Embedding）和位置编码层（Positional Encoding），得到最终输入，流经掩码自注意力层（Masked Multi-Head Attention，把当前词之后的词全部mask掉）、残差和层归一化（Add&Norm）、交互注意力层（Multi-Head Attention，把编码端的输出和解码端的信息进行交互，Q矩阵来自解码端，K、V矩阵来自编码端的输出）、残差和层归一化（Add&Norm）、前馈神经网络层（Feed Forward）、残差和层归一化（Add&Norm），得到解码端的输出。


#### Encoder

![](./imgs/2640.webp)

下面还是以机器翻译("我是学生"->"I am a student")为例说明。

对于上图中，整个模型的输入即为"我是学生"，目标是将其翻译为"I am a student"，但是计算机是无法识别"我是学生"的，需要将其转化为二进制形式，再送入模型。

将中文转换为计算机可以识别的向量通常有两种方法：

- One Hot编码：形成高维向量，对于中文来说，汉字的数量就是向量的维度，然后是哪个字就将对应位置变为1，其它位置变为0，以此来表示一句话。
- Embedding词嵌入：通过网络进行训练或者通过一些训练好的模型将其转化成连续性的向量。

一般来说第二种方法使用较多，因为第一种有几个缺点，第一个就是每个字都是相互独立的，缺少语义联系信息，第二就是汉字数量太多，会导致生成的维度过大，占用系统内存。

##### 输入Input

输入Inputs维度是[batch size,sequence length]，经Word2Vec，转换为计算机可以识别的Input Embedding，论文中每个词对应一个512维度的向量，维度是[batch_size,sequence_length,embedding_dimmension]。batch size指的是句子数，sequence length指的是输入的句子中最长的句子的字数，embedding_dimmension是词向量长度。

![](./imgs/3640.webp)

如上图所示，以机器翻译("我是学生"->"I am a student")为例，首先对输入的文字进行Word Embedding处理，每个字（词）用一个连续型向量表示（这里定义的是4维向量），称为词向量。这样一个句子，也就是嵌入后的输入向量input Embedding就可以用一个矩阵表示(4*4维，序列长度为4，每个字用4维向量表示)。input Embedding加上位置信息得到编码器的输入

矩阵。

「为什么需要在input Embedding加上位置信息？」 与RNN相比，RNN是一个字一个字输入，自然可以保留每个字的顺序关系信息，而Transformer使用的是自注意力机制来提取信息，一个句子中的每个字/词是并行计算，虽然处理每个字的时候考虑到了所有字对其的影响，但是并没有考虑到各个字相互之间的位置信息，也就是上下文。所以需要引入位置信息。

Transformer中使用Positional Encoding表示每个字/词的位置信息。定义如下：

```math
PE_{(pos, 2i)}   = sin(pos / 10000^{2i/d_{model}}) \\
PE_{(pos, 2i+1)} = cos(pos / 10000^{2i/d_{model}})
```

- pos：当前位置（坐标）。例如 $P^{03}$，表示第1个字，pos=0；$P^{13}$ ，表示第2个字，pos=1。
- $PE_{(pos, i)}$ 表示pos位置处的字的Positional Encoding向量，该向量可以用来给句子中每个字提供位置信息。换句话说，就是我们通过注入每个字的位置信息，增强了模型输入。
- i：维度索引（0 ≤ i < $d_{model}/2$ ）
- d_model：嵌入维度,例如上述示例定义的4，例如论文中的512


例如 $P^{22}$ 表示第3个字(pos=2) “学” 的第3维度(i=2)，对应的值就是 
```math
PE_{2,2}=sin(\frac{2}{ 10000^{ \frac {2}{4}}})
```


例如 $P^{13}$ 表示第2个字(pos=1) “是” 的第4维度(i=3)，对应的值就是 
```math
PE_{1,3}=cos(\frac{1}{ 10000^{ \frac {2}{4}}})
```

假设词向量Embedding的维度是6，即 $d_{model}=6$ ，根据上面的公式：

pos = 0 的情况

```math
PE_{0} = \begin{bmatrix} \sin(\frac{1}{10000^\frac{0}{6}} \cdot 0), \\ \cos(\frac{1}{10000^\frac{0}{6}} \cdot 0), \\ \sin(\frac{1}{10000^\frac{2}{6}} \cdot 0), \\ \cos(\frac{1}{10000^\frac{2}{6}} \cdot 0), \\ \sin(\frac{1}{10000^\frac{4}{6}} \cdot 0), \\ \cos(\frac{1}{10000^\frac{4}{6}}\cdot 0) \\ \end{bmatrix}  =  \begin{bmatrix} 0, \\ 1, \\0, \\ 1, \\ 0, \\ 1 \end{bmatrix}\tag*{}
```

pos = 1 的情况

```math

PE_{1} = \begin{bmatrix} \sin(\frac{1}{10000^\frac{0}{6}} \cdot 1), \\ \cos(\frac{1}{10000^\frac{0}{6}} \cdot 1), \\ \sin(\frac{1}{10000^\frac{2}{6}} \cdot 1), \\ \cos(\frac{1}{10000^\frac{2}{6}} \cdot 1), \\ \sin(\frac{1}{10000^\frac{4}{6}} \cdot 1), \\ \cos(\frac{1}{10000^\frac{4}{6}}\cdot 1) \\ \end{bmatrix}  =  \begin{bmatrix} 0.8414709848, \\ 0.54030230586, \\0.04639922346, \\ 0.99892297604, \\ 0.00215443302, \\ 0.9999976792 \end{bmatrix}\tag*{}
```

pos = 2 的情况


```math

PE_{2} = \begin{bmatrix} \sin(\frac{1}{10000^\frac{0}{6}} \cdot 2), \\ \cos(\frac{1}{10000^\frac{0}{6}} \cdot 2), \\ \sin(\frac{1}{10000^\frac{2}{6}} \cdot 2), \\ \cos(\frac{1}{10000^\frac{2}{6}} \cdot 2), \\ \sin(\frac{1}{10000^\frac{4}{6}} \cdot 2), \\ \cos(\frac{1}{10000^\frac{4}{6}}\cdot 2) \\ \end{bmatrix}  =  \begin{bmatrix} 0.90929742682, \\-0.41614683654, \\0.09269850077, \\ 0.99569422412, \\ 0.00430885604, \\ 0.99999071683\end{bmatrix}\tag*{}
```

```python
position = paddle.arange(0, 6, dtype='float32').unsqueeze(1)
div_term = paddle.exp(paddle.arange(0, 6, 2) * (-math.log(10000.0) / 6)) 
```


在2D中，我们有两个坐标：行（height）和列（width）。因此，我们可以分别为行和列构建位置嵌入，然后将它们拼接起来或者相加。常见的做法是分别构建两个方向的位置嵌入，然后按元素相加。


对于2D图像，DETR将2D坐标视为两个独立的1D坐标，然后分别计算位置嵌入（每个方向嵌入的维度是embed_dim/2），最后拼接起来得到embed_dim维的位置嵌入。具体如下：


 步骤：
  1. 确定网格的高度H和宽度W。
  2. 确定嵌入的维度d_model（必须为偶数，因为要分成两个方向）。
  3. 分别构建x轴（宽度方向）和y轴（高度方向）的位置编码，每个轴的位置编码维度为d_model//2。
  4. 将两个位置编码在最后一个维度拼接，得到每个位置d_model维的嵌入。