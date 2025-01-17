

#### 描述

GeoDjango打算成为一个世界级的地理网络框架。它的目标是尽可能容易地构建GIS网络应用程序，利用空间数据的强大功能

GeoDjango是Django的一个包含的contrib模块，它把它变成了一个世界级的地理网络框架。GeoDjango努力让创建地理网络应用程序变得尽可能简单，比如基于位置的服务。

它的功能包括

- Django为OGC（开放地理空间联盟）几何图形和栅格数据提供建模字段。 
- 对Django ORM的扩展，用于查询和操作空间数据
-  松耦合的高级Python接口，用于GIS几何图形和光栅操作以及不同格式的数据操作
-  后台管理编辑几何图形字段

####  安装

- django4.0 
- postgis13 （docker安装包括依赖GEOS、PROJ和GDAL等）
- psycopg2: 当将GeoDjango与PostGIS结合使用时，psycopg2模块需要用作数据库适配器 
- GDAL-3.2.3-cp38-cp38-win_amd64.whl （for windows development  包括了proj，geos） 

#### 创建空间数据库

```
$ createdb  wgis
$ psql wgis
wgis=# CREATE EXTENSION postgis;
CREATE EXTENSION
wgis=# CREATE EXTENSION postgis_raster;
CREATE EXTENSION
```

#### 创建项目

```
django-admin startproject wgis
cd wgis
$ python manage.py startapp apps
```

#### 配置settings

```
INSTALLED_APPS = [
    'django.contrib.admin',
	 ...
    'django.contrib.gis',  # # 启用GIS模块
    'apps',
]

## gis库连接
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'wgis',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}
```

#### 获取地理数据（.shp）

```
wget https://thematicmapping.org/downloads/TM_WORLD_BORDERS-0.3.zip

$ ogrinfo world/data/TM_WORLD_BORDERS-0.3.shp
INFO: Open of `world/data/TM_WORLD_BORDERS-0.3.shp'
      using driver `ESRI Shapefile' successful.
1: TM_WORLD_BORDERS-0.3 (Polygon) # shapefile有一个名称为TM_WORLD_BORDERS-0.3图层，这个图层包含多边形数据
# 指定层名，并使用-so选项来获取重要的属性信息
$ ogrinfo -so world/data/TM_WORLD_BORDERS-0.3.shp TM_WORLD_BORDERS-0.3
```

#### 根据属性定义模型

```
# 默认WGS84（4326）
# https://docs.djangoproject.com/en/4.0/ref/contrib/gis/tutorial/#defining-a-geographic-model
class WorldBorder(models.Model):
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField("United Nations Code")
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()
    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    def __str__(self):
        return self.name
```

#### 迁移

```
# 创建表
>python manage.py makemigrations
>python manage.py sqlmigrate apps 0001  # 打印创建表语句
>python manage.py  migrate    
```

#### 导入数据

- 通过工具导入
  - ogr2ogr 
  - shp2pgsql

-  GeoDjango 接口

   1. 手动创建load.py文件，使用LayerMapping函数

      ```
      from django.contrib.gis.utils import LayerMapping
      from .models import WorldBorder
      
      shp_file = r"G:\TM_WORLD_BORDERS-0.3\TM_WORLD_BORDERS-0.3.shp"
      world_mapping = {
          'fips' : 'FIPS',
          'iso2' : 'ISO2',
          'iso3' : 'ISO3',
          'un' : 'UN',
          'name' : 'NAME',
          'area' : 'AREA',
          'pop2005' : 'POP2005',
          'region' : 'REGION',
          'subregion' : 'SUBREGION',
          'lon' : 'LON',
          'lat' : 'LAT',
          'mpoly' : 'MULTIPOLYGON',
      }
      
      def run(verbose=True):
          lm = LayerMapping(WorldBorder, shp_file, world_mapping, transform=False)
          lm.save(strict=True, verbose=verbose)
      ```

      world_mapping字典中的每个键都对应于`WorldBorder`模型中的一个字段，值是将从中加载数据的shapefile字段的名称

      transform关键字被设置为False，因为shapefile中的数据不需要转换

      ```
      >>> from world import load
      >>> load.run()
      ```

  2. 使用命令`ogrinspect`  自动生成模型定义和LayerMapping字典

     ```
     python manage.py ogrinspect TM_WORLD_BORDERS-0.3.shp WorldBorder \
         --srid=4326 --mapping --multi
     ```

     ```
     - srid=4326选项设置地理字段的srid- mapping选项告诉ogrinspect也生成一个映射字典，用于LayerMapping- multi选项被指定，这样地理字段是一个MultiPolygonField而不是一个PolygonField
     ```

     	- srid=4326选项设置地理字段的srid
     	- mapping选项告诉ogrinspect也生成一个映射字典，用于LayerMapping
     	- multi选项被指定，这样地理字段是一个MultiPolygonField而不是一个PolygonField

####  Admin

- GISModelAdmin

  GeoDjango在管理中使用了一个OpenStreetMap层。这提供了更多的背景信息(包括街道和通道的细节)

```
admin.site.register(WorldBorder, admin.GISModelAdmin)
```

- GeoModelAdmin

  srid = 4326

````
admin.site.register(WorldBorder, admin.GeoModelAdmin)
````

- OSMGeoAdmin

​       srid = 3857

#### 错误

ImportError: Could not find the GEOS library (tried "geos_c", "libgeos_c-1"). Try setting GEOS_LIBRARY_PATH in your settings.

```
GDAL_LIBRARY_PATH = "D:\\xx\\osgeo\\gdal302"   # 安装路劲
GEOS_LIBRARY_PATH = r"D:\xxx\osgeo\geos_c"
```

GDAL_ERROR 1: b'PROJ: proj_create_from_database: Cannot find proj.db'

```
os.environ['PROJ_LIB'] = r"D:\ProgramData\wgis_env\Lib\site-packages\osgeo\data\proj"
```

#### 相关连接

https://docs.djangoproject.com/en/4.0/ref/contrib/gis/install/postgis/

https://docs.djangoproject.com/en/4.0/ref/contrib/gis/install/#windows

https://docs.djangoproject.com/en/4.0/ref/contrib/gis/tutorial/

