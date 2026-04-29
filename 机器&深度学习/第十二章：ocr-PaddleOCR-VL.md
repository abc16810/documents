
### PaddleOCR-VL(2025.10.16)

PaddleOCR-VL 是一款先进、高效的文档解析模型，专为文档中的元素识别设计。其核心组件为 PaddleOCR-VL-0.9B，这是一种紧凑而强大的视觉语言模型（VLM），它由 NaViT 风格的动态分辨率视觉编码器与 ERNIE-4.5-0.3B 语言模型组成，能够实现精准的元素识别。该模型支持 109 种语言，并在识别复杂元素（如文本、表格、公式和图表）方面表现出色，同时保持极低的资源消耗。通过在广泛使用的公开基准与内部基准上的全面评测，PaddleOCR-VL 在页级级文档解析与元素级识别均达到 SOTA 表现。它显著优于现有的基于Pipeline方案和文档解析多模态方案以及先进的通用多模态大模型，并具备更快的推理速度。这些优势使其非常适合在真实场景中落地部署。


#### 关键指标

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr_vl/metrics/allmetric.png)


#### 核心特征

**紧凑而强大的视觉语言模型架构**： 我们提出了一种新的视觉语言模型，专为资源高效的推理而设计，在元素识别方面表现出色。通过将NaViT风格的动态高分辨率视觉编码器与轻量级的ERNIE-4.5-0.3B语言模型结合，我们显著增强了模型的识别能力和解码效率。这种集成在保持高准确率的同时降低了计算需求，使其非常适合高效且实用的文档处理应用。

**文档解析的SOTA性能**： PaddleOCR-VL在页面级文档解析和元素级识别中达到了最先进的性能。它显著优于现有的基于流水线的解决方案，并在文档解析中展现出与领先的视觉语言模型（VLMs）竞争的强劲实力。此外，它在识别复杂的文档元素（如文本、表格、公式和图表）方面表现出色，使其适用于包括手写文本和历史文献在内的各种具有挑战性的内容类型。这使得它具有高度的多功能性，适用于广泛的文档类型和场景。

**多语言支持**： PaddleOCR-VL支持109种语言，覆盖了主要的全球语言，包括但不限于中文、英文、日文、拉丁文和韩文，以及使用不同文字和结构的语言，如俄语（西里尔字母）、阿拉伯语、印地语（天城文）和泰语。这种广泛的语言覆盖大大增强了我们系统在多语言和全球化文档处理场景中的适用性。


#### 技术架构
PaddleOCR-VL 是个两阶段的结构：
- 第一阶段采用 PP-DocLayoutV2 进行版面分析，负责定位语义区域并预测阅读顺序
- 第二阶段通过 PaddleOCR-VL-0.9B 模型，基于版面预测结果对文本、表格、公式和图表等多样化内容进行细粒度识别，最后将文档结构化转换为Markdown与JSON格式。

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr_vl/methods/paddleocrvl.png)


##### PP-DocLayoutV2

PP-DocLayoutV2 具体结构是由两个顺序连接的网络组成：
- 第一个：基于RT-DETR的检测模型，负责执行布局元素检测与分类
- 第二个：输入检测到的边界框和类别标签，通过指针网络对这些布局元素进行排序

该模块目前仅支持 PP-DocLayoutV2 一个模型。模型结构上，PP-DocLayoutV2 是在版面检测模型 PP-DocLayout_plus-L（基于 RT-DETR-L 模型） 的基础上级联一个含 6 层 Transformer 层的轻量级指针网络（Pointer network）组成，原先 PP-DocLayout_plus-L 部分继续用于版面检测，识别文档图像中的不同元素（如文字、图表、图像、公式、段落、摘要、参考文献等），将其归类为预定义的类别并确定这些区域在文档中的位置。检测到的边界框和类别标签作为后续的指针网络的输入来对版面元素进行排序从而得到正确的阅读顺序。

![](./imgs/87af7dd3c9ffea659a16bd4df8e87b54.jpeg)

