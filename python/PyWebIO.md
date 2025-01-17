PyWebIO提供了一系列的命令函数来获取用户在浏览器上的输入和输出，将浏览器变成了一个“富文本终端”，可以用来构建简单的web应用程序或基于浏览器的GUI应用程序，而不需要具备HTML和JS的知识。PyWebIO还可以轻松集成到现有的Web服务中。PyWebIO非常适合快速构建不需要复杂UI的应用程序



使用`PyWebIO.platform.Django.webio_view()`获取视图函数，在Django中运行PyWebIO应用程序

```
from django.urls import path
from pywebio.platform.django import webio_view

# `task_func` is PyWebIO task function
webio_view_func = webio_view(task_func)

urlpatterns = [
    path(r"tool", webio_view_func),
]
```



#### 柱状图

```
def bar1():
    c = (
        Bar()
            .add_xaxis(Faker.choose())
            .add_yaxis("商家A", Faker.values(), category_gap="80%")  # category_gap 柱之间的空隙默认20%
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-单系列柱间距离"))
    )
    c.width = "100%"
    return put_html(c.render_notebook())
```

![1648433057337](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1648433057337.png)

```
c = (
        Bar()
            .add_xaxis(Faker.choose())
            .add_yaxis("商家A", Faker.values())
            .add_yaxis("商家B", Faker.values())
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-MarkPoint（指定类型）"))
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),  # 不显示label
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                    opts.MarkPointItem(type_="average", name="平均值"),
                ]
            ),
        )

    )
```

![1648433158395](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1648433158395.png)

**Bar-堆叠数据**

```
c = (
    Bar()
    .add_xaxis(Faker.choose())
    .add_yaxis("A", Faker.values(), stack="stack1")
    .add_yaxis("B", Faker.values(), stack="stack1")   # A,B 堆叠
    .add_yaxis("C", Faker.values())
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(title_opts=opts.TitleOpts(title="Bar-堆叠数据（部分）"))
)
```

**Y 轴 formatter**

```
.set_global_opts(
        title_opts=opts.TitleOpts(title="Bar-Y 轴 formatter"),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} /月")),
    )
```

**显示 ToolBox**

```
.set_global_opts(
	title_opts=opts.TitleOpts(title="Bar-显示 ToolBox"),
	toolbox_opts=opts.ToolboxOpts(),   # Toolbox
	legend_opts=opts.LegendOpts(is_show=False),
)
```

#### 词云

```
    c = (
        WordCloud()
            # word_size_range: 单词字体大小范围
            .add("", words,
                 word_size_range=[6,66],
                 shape='circle',    # 形状 diamond、rect、cardioid
                 textstyle_opts=opts.TextStyleOpts(font_family="cursive"))  # 自定义字体
            .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud"))
    )
```









https://pywebio-charts.pywebio.online/?app=plotly

https://pywebio-demos.pywebio.online/