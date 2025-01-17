Django使用它的GeoDjango模块，将地理数据存储在PostgreSQL数据库中，在该数据库上运行PostGIS的地理空间查询



#### 增加一个模板视图

```
# apps/views.py
from django.views.generic.base import TemplateView

class TestView(TemplateView):
    """for test"""
    template_name = "test_map.html"
    
```

`templates/test_map.html`

```
<!doctype html>
<html lang="en">
<head>
    <title>Markers Map</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
</body>
</html>
```

`apps/urls.py`

```
from .views import TestView

urlpatterns = [
    path("map/", TestView.as_view())
]
# wgis/urls.py
# urlpatterns = [
#    path('apps/', include("apps.urls")),
# ]
```

#### 测试空白地图页

```
python3 manage.py runserver
```

现在服务器已经运行，用您的Web浏览器访问http://127.0.0.1:8000/apps/map/。您将看到一个可用的空白地图页面

#### leaflet

Leaflet 是一个为移动设备设计的交互式地图的开源的 javascript库， 并只有38k，包含了大多数开发者需要的地图特点

#### 更新模板

要使用Leaflet，我们需要在模板中链接它的JavaScript和CSS模块

```
{% load static %}
<!doctype html>
<html lang="en">
<head>
    <title>Markers Map</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="{% static 'map.css' %}">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css">   # 样式
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
</head>
<body>
    <div id="map"></div>
    <script src="{% static 'map.js' %}"></script>
</body>
</html>

```

`static/map.css`  自定义一些样式

```
html, body {
    height: 100%;
    margin: 0;
}
#map {
    width: 100%;
    height: 100%;
}
```

`static/map.js`

```
const copy = "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors";
const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osm = L.tileLayer(url, { attribution: copy });
const map = L.map("map", { layers: [osm] });
map.fitWorld(); # 设置一个地图视图，该视图主要包含整个世界和可能的最大缩放级别
```

使用已定义的变量，我们初始化一个OpenStreetMap层，并将其挂接到我们的“map”上。

现在服务器已经运行，用您的Web浏览器访问http://127.0.0.1:8000/apps/map/。您将看到一个“标记地图”页面，其中包含一个完整的页面地图

![1646103781768](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1646103781768.png)



#### 增加标记（点状数据）

现在我们可以向地图添加一些标记

`apps/models.py`

```
class Marks(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField()   # 点状类型
```

#### 添加到admin

```
@admin.register(Marks)
class ShopAdmin(admin.OSMGeoAdmin):    
	list_display = ("name", "location")
```

#### 添加数据

```
>python manage.py  makemigrations
>python manage.py  migrate
>python manage.py createsuperuser  # 创建管理员用户
```

运行服务，通过http://127.0.0.1:8000/admin/apps/marks/add/添加一些标记点

![1646104388321](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1646104388321.png)



#### 在前端显示添加的标记点

我们通过EAST api接口返回数据，安装Django REST Framework

`wgis/requirements.txt`

```
djangorestframework
djangorestframework-gis
django-filter
```

`wgis/settings.py`

```
INSTALLED_APPS = [
    "django.contrib.admin",
	 ...
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "apps",
]
```

##### serializer

`apps/serializers.py`

```
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from apps.models import Marks

class MarkSerializer(GeoFeatureModelSerializer):
    class Meta:
        fields = ("id", "name")
        geo_field = "location"
        model = Marks
```

**viewset**

```
from rest_framework import viewsets
from rest_framework_gis import filters
from .models import Marks
from .serializers import MarkSerializer


class MarkViewSet(viewsets.ReadOnlyModelViewSet):
    bbox_filter_field = 'location'

    serializer_class = MarkSerializer
    filter_backends = filters.InBBoxFilter
    queryset = Marks.objects.all()
```

**配置url**

`apps/urls.py`

```
from rest_framework import routers
from apps.viewsets import MarkViewSet
from django.urls import path
from .views import TestView

urlpatterns = [
    path("map/", TestView.as_view())
]

routers = routers.DefaultRouter()
routers.register(r"api/marks", MarkViewSet)

urlpatterns += routers.urls
```

**更新JS**

`static/map.js`

```
const copy = "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors";
const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osm = L.tileLayer(url, { attribution: copy });
const map = L.map("map", { layers: [osm], minZoom: 5 });
 map.setView([32,106], 5)

async function load_markers() {
    const markers_url = `/apps/api/marks/?in_bbox=${map.getBounds().toBBoxString()}`
    const response = await fetch(markers_url)
    const geojson = await response.json()
    return geojson
}
async function render_markers() {
    const markers = await load_markers();
    L.geoJSON(markers)
    .bindPopup((layer) => layer.feature.properties.name)
    .addTo(map);
}
map.on("moveend", render_markers);
```

浏览器访问http://127.0.0.1:8000/apps/map/。您将看到“标记地图”页面，其中包含一个完整的页面地图和所有标记

![1646119771860](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1646119771860.png)