元光栅格式(MRF)是一种图像和数据存储格式，旨在快速访问离散分辨率的地理参考瓦片金字塔中的图像

![](D:\u\机器学习\img\pyramids.png)



该格式支持非常大的、平铺的、多分辨率和多光谱数据。支持稀疏的栅格数据。JPEG(有损)和PNG(无损)压缩每个平铺目前是支持的。支持灰度、颜色、索引(调色板)颜色模型

这种文件格式最初是由美国宇航局喷气推进实验室开发的

MRF由元数据、数据和索引文件组成，扩展名分别为:. `mrf、.ppg/pjg and .idx`。

#### MRF元数据文件(.mrf)

头XML元数据文件，包含关于用于GDAL日常的图像的描述性信息。所有瓦片存储相同的元数据集。

```
MRF_META: root node
    Raster: image metadata
        Size: size of overview
        Compression: JPEG, PNG, PPNG (Paletted-PNG)
        Quality: image quality
        PageSize: dimension of tiles
    Rsets: single image or uniform scaling factor
    GeoTags: 
        BoundingBox: bounding box for imagery
```

> mod_onearth使用了其它定制元素

```
<MRF_META>
    <Raster>
        <Size x="81920" y="40960" c="1" />
        <Compression>PPNG</Compression>
        <DataValues NoData="0" />
        <Quality>85</Quality>
        <PageSize x="512" y="512" c="1" />
    </Raster>
    <Rsets model="uniform" />
    <GeoTags>
        <BoundingBox minx="-180" miny="-90" maxx="180" maxy="90" />
    </GeoTags>
</MRF_META> 
```

#### MRF数据文件(.ppg/.pjg)

png (ppg)或jpeg (pjg)数据文件包含连接的图像块。每个块都是一个自包含的图像，可以是PNG或JPEG。首先是金字塔的完全分辨率基础，然后是任何后续的金字塔层次。数据文件消除了将tiles存储在独立文件中的需求，从而最小化了文件系统操作并显著提高了性能

![](D:\u\机器学习\img\tiledata.png)

支持RGB和索引颜色。对文件的修改只能通过追加完成。使用mod_onearth时，文件以一个空的平铺开始

#### MRF索引文件(.idx)

索引文件包含一个MRF (ppg/pjg)数据文件中指向单个块的有空间组织的指针。块通过数据文件中的偏移量和块的大小(都是64位整数)来引用。瓦片有一个左上角的原点。索引是固定大小的，并且随着tile的修改而更新

![](D:\u\机器学习\img\tileidx.png)

