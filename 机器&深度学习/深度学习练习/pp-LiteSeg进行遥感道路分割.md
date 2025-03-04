#### 数据集


在灾区，尤其是在发展中国家，地图和无障碍信息对于危机应对至关重要。DeepGlobe Road Extraction Challenge（https://competitions.codalab.org/competitions/18467）提出了从卫星图像中自动提取道路和街道网络的挑战。

**数据**
Road Challenge 的训练数据包含 6226 张 RGB 卫星图像，大小为 1024x1024。
该图像具有 50 厘米像素分辨率，由 DigitalGlobe 的卫星收集。
该数据集包含 1243 个验证图像和 1101 个测试图像（但没有掩码）。

**标签**

每个卫星图像都与道路标签的蒙版图像配对。蒙版是灰度图像，白色代表道路像素，黑色代表背景。
卫星图像和相应蒙版图像的文件名是id _sat.jpg 和id _mask.png。id是一个随机整数。
请注意：遮罩图像的值可能不是纯0和255，转换为标签时，请在阈值128处进行二值化。
由于注释分割掩码的成本，标签并不完美，特别是在农村地区。此外，我们故意没有标注农田内的小路。

#### 数据集准备

DeepGlobe数据集已经整理成如下格式。

```
deepglobe
├── readme.md
├── test.txt
├── train
├── train.txt
├── valid
└── val.txt
```

我们将标注的遥感图片划分为训练集、验证集和测试集。

训练集图片：4981张
验证集图片：623张
测试集图片：622张

`train.txt、val.txt、test.txt`分别表示训练集、验证集和测试的划分，保存的内容如下。

```
train/81456_sat.jpg train/81456_mask.png
train/814574_sat.jpg train/814574_mask.png
train/814591_sat.jpg train/814591_mask.png
train/814649_sat.jpg train/814649_mask.png
```

**图像预处理**

> 由于遮罩图像的值可能不是纯0和255，转换为标签时，需要在阈值128处进行二值化。

由于*_mask.png 是RGB 3通道格式 需要转换成P调色板模式


```
# paddle 处理标签的代码如下：
import numpy as np
from PIL import Image
np.asarray(Image.open(data['label']))

## 
import glob
import os
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# img = cv2.imread("tests/99816_mask.png")   # B G R
# img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# difference = 128
# retval, img_binary = cv2.threshold(img_gray, difference, 1, cv2.THRESH_BINARY)
# plt.imshow(img_binary)
# plt.show()
# cv2.imwrite('222.png', img_binary)

def mask_to_gray(inputdir, outdir, format='png', postfix=''):
    pattern = '*%s.%s' % (postfix, format)
    search_files = inputdir  /  pattern
    for file in glob.glob(str(search_files)):
        print('开始处理文件 %s' % file)
        f = Path(file)
        labelname=f.name
        outfile = outdir / labelname
        if not outdir.is_dir():
            os.makedirs(outdir)
        img = Image.open(file)
        if img.mode == 'RGB':
            img = np.asarray(img)
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            retval, img_binary = cv2.threshold(img_gray, 128, 1, cv2.THRESH_BINARY)
            cv2.imwrite(str(outfile), img_binary)
            print('处理完成')

        elif img.mode == 'P':
            print('忽略')
        else:
            print('错误模式')

if __name__  == '__main__':
    inputdir = Path('/srv/PaddleSeg/data/train')
    outdir = Path('/srv/PaddleSeg/data/new')
    mask_to_gray(inputdir, outdir)
```


训练 

```yaml
# ## pp_liteseg_stdc1_deepglobe_1024x1024_80k.yml
batch_size: 4
iters: 80000

train_dataset:
  type: Dataset
  dataset_root: data
  train_path: data/train.txt
  num_classes: 2
  mode: train
  transforms:
    - type: ResizeStepScaling
      min_scale_factor: 0.8
      max_scale_factor: 1.2
      scale_step_size: 0.25
    - type: RandomPaddingCrop
      crop_size: [1024, 1024]
    - type: RandomHorizontalFlip
    - type: RandomVerticalFlip
    - type: RandomDistort
      brightness_range: 0.3
      brightness_prob: 0.5
      contrast_range: 0.3
      contrast_prob: 0.5
      saturation_range: 0.3
      saturation_prob: 0.5
      hue_range: 15
      hue_prob: 0.5
    - type: Normalize

val_dataset:
  type: Dataset
  dataset_root: data
  val_path: data/val.txt
  num_classes: 2
  mode: val
  transforms:
    - type: Normalize

optimizer:
  type: SGD
  momentum: 0.9
  weight_decay: 4.0e-5

lr_scheduler:
  type: PolynomialDecay
  learning_rate: 0.01
  end_lr: 0
  power: 0.9
  warmup_iters: 1000
  warmup_start_lr: 1.0e-4


model:
  type: PPLiteSeg
  backbone:
    type: STDC1
    pretrained: https://bj.bcebos.com/paddleseg/dygraph/PP_STDCNet1.tar.gz
  arm_out_chs: [32, 64, 128]
  seg_head_inter_chs: [32, 64, 64]

loss:
  types:
    - type: OhemCrossEntropyLoss
      min_kept: 260000 
    - type: OhemCrossEntropyLoss
      min_kept: 260000
    - type: OhemCrossEntropyLoss
      min_kept: 260000
  coef: [1, 1, 1]
```


```
# 训练
python tools/train.py  --config configs/quick_start/pp_liteseg_stdc1_deepglobe_1024x1024_80k.yml \
--do_eval \
--num_workers 3 \
--save_interval 1000 \
--save_dir output/ocrnet_hrnetw18_deepglobe

# 预测
python tools/predict.py --config configs/quick_start/pp_liteseg_stdc1_deepglobe_1024x1024_80k.yml \
--model_path output/pp_liteseg_stdc1_deepglobe/best_model/model.pdparams  \
--image_path data/deepglobe/test.txt \
--save_dir output/pp_liteseg_stdc1_deepglobe_1024x1024_80k/pred_test
```