具体如上图所示，PP-DocLayoutV2 对来自 RT-DETR 检出的目标利用绝对二维位置编码和类别标签进行嵌入表示。此外，指针网络的注意力机制融合了 Relation-DETR中的几何偏置机制，以显式地建模元素之间的成对几何关系。成对关系头（pairwise relation head）将元素表示线性投影为查询（query）向量和键（key）向量，然后计算双线性相似度以生成成对的 logits，最终得到一个表示每对元素之间相对顺序的 N×N 矩阵。最后，一种确定性的“胜者累积”（win-accumulation）解码算法会为检测到的版面元素恢复出一个拓扑一致的阅读顺序。


##### PaddleOCR-VL-0.9B

PaddleOCR-VL-0.9B 的核心是通过 ERNIE-4.5-0.3B 这个语言模型驱动的，它的输入包括两部分：
- 第一部分：不同的任务指令(文本识别/表格识别)，通过分词器(tokenizer)，再进行向量化嵌入
- 第二部分：不同的图像元素通过NaViT风格编码?之后，再经过两层MLP和GELU之后，跟在指令输出后面

![](./imgs/126d3e004a899ca808a48e3696ef7700.jpeg)


**Dynamic Resolution Preprocessor**

Dynamic Resolution Preprocessor（动态分辨率预处理器）是一个常用于实时渲染、视频编码和计算机视觉等领域的组件。它的核心作用是在主处理流程（如渲染、编码或推理）开始之前，根据当前系统的性能、带宽或场景复杂度等实时条件，动态地调整输入图像或帧的分辨率。

配置中的动态分辨率策略并非由单一开关控制，而是通过 像素总数约束 来实现的

- "max_pixels": 2822400
输入图像被允许的最大像素数（约 2.82M，对应约 1680×1680）。如果原图像素超过此值，处理器会自动按比例缩小图像，直到总像素 ≤ max_pixels

- "min_pixels": 147384
输入图像被允许的最小像素数（约 147k，对应约 384×384）。如果原图像素低于此值，处理器会自动按比例放大图像，直到总像素 ≥ min_pixels

- "patch_size": 14
将图像切分为 14×14 的 patches（视觉 Transformer 的标准做法）。动态分辨率调整会确保最终的图像尺寸能被 patch_size 整除（通常配合 size_divisor 或取整逻辑，本配置未直接显示但隐含）。


不是固定将所有图片缩放到同一个分辨率（如 224×224），而是根据每张原始图片的尺寸，独立地选择一个缩放比例，使其像素总数落在 [min_pixels, max_pixels] 区间内，同时尽量保持宽高比。这在处理文档图像（OCR 任务常见）时尤为重要——因为文档图像的长宽比差异很大（A4 竖版、长截图、宽表格等），固定分辨率会丢失细节或浪费计算。

`preprocessor_config.json`
```yaml
{
  "auto_map": {
    "AutoImageProcessor": "image_processing_paddleocr_vl.PaddleOCRVLImageProcessor",
    "AutoProcessor": "processing_paddleocr_vl.PaddleOCRVLProcessor"
  },
  "do_convert_rgb": true, # 确保输入为 RGB 三通道
  "do_normalize": true,  # 执行标准化：(像素 - mean) / std
  "do_rescale": true,   # 将像素值从 [0,255] 缩放到 [0,1]
  "do_resize": true,   # 启用动态分辨率调整（基于上述 min/max pixels）
  "image_mean": [
    0.5,
    0.5,
    0.5
  ],
  "image_processor_type": "PaddleOCRVLImageProcessor",
  "image_std": [
    0.5,
    0.5,
    0.5
  ],
  "max_pixels": 2822400,
  "merge_size": 2,  # 将相邻的 2×2 个 patches 合并为一个 token（降低序列长度）
  "min_pixels": 147384,
  "patch_size": 14,
  "processor_class": "PaddleOCRVLProcessor",
  "resample": 3,   # 缩放时使用的插值方法，3 对应 cv2.INTER_CUBIC（双三次插值）
  "rescale_factor": 0.00392156862745098,  # 即 1/255，用于上述缩放 do_rescale
  "temporal_patch_size": 1  # 用于视频时的时间维度 patch 大小，此处为 1 表示仅处理单帧图像
}
```

