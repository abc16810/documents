
#### yaml

paddle下的yaml配置文件如下：
```
batch_size: 2
iters: 80000

train_dataset:
  type: Dataset
  dataset_root: /srv/data/dongqu
  train_path: /srv/data/dongqu/train.txt
  num_classes: 2  # 前景和背景
  mode: train
  transforms:
    - type: ResizeStepScaling
      min_scale_factor: 0.5
      max_scale_factor: 2.0
      scale_step_size: 0.25
    - type: RandomPaddingCrop
      crop_size: [1024, 512]
    - type: RandomHorizontalFlip
    - type: RandomDistort
      brightness_range: 0.5
      contrast_range: 0.5
      saturation_range: 0.5
    - type: Normalize

val_dataset:
  type: Dataset
  dataset_root: /srv/data/dongqu
  val_path: /srv/data/dongqu/val.txt
  num_classes: 2
  mode: val
  transforms:
    - type: Normalize

optimizer:
  type: SGD
  momentum: 0.9
  weight_decay: 4.0e-5

lr_scheduler:   # 率值逐步从初始的 learning_rate，衰减到 end_lr
  type: PolynomialDecay
  learning_rate: 0.01
  power: 0.9
  end_lr: 1.0e-5


loss:
  types:
    - type: CrossEntropyLoss
  coef: [1, 0.4]  # 对应模型返回的长度

# 返回list，长度为2
model:
  type: PSPNet
  backbone:
    type: ResNet50_vd     # 骨干网络
    output_stride: 8    # 最终缩放8倍
    pretrained: https://bj.bcebos.com/paddleseg/dygraph/resnet50_vd_ssld_v2.tar.gz   # 骨干网络预训练
  enable_auxiliary_loss: True   # 是否计算额外的损失，（特征【-2】）
  align_corners: False
  pretrained: null
  # backbone_indices: (2, 3)
```
