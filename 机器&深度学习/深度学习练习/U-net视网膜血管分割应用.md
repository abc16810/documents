#### 数据集

这个DRIVE (Digital Retinal Images for Vessel Extraction)数据集来自荷兰的一个筛分计划，旨在进行分割目的和有关视网膜图像中血管的研究。这些图像是从一组400名年龄介于20到85岁的糖尿病患者中随机选择的。在这批图像中，有33人没有显示出任何损伤或疾病的迹象，但有7人显示出糖尿病视网膜病变的迹象。为此，需要进行分割过程以更好地研究眼科学和相关患者。

[数据集下载](https://bj.bcebos.com/paddleseg/dataset/drive/drive.zip)


```
train_dataset:
  type: DRIVE
  dataset_root: data/DRIVE
  transforms:
    - type: ResizeStepScaling
      min_scale_factor: 0.5
      max_scale_factor: 2.0
      scale_step_size: 0.25
    - type: RandomPaddingCrop
      crop_size: [128, 128]
    - type: RandomHorizontalFlip
    - type: RandomVerticalFlip
    - type: RandomDistort
      brightness_range: 0.4
      contrast_range: 0.4
      saturation_range: 0.4
    - type: Normalize
  mode: train

val_dataset:
  type: DRIVE
  dataset_root: data/DRIVE
  transforms:
    - type: Normalize
  mode: val
```




#### unet网络

```
model:
  type: UNet
  num_classes: 2   # 指定类别数，
  use_deconv: False # 是否使用反卷积
  pretrained: Null  # 预训练权重
  # in_channels  图片输入通道  默认3
  # align_corners  F.interpolate的一个参数。当特征的输出大小为偶数时，它应该设置为False，例如1024x512，否则设置为True，例如769x769。默认值False
```

##### encode 部分

| input | name | Operator | output| cuts |
| --- | --- | --- | ---| --- |
| N * 3 *128 * 128 | double_conv0 | ConvBNReLU 3*3 64 same  | N * 64 *128 * 128 | |
| N * 64 *128 * 128 | double_conv1 | ConvBNReLU 3*3 64 same  | N * 64 * 128 * 128 | y0 |
| N * 64 *128 * 128 | down_sample_0_0 | MaxPool2D 2*2 s=2 | N * 64 * 64 * 64 | |
| N * 64 *64 * 64 | down_sample_0_1 | ConvBNReLU 3*3 128 same | N * 128 * 64 * 64 | |
| N * 128 *64 * 64 | down_sample_0_2 | ConvBNReLU 3*3 128 same | N * 128 * 64 * 64 | y1 |
| N * 128 *64 * 64 | down_sample_1_0 | MaxPool2D 2*2 s=2 | N * 128 * 32 * 32 | |
| N * 128 *32 * 23 | down_sample_1_1 | ConvBNReLU 3*3 256 same | N * 256 * 32 * 32 | |
| N * 256 *32 * 32 | down_sample_1_2 | ConvBNReLU 3*3 256 same | N * 256 * 32 * 32 | y2|
| N * 256 *32 * 32 | down_sample_2_0 | MaxPool2D 2*2 s=2 | N * 256 * 16 * 16 | |
| N * 256 *16 * 16 | down_sample_2_1 | ConvBNReLU 3*3 512 same | N * 512 * 16 * 16 | |
| N * 512 *16 * 16 | down_sample_2_2 | ConvBNReLU 3*3 512 same | N * 512 * 16 * 16 | y3 |
| N * 512 *16 * 16 | down_sample_3_0 | MaxPool2D 2*2 s=2 | N * 512 * 8 * 8 | |
| N * 512 *8 * 8 | down_sample_3_1 | ConvBNReLU 3*3 512 same | N * 512 * 8 * 8 | |
| N * 512 *8 * 8 | down_sample_3_2 | ConvBNReLU 3*3 512 same | N * 512 * 8 * 8 | |

通过encode部分返回down_sample_3_2 和 [y0,y1,y2,y3]

> padding = 'same' 输出的宽和高不变

##### decode 部分

通过上采样进行像素的分类

down_sample_3_2 = [4, 512, 8, 8]
y3 = [4, 512, 16, 16]

1、当use_deconv=True 时通过反卷积上采样，否则通过线性插值上采样

```
x = F.interpolate(down_sample_3_2, ... mode='bilinear',...)
```
2、通过paddle.concat 沿通道联结

```
output = paddle.concat([x, y3], axis=1)
# [4, 1024, 16, 16]
```
3、再进行如下卷积

| input | name | Operator | output| 
| --- | --- | --- | ---| 
| output | double_conv0 | ConvBNReLU 3*3 256 same  | 4 * 256 *16 * 16 |
| 4 * 256 *16 * 16 | double_conv1 | ConvBNReLU 3*3 256 same  | 4 * 256 *16 * 16 | 

输出【4,256,16,16】 和 y2 = [4, 256, 32, 32 ] 一并作为输入再次进行如上步骤 1,2 
输出 [4, 512, 32, 32]

再进行如下卷积

| input | name | Operator | output| 
| --- | --- | --- | ---| 
| output | double_conv0 | ConvBNReLU 3*3 128 same  | 4 * 128 *32 * 32 | 
| 4 * 128 *32 * 32 | double_conv1 | ConvBNReLU 3*3 128 same  | 4 * 128 *32 * 32 | 


输出【4,128,32,32] 和 y1 = [4, 128, 64, 64 ] 一并作为输入再次进行如上步骤 1,2 
输出 [4, 256, 64, 64]

再进行如下卷积

| input | name | Operator | output| 
| --- | --- | --- | ---| 
| output | double_conv0 | ConvBNReLU 3*3 64 same  | 4 * 64 *64 * 64 | 
| 4 * 128 *32 * 32 | double_conv1 | ConvBNReLU 3*3 64 same  | 4 * 64 *64 * 64 | 


输出【4,64,64,46] 和 y0 = [4, 64, 128, 128 ] 一并作为输入再次进行如上步骤 1,2 
输出 [4, 128, 128, 128]

再进行如下卷积

| input | name | Operator | output| 
| --- | --- | --- | ---| 
| output | double_conv0 | ConvBNReLU 3*3 64 same  | 4 * 64 *128 * 128 | 
| 4 * 128 *32 * 32 | double_conv1 | ConvBNReLU 3*3 64 same  | 4 * 64 *128 * 128 | 