**Vision Encoder**

在计算机视觉，特别是多模态模型（如视觉-语言模型，VLM）中，Vision Encoder 的核心任务是将原始的像素矩阵（图像）转换为高维、语义丰富的特征向量序列。简单说，它是一台“将图像翻译成模型能理解的语言”的机器。

MLP Projector：一个随机初始化的两层 MLP（带GELU激活函数），将视觉特征映射到语言模型可理解的语义空间


以典型的VLM架构为例（如LLaVA），流程如下
```
输入图像 → Vision Encoder (ViT, 冻结或微调) → 特征图 [H, W, C]
 → Projector (MLP) → 视觉Token序列 [N, D_LLM] → 与文本Token拼接 → LLM
```

**NaViT**




> https://aistudio.baidu.com/learn/education-video/6572372


### PaddleOCR-VL-1.5(2026.1.29)

PaddleOCR-VL-1.5 在1.0版本上进行了进一步能力的扩展和升级优化，在文档解析 OmniDocBench v1.5 上取得了 94.5% 的更高的新 SOTA（最佳）结果。为了严格评估其对现实世界物理畸变的鲁棒性——包括扫描伪影、倾斜、弯曲、屏摄和光照变化——我们提出了 Real5-OmniDocBench 基准测试。实验结果表明，该增强模型在这一新构建的基准测试中各个场景都达到了 SOTA 性能。此外，我们通过加入印章识别和文字检测识别任务扩展了模型能力，同时保持了 0.9B 的超紧凑 VLM 规模和高效率。

#### 关键指标

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr_vl_1_5/paddleocr-vl-1.5_metrics.png)


#### 核心特性

- **文档解析的SOTA性能**： 凭借 0.9B 的参数量，PaddleOCR-VL-1.5 在 OmniDocBench v1.5 上达到了 94.5% 的准确率，超越了之前的 SOTA 模型 PaddleOCR-VL。在表格、公式和文本识别方面观察到了显著提升。
- **现实5大场景文档解析的SOTA性能**： 引入了一种创新的文档解析方法，支持不规则形状定位，能够在文档倾斜和弯曲条件下实现精确的多边形检测。在扫描、弯曲、倾斜、屏摄和光照变化这五个现实场景的评估中，表现优于主流的开源和闭源模型。
- **0.9B紧凑架构扩充能力**： 模型引入了文本行定位与识别 以及 印章识别，所有相关指标均在各自任务中创下了新的 SOTA 结果。
- **强化多元素识别能力**： PaddleOCR-VL-1.5 进一步增强了在特定场景和多语言识别方面的能力。针对特殊符号、古籍、多语言表格、下划线和复选框的识别性能得到提升，语言覆盖范围扩展至包括中国藏文和孟加拉语。
- **长文档跨页解析**： 模型支持跨页表格自动合并和跨页段落标题识别，有效缓解了长文档解析中的内容碎片化问题。

#### 技术架构

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/paddleocr_vl_1_5/PaddleOCR-VL-1.5.png)




##### PP-DocLayoutV3

版面分析任务在版面区域检测的基础上，进一步引入了实例分割与阅读顺序预测能力。通过对输入的文档图像进行分析，不仅能识别各类版面元素（如文字、图表、图像、公式、段落标题、摘要、参考文献等）并输出其边界框，还能同时输出每个区域的精确轮廓掩码和阅读顺序编号，为文档理解与信息抽取流程提供更完整的结构化信息。

版面分析模块目前支持模型 PP-DocLayoutV3，基于 DETR 架构并以 PPHGNetV2-L 为骨干网络，在实例分割任务之上增加了阅读顺序预测分支，可端到端学习文档元素的阅读顺序关系。

![](https://raw.githubusercontent.com/cuicheng01/PaddleX_doc_images/refs/heads/main/images/modules/layout_analysis/layout_analysis.png
)

mask2polygon

```python
def mask2polygon(mask, max_allowed_dist, epsilon_ratio=0.004, extract_custom=True):
    """
    Postprocess mask by removing small noise.
    Args:
        mask (ndarray): 二值图像，形状 (H, W)，类型 uint8. 前景像素值为 255（或非零）。
        epsilon_ratio (float): 多边形近似精度因子（相对于轮廓周长的比例）。
                                值越小，点越多；值越大，点越少
    Returns:
        ndarray: The output mask after postprocessing.
    """
    # # 查找轮廓（只取外轮廓；若需包含孔洞，改用 RETR_TREE）
    # CHAIN_APPROX_SIMPLE 压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，例如一个矩形轮廓只需4个点来保存轮廓信
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not cnts:
        return None

    # 计算每个轮廓的面积 取最大值
    cnt = max(cnts, key=cv2.contourArea)
    # 计算轮廓周长，多边形近似
    epsilon = epsilon_ratio * cv2.arcLength(cnt, True)
    approx_cnt = cv2.approxPolyDP(cnt, epsilon, True)
    # # 转换为 (x, y) 列表
    polygon_points = approx_cnt.squeeze()
    polygon_points = np.atleast_2d(polygon_points)  # 确保输入至少是二维数组
    if extract_custom:
        # 通过max_allowed_dist 过滤相应多边形点
        polygon_points = extract_custom_vertices(polygon_points, max_allowed_dist)

    return polygon_points
```

**整体设计思路**

PP-DocLayoutV3摒弃了传统的矩形框检测方法，采用端到端的实例分割架构。这种设计能够更好地处理真实场景中的复杂文档布局，特别是那些包含倾斜、弯曲或非矩形区域的文档元素。

模型的核心思想是将文档布局分析任务转化为实例分割问题，为每个版面元素生成精确的像素级掩码，同时完成多类别分类。这种方法相比传统的边界框检测，能够提供更精确的定位信息。

**网络结构设计**

PP-DocLayoutV3基于改进的Mask R-CNN架构，主要包含以下几个核心组件：
<ul><li><strong>骨干网络</strong>：采用ResNet-FPN（PPHGNetV2）作为特征提取主干，能够在不同尺度上捕获文档布局特征（返回4阶段特征）</li>
<li><strong>区域建议网络</strong>：生成候选区域提案，定位潜在的版面元素</li><li><strong>ROI对齐</strong>：精确对齐特征区域，为后续分类和分割提供高质量特征</li><li><strong>多任务头</strong>：同时完成边界框回归、类别分类和掩码预测</li></ul>



**多边形边界框的技术实现**

传统目标检测通常使用轴对齐的矩形边界框（xmin, ymin, xmax, ymax），但对于文档中的倾斜、弯曲区域，矩形框会包含大量背景或遗漏部分内容。

关键创新点一：可变形注意力机制。 DETR原本使用固定的注意力模式，PP-DocLayoutV3引入了可变形注意力，让模型能够“聚焦”在非矩形的区域上。注意力头可以学习到文档元素的形状先验，比如表格通常是网格状，文本行通常是长条形。

关键创新点二：多边形回归头。 在DETR的解码器输出后，PP-DocLayoutV3添加了一个专门的多边形回归头。这个头不是直接预测多边形点坐标，而是预测相对于一个初始多边形的偏移量，这样训练更稳定。

**阅读顺序的自动确定**
文档布局分析不仅要识别元素，还要确定阅读顺序。对于平面文档，通常是左上到右下；但对于非平面文档，顺序可能很复杂。
PP-DocLayoutV3通过两种方式确定阅读顺序：

方式一：几何关系学习。 模型在训练时，除了学习每个元素的位置和类别，还会学习元素之间的相对位置关系。通过注意力机制，模型能够捕捉到“这个文本块应该在那个文本块之后”这样的信息。
方式二：图神经网络后处理。 对于特别复杂的布局，PP-DocLayoutV3使用一个轻量的图神经网络对初步结果进行后处理。将每个布局元素作为图节点，元素之间的空间关系作为边，通过图推理确定最优的阅读顺序。