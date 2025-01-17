#### GDALRaster

GDALRaster是GDAL栅格源对象的包装器，它支持使用一致的接口从各种GDAL支持的地理空间文件格式和数据源读取数据。每个数据源都由一个GDALRaster对象表示，该对象包含一个或多个名为波段的数据层。每个波段，由一个GDALBand对象表示，包含地理参考图像数据

*class* `GDALRaster`(*ds_input*, *write=False*)

GDALRaster的构造函数接受两个参数。第一个参数定义光栅源，第二个参数定义光栅是否应该以写模式打开。对于新创建的栅格，第二个参数被忽略，新的栅格总是以写模式创建

```
>>> from django.contrib.gis.gdal import GDALRaster
>>> rst = GDALRaster('/path/to/your/raster.tif', write=False)  # 指定文件只读打开
>>> rst.name  # 文件名
'D:\\demo\\add_color\\SA.tif'
>>> rst.width, rst.height  # 这个文件有7560 x 4320像素  以像素为单位(x轴，y轴)
(7560, 4320)
```

**name**  在实例化时提供的名称或输入文件路径

```
>>> GDALRaster({'width': 10, 'height': 10, 'name': 'myraster', 'srid': 4326}).name
'myraster'
# 如果实例化没有name 则为‘’
```

**driver**  用于处理输入文件的GDAL驱动程序的名称。对于从文件创建的GDALRasters，驱动程序类型是自动检测的。默认情况下，创建的光栅是内存光栅('MEM')

```
>>> rst.driver.name
'GTiff
>>> GDALRaster({'width': 10, 'height': 10, 'srid': 4326}).driver.name
'MEM'
```

**srs** 光栅的空间参考系统，作为一个空间参考实例

```
>>> rst.srs
<django.contrib.gis.gdal.srs.SpatialReference object at 0x000002CC472A7E80>
# 光栅的空间参考系统标识(SRID)。这个属性是通过srs属性获取或设置SRID
>>> rst.srs.srid
4326
from django.contrib.gis.gdal import srs
>>> wgs84 = srs.SpatialReference('WGS84') # shorthand string
>>> wgs84 = srs.SpatialReference(4326) # EPSG code
>>> wgs84 = srs.SpatialReference('EPSG:4326') # EPSG string
>>> rst.srs =  srs.SpatialReference(3857) # 写模式打开才能设置srs
>>> rst.srs.srid
3857
```

**geotransform** 用于对源进行地理参考的仿射变换矩阵，是一个由六个系数组成的元组。 默认`[0.0, 1.0, 0.0, 0.0, 0.0, -1.0]`.

```
>>> rst.geotransform
[0.0, 1.0, 0.0, 0.0, 0.0, -1.0]
>>> rst = GDALRaster(r'D:\demo\add_color\SA.tif', write=False)
>>> rst.geotransform
[73.004166, 0.008333300000000002, 0.0, 53.995834, 0.0, -0.008331404166666667]
# 索引0和3 为原点坐标（origin）  索引1和5为缩放比例（scale） 索引2和4 倾斜系数（skew）
```

**origin**在源的空间参考系统中，光栅的左上角的坐标，具有x和y成员的点对象

```
>>> rst.origin
[73.004166, 53.995834]
```

**scale** 用于栅格地理参考的像素宽度和高度，具有x和y成员的点对象

```
>>> rst.scale
[0.008333300000000002, -0.008331404166666667]
```

**extent** 栅格源的范围(边界值)，在源的空间参考系统中为4元组(xmin, ymin, xmax, ymax)

```
>>> rst.extent
(73.004166, 18.004168, 136.003914, 53.995834)

>>> rst = GDALRaster({'width': 10, 'height': 20, 'srid': 4326})
>>> rst.extent
(0.0, -20.0, 10.0, 0.0)
```

**bands**  源的所有波段列表，GDALBand实例

```
>>> rst = GDALRaster(r'D:\demo\add_color\SA.tif', write=False)
>>> len(rst.bands)
1
>>> rst = GDALRaster({"width": 1, "height": 2, 'srid': 4326,"bands": [{"data": [0, 1]}, {"data": [2, 3]}]})
>>> len(rst.bands)
2
>>> rst.bands[1].data()
array([[2.],
       [3.]], dtype=float32)
```

**warp** `(ds_input, resampling='NearestNeighbour', max_error=0.0)`

返回此光栅的变形版本,即按照重新采样方法(`NearestNeighbor`)转换投影  类似命令`gdalwarp`

```
>>> rst = GDALRaster({"width": 6, "height": 6, "srid": 3086,"origin": [500000, 400000],"scale": [100, -100],"bands": [{"data": range(36), "nodata_value": 99}]})
>>> rst.bands[0].data()
array([[ 0.,  1.,  2.,  3.,  4.,  5.],
       [ 6.,  7.,  8.,  9., 10., 11.],
       [12., 13., 14., 15., 16., 17.],
       [18., 19., 20., 21., 22., 23.],
       [24., 25., 26., 27., 28., 29.],
       [30., 31., 32., 33., 34., 35.]], dtype=float32)
>>> target = rst.warp({"scale": [200, -200], "width": 3, "height": 3})
>>> target.bands[0].data()
array([[ 7.,  9., 11.],
       [19., 21., 23.],
       [31., 33., 35.]], dtype=float32)
```

**transform**(*srs*, *driver=None*, *name=None*, *resampling='NearestNeighbour'*, *max_error=0.0*)

将这个光栅转换为一个不同的空间参考系统(srs),转换坐标系 如4326到3857转换

默认的重采样算法是NearestNeighbour，但可以使用重采样参数进行更改。默认的重采样允许的最大错误值是0.0，可以使用max_error参数来更改

```
>>> target_srs  = srs.SpatialReference(4326)
>>> target = rst.transform(target_srs)
>>> target.origin
[-82.98492744885777, 27.601924753080162]
```

**info** 返回带有光栅摘要的字符串。相当于gdalinfo命令行实用程序

**metadata **栅格的元数据

```
>>> rst = GDALRaster(r'D:\demo\add_color\SA.tif', write=False)
>>> rst.metadata
{'IMAGE_STRUCTURE': {'INTERLEAVE': 'BAND'}, 'DERIVED_SUBDATASETS': {'DERIVED_SUBDATASET_1_NAME': 'DERIVED_SUBDATASET:LOGAMPLITUDE:D:\\demo\\add_color\\SA.tif', 'DERIVED_SUBDATASET_
1_DESC': 'log10 of amplitude of input bands from D:\\demo\\add_color\\SA.tif'}}
>>> rst.metadata = {'DEFAULT': {'OWNER': None, 'VERSION': '2.0'}} # 写模式下更新元数据
>>> rst.metadata
{'DEFAULT': {'VERSION': '2.0'}}
```

**vsi_buffer**  这个光栅的字节表示。对于没有存储在GDAL的虚拟文件系统中的光栅，返回None

**is_vsi_based** 一个布尔值，指示该光栅是否存储在GDAL的虚拟文件系统中

  

#### GDALBand

GDALBand实例不是显式创建的，而是通过GDALRaster对象的bands属性获得的。gdalband包含光栅的实际像素值

- description  波段的描述信息 

- height Y-axis  像素

- width  X-axis

- pixel_count  在这个波段内的总像素数。等于宽*高。

- min   （不包括nodata）

- max  （不包括nodata）

- mean  （不包括nodata）

- std   标准差 （不包括nodata）

- nodata_value   no data 值用于标记那些不是有效数据的像素

- datatype()  带中包含的数据类型，作为0 (Unknown)到11之间的整数常量

- color_interp()  波段的颜色映射，为0到16之间的整数

- data(*data=None*, *offset=None*, *size=None*, *shape=None*) GDALBand的像素值访问器。如果没有提供参数，则返回完整的数据数组。可以通过指定偏移量和块大小作为元组来请求像素数组的子集。

  ```
  >>> rst = GDALRaster({'width': 4, 'height': 4, 'srid': 4326, 'datatype': 1, 'nr_of_bands': 1, 'bands':[{'data': range(16)}]})
  >>> rst.bands[0].data()
  array([[ 0,  1,  2,  3],
         [ 4,  5,  6,  7],
         [ 8,  9, 10, 11],
         [12, 13, 14, 15]], dtype=uint8)
  >>> rst.bands[0].data(offset=(1,1), size=(2,2))   # 部分读取
  array([[ 5,  6],
         [ 9, 10]], dtype=uint8)
  >>> bnd.data(data=[-1, -2, -3, -4], offset=(1, 1), size=(2, 2))  # 赋值
  >>> bnd.data()
  array([[ 0,  1,  2,  3],
         [ 4, -1, -2,  7],
         [ 8, -3, -4, 11],
         [12, 13, 14, 15]], dtype=int8)
  >>> bnd.data(range(4), shape=(1, 4))   # 用shape复制填充
  array([[0, 0, 0, 0],
         [1, 1, 1, 1],
         [2, 2, 2, 2],
         [3, 3, 3, 3]], dtype=uint8)
  ```

- metadata  波段元数据

#### 创建栅格文件

通过指定`ds_input`参数创建栅格文件。

当字典被传递给GDALRaster构造函数时，一个新的栅格被创建。字典包含新栅格的定义参数，如 `origin`, 大小或空间参考系统（srs）。字典还可以包含像素数据和关于新光栅格式的信息。因此，根据指定的驱动程序，生成的光栅可以是基于文件的，也可以是基于内存的

在字典或JSON风格中没有描述光栅数据的标准。因此，GDALRaster类的字典输入的定义是特定于Django的。它的灵感来自于geojson格式，但geojson标准目前仅限于矢量格式

ds_input字典中只需要几个键就可以创建一个栅格:`width`, `height`, and `srid`。所有其他参数都有默认值(参见下表)。可以在ds_input字典中传递的键列表与GDALRaster属性密切相关，但并不完全相同。许多参数直接映射到这些属性

| Key             | Default  | Usage                                                        |
| --------------- | -------- | ------------------------------------------------------------ |
| `srid`          | required |                                                              |
| `width`         | required |                                                              |
| `height`        | required |                                                              |
| `driver`        | `MEM`    |                                                              |
| `name`          | `''`     | 表示栅格名称的字符串。在创建基于文件的光栅时，此参数必须是新光栅的文件路径。如果名称以/vsimem/开头，则在GDAL的虚拟文件系统中创建光栅 |
| `origin`        | `0`      | Mapped to the [`origin`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster.origin) attribute |
| `scale`         | `0`      | Mapped to the [`scale`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster.scale) attribute |
| `skew`          | `0`      | Mapped to the [`width`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster.width) attribute |
| `bands`         | `[]`     | 带输入数据的band_input字典列表。得到的带索引与所提供的列表中相同。频带输入字典的定义如下。如果没有提供波段数据，栅格波段值将被实例化为一个零数组，并且“no data”值将设置为None |
| `nr_of_bands`   | `0`      | 表示栅格的频带数 ，不可改变                                  |
| `datatype`      | `6`      | 表示所有波段的数据类型的整数。默认为6 (Float32)              |
| `papsz_options` | `{}`     | 选项（值不区分大小写）                                       |

[详情参考](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#the-ds-input-dictionary)



GDAL可以访问存储在文件系统中的文件，但也支持虚拟文件系统来抽象访问其他类型的文件，如压缩的、加密的或远程文件

