#### 简介

开放地理空间联盟 (OGC) 的 Web 地图切片服务 (WMTS) 规范是一种在 web 上使用缓存图像切片提供数字地图时需遵守的国际规范。当您使用 ArcGIS Server 创建缓存地图或影像服务时，可通过 WMTS 规范自动访问该服务及其切片

WMTS提供了一种采用预定义图块方法发布数字地图服务的标准化解决方案。**WMTS弥补了WMS不能提供分块地图的不足。WMTS牺牲了提供定制地图的灵活性，代之以通过提供静态数据（基础地图）来增强伸缩性**，这些静态数据的范围框和比例尺被限定在各个图块内。这些固定的图块集使得对WMTS服务的实现可以使用一个仅简单返回已有文件的Web服务器即可，同时使得可以利用一些标准的诸如分布式缓存的网络机制实现伸缩性



#### 平铺金字塔

WMTS 使用瓦片矩阵集（Tile matrix set）来表示切割后的地图，如下图。瓦片就是包含地理数据的矩形影像，一幅地图按一定的瓦片大小被切割成多个瓦片，形成瓦片矩阵，一个或多个瓦片矩阵即组成瓦片矩阵集。不同的瓦片矩阵具有不同的分辨率，每个瓦片矩阵由瓦片矩阵标识符（一般为瓦片矩阵的序号，分辨率最低的一层为第0层，依次向上排）进行标识

![tile_pyramid](https://nasa-gibs.github.io/gibs-api-docs/img/tile_pyramid.png)



WMTS 的切片坐标系统和其组织方式可参考图

![image0](D:\u\机器学习\img\image095.jpg)

- 通过像素数来定义的每个瓦片的宽（TileWidth）和高（TileHeight），即瓦片的大小。GIBS目前提供的瓦片大小是512*512个像素；
- 边界框的左上角坐标（TileMatrixminX，TileMatrixmaxY）；
- 以瓦片为单位来定义的矩阵的宽（MatrixWidth）和高（MatrixHeight）
- 瓦片矩阵中的每个瓦片由瓦片的行（TileRow）列（TileCol）值进行标识，行列值分别从瓦片矩阵左上角点所在的瓦片开始算起，起始行列值是（0，0），依次向下向右增加

#### 瓦片编号

使用ZXY这样的坐标来精确定位一张瓦片。**即XY表示某个层级内的平面，X为横坐标，Y为纵坐标**，不同地图商定义有分歧

当 Zoom = 1时，切片如图所示

![1646726503106](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1646726503106.png)

由于像素为512x512，分辨率为0.5625， 512x0.5625=288 即每个Tile的长和宽都为288度，
Zoom = 1， 两个tile的左上坐标分别为（x，y）=（0，0），（1，0）  

tile: 1/0/0  tile: 1/1/0     x分为2部分 y为1  xy = 2

当 Zoom = 2时,每个Tile的长和宽都为144度,`x分为3部分，y分为2部分  xy = 6`

tile: 2/0/0  2/1/0  2/2/0 2/0/1 2/1/1 2/2/1

当 Zoom = 3时,每个Tile的长和宽都为144度,`x分为5部分，y分为3部分  xy = 15`

（EPSG:4326）投影分辨率为（512*512），每个像素最大0.5625度

| Resolution (per pixel) | Tile Matrix Set (WMTS) | Zoom Levels | 瓦片个数（X,Y） | Max Resolution (deg/pixel) | Min Resolution (deg/pixel) |
| ---------------------- | ---------------------- | ----------- | --------------- | -------------------------- | -------------------------- |
| 15.125m                | 15.125m                | 13          |                 | 0.5625                     | 0.0001373291015625         |
| 31.25m                 | 31.25m                 | 12          |                 | 0.5625                     | 0.000274658203125          |
| 250m                   | 250m                   | 9           | 320*160         | 0.5625                     | 0.002197265625             |
| 500m                   | 500m                   | 8           | 160*80          | 0.5625                     | 0.00439453125              |
| 1km                    | 1km                    | 7           | 80*40           | 0.5625                     | 0.0087890625               |
| 2km                    | 2km                    | 6           | 40*20           | 0.5625                     | 0.017578125                |
| 4km                    | 4km                    | 5           | 20*10           | 0.5625                     | 0.03515625                 |
| 8km                    | 8km                    | 4           | 10*5            | 0.5625                     | 0.0703125                  |
| 16km                   | 16km                   | 3           | 5*3             | 0.5625                     | 0.140625                   |
|                        |                        | 2           | 3*2             | 0.5625                     | 0.28125                    |
|                        |                        | 1           | 2*1             | 0.5625                     | 0.5625                     |

**Scale**

地球半径约为6370997米

unit = 2 * math.pi * 6370997 / 360 



**GIBS REST**

- *Pattern* - https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{*LayerIdentifier*}/default/{*Time*}/{*TileMatrixSet*}/{*TileMatrix*}/{*TileRow*}/{*TileCol*}.{*FormatExt*}

  - TileMatrix - 请求的贴图的贴图缩放级别(0..N)（注 从0开始）; Tile Matrix 决定大小
  - TileRow - 请求的贴图行Y (0..N) 从上到下
  - TileCol - 请求的贴图列X （0..N） 从左到右

     注：TileMatrix  = Zoom - 1 从0开始

**参考**

https://nasa-gibs.github.io/gibs-api-docs/access-basics/

http://webgis.cn/book/ch09-tiles/sec1-concept/section.html#id2