### Scikit-Learn中的k近邻算法

k近邻(KNN)算法是一种有监督的机器学习算法。KNN非常容易以其最基本的形式实现，但是执行相当复杂的分类任务。它是一个懒惰的学习算法，因为它没有专门的训练阶段。相反，它在分类新数据点或实例时使用所有数据进行培训。KNN是一种非参数学习算法，这意味着它对底层数据不做任何假设。这是一个非常有用的特性，因为现实世界中的大多数数据实际上并不遵循任何定理

在本文中，我们将看到如何使用Python的Scikit-Learn库实现KNN。

KNN理论 （详情[K-NN 近邻算法学习](http://192.168.9.169/article/k-nn-jin-lin-suan-fa-xue-xi/)）

KNN算法是所有监督机器学习算法中最简单的算法之一。它只是计算一个新数据点到所有其他训练数据点的距离。距离可以是任何类型的e。欧氏距离或曼哈顿等等。然后选择K最近的数据点，其中K可以是任意整数。最后，它将数据点分配给大多数K个数据点所属的类。



优点

1. 它非常容易实现
2. 如前所述，它是一种延迟学习算法，因此在进行实时预测之前不需要任何训练。这使得KNN算法比其他需要训练的算法要快得多。如 SVM 支持向量机、线性回归（linear regression）等
3. 由于该算法在进行预测之前不需要任何训练，因此可以无缝地添加新数据。
4. 实现KNN只需要两个参数，即K的值和距离函数(欧氏距离或曼哈顿等)



缺点

​	1、KNN算法在处理高维数据时，由于维数大，计算每个维的距离变得困难

​	2、KNN算法对大数据集具有较高的预测代价。这是因为在大型数据集中，计算新点与每个现有点之间距离的成本变得更高

​	3、最后，由于分类特征维间的距离难以确定，KNN算法不能很好地处理分类特征



#### 用Scikit-Learn实现KNN算法

在本节中，我们将看到如何使用Python的Scikit-Learn库在不到20行代码中实现KNN算法。

安装要求

```
Python (>= 3.5)
NumPy (>= 1.11.0)
SciPy (>= 0.17.0)
joblib (>= 0.11)
```

安装

```
pip install scikit-learn
```

#### 数据集

鸢尾花识别是一个经典的机器学习分类问题，它的数据样本中包括了4个特征变量，1个类别变量，样本总数为150。

　　它的目标是为了根据花萼长度（sepal length）、花萼宽度（sepal width）、花瓣长度（petal length）、花瓣宽度（petal width）这四个特征来识别出鸢尾花属于山鸢尾（iris-setosa）、变色鸢尾（iris-versicolor）和维吉尼亚鸢尾（iris-virginica）中的哪一种。

有关数据集的详细信息可以在这里找到 https://archive.ics.uci.edu/ml/machine-learning-databases/iris/

#### 导入库 \导入数据集

```    python
    url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'

    # 为数据集分配colum名称
    names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'Class']


    # 将数据集读取到panda dataframe
    dataset = pd.read_csv(url, names=names)
 	dataset.head()
```

执行上述脚本将显示数据集的前五行，如下所示:

```python
   sepal-length  sepal-width  petal-length  petal-width        Class
0           5.1          3.5           1.4          0.2  Iris-setosa
1           4.9          3.0           1.4          0.2  Iris-setosa
2           4.7          3.2           1.3          0.2  Iris-setosa
3           4.6          3.1           1.5          0.2  Iris-setosa
4           5.0          3.6           1.4          0.2  Iris-setosa
```

####  预处理

下一步是将数据集拆分为它的属性和标签，X变量包含数据集的前四列(即属性)，而y包含标签

```python
    X = dataset.iloc[:, :-1].values     #前四列
    y = dataset.iloc[:, 4].values   # 最后一项
```



#### 训练测试分割

为了避免过度拟合，我们将数据集分为训练和测试分割，这让我们更好地了解我们的算法在测试阶段是如何执行的。通过这种方法，我们的算法将在未见数据上进行测试，就像在生产应用程序中一样。

在得到训练数据集时，通常我们经常会把训练数据进一步拆分成训练集和验证集，这样有助于我们模型参数的选取。train_test_split是交叉验证中常用的函数，功能是从样本中随机的按比例选取train data和testdata，形式为

```python
X_train,X_test, y_train, y_test =
cross_validation.train_test_split(train_data,train_target,test_size=0.4, random_state=0)
```

执行如下脚本

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
```

上面的脚本将数据集分为80%的训练数据和20%的测试数据。这意味着在150条记录中，训练集将包含120条记录，而测试集包含其中的30条记录

####  特征缩放

在进行任何实际预测之前，最好先对特性进行伸缩，以便对所有特性进行统一的评估 

梯度下降算法(用于神经网络训练和其他机器学习算法)具有归一化特征，收敛速度更快。下面的脚本执行特性缩放

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)
```

> StandardScaler计算训练集的平均值和标准差，以便测试数据及使用相同的变换,变换后各维特征有0均值，单位方差，也叫z-score规范化（零均值规范化），计算方式是将特征值减去均值，除以标准差  即z = (x - u) / s 
>
> 　　其中u是训练样本的均值，如果with_mean=False,则为0
>
> 　　s是训练样本的标准偏差，如果with_std=False,则为1
>
> **fit**
>
> 　　用于计算训练数据的均值和方差，后面就会用均值和方差来转换训练数据
>
> **fit_transform**
>
> 　　不仅计算训练数据的均值和方差，还会基于计算出来的均值和方差来转换训练数据，从而把数据转化成标准的正态分布。
>
> **transform**
>
> 　　很显然，它只是进行转换，只是把训练数据转换成标准的正态分布。（一般会把train和test集放在一起做标准化，或者在train集上做标准化后，用同样的标准化器去标准化test集，此时可以使用scaler)。

#### 训练和预测

训练KNN算法并使用它进行预测是非常直接的，尤其是在使用Scikit-Learn时

```python
from sklearn.neighbors import KNeighborsClassifier
classifier = KNeighborsClassifier(n_neighbors=5)
classifier.fit(X_train, y_train)
```

第一步是从sklearn导入KNeighborsClassifier类,在第二行中，这个类用一个参数初始化```n_neigbours```使用邻居的数目-这就是K的值,K没有理想值，是经过测试和评估后选择的,然而，从一开始，5似乎是KNN算法中最常用的值

最后一步是对测试数据进行预测。为此，执行以下脚本

```python
y_pred = classifier.predict(X_test)
```



#### 评估算法

对于算法的评价，混淆矩阵、精确度、召回率和f1_score是最常用的指标, sklearn.metrics的confusion_matrix和classification_report方法。度量可以用来计算这些度量

```python
from sklearn.metrics import classification_report, confusion_matrix
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

> confusion_matrix（混淆矩阵）
>
> ```python
> >>> ``from` `sklearn.metrics import confusion_matrix
> >>> y_true = [2, 0, 2, 2, 0, 1]
> >>> y_pred = [0, 0, 2, 2, 0, 2]
> >>> confusion_matrix(y_true, y_pred)
> array([[2, 0, 0],
>        ``[0, 0, 1],
>        ``[1, 0, 2]])
> ```

> - 正确率 —— 提取出的正确信息条数 / 提取出的信息条数
> - Precision	精准度/查准率  TP /（TP+FP）预测出为阳性的样本中，正确的有多少
> - Recall	召回率/查全率 —— TP/（TP+FN） 正确预测为阳性的数量占总样本中阳性数量的比例
> - F 值 —— 正确率 * 召回率 * 2 / （正确率 + 召回率）（F值即为正确率和召回率的调和平均值）

上面脚本的输出如下

```
[[11  1  0]
 [ 0 10  0]
 [ 0  0  8]]
                 precision    recall  f1-score   support

    Iris-setosa       1.00      0.92      0.96        12
Iris-versicolor       0.91      1.00      0.95        10
 Iris-virginica       1.00      1.00      1.00         8

       accuracy                           0.97        30
      macro avg       0.97      0.97      0.97        30
   weighted avg       0.97      0.97      0.97        30
```



#### 比较错误率与K值

在训练和预测部分，我们说过，没有办法事先知道K的哪个值在第一次测试中产生最好的结果。我们随机选择5作为K值，结果是97%的正确率

帮助您找到K的最佳值的一种方法是绘制K值的图以及数据集的相应错误率

在本节中，我们将绘制所有K值在1到40之间的测试集预测值的平均误差

为此，我们首先计算K从1到40的所有预测值的误差均值。执行以下脚本:

```python
error = []

# Calculating error for K values between 1 and 40
for i in range(1, 40):
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error.append(np.mean(pred_i != y_test))
```

上面的脚本执行一个从1到40的循环。每次迭代都计算出测试集预测值的平均误差，并将结果附加到误差列表中

下一步是根据K值绘制错误值。执行以下脚本创建情节:

```python
plt.figure(figsize=(12, 6))
plt.plot(range(1, 40), error, color='red', linestyle='dashed', marker='o',
         markerfacecolor='blue', markersize=10)
plt.title('Error Rate K Value')
plt.xlabel('K Value')
plt.ylabel('Mean Error')
```



![](C:\Users\Administrator\Desktop\机器学习\img\20190911171211.png)

从输出可以看出，当K值在4、6、7到11-15之间时，平均误差最低。我建议你们尝试一下K的值看看它是如何影响预测的准确性的。

#### 总结

KNN是一种简单但功能强大的分类算法。它不需要进行预测训练，而预测通常是机器学习算法中最困难的部分之一。KNN算法已广泛应用于文档相似度和模式识别。它还被用于开发推荐系统，并用于计算机视觉的降维和预处理步骤，特别是人脸识别任务。

从这里开始，我建议您为不同的分类数据集实现KNN算法。改变测试和训练的大小以及K值，看看结果如何不同，以及如何提高算法的准确性。[这里](https://archive.ics.uci.edu/ml/datasets.php)有一个很好的分类数据集集合供您使用。

您还将KNN算法应用于哪些其他应用程序?结果怎么样?请在评论中告诉我们!

