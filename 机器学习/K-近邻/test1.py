import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics.cluster import contingency_matrix


n_samples = 1500
random_state = 170
transformation = [[0.60834549, -0.63667341], [-0.40887718, 0.85253229]]

X, y = make_blobs(n_samples=n_samples, random_state=random_state)
X_aniso = np.dot(X, transformation)  # Anisotropic blobs
X_varied, y_varied = make_blobs(
    n_samples=n_samples, cluster_std=[1.0, 2.5, 0.5], random_state=random_state
)  # Unequal variance
X_filtered = np.vstack(
    (X[y == 0][:500], X[y == 1][:100], X[y == 2][:10])
)  # Unevenly sized blobs
y_filtered = [0] * 500 + [1] * 100 + [2] * 10


print(X.shape)


fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))

axs[0, 0].scatter(X[:, 0], X[:, 1], c=y)   #   x, y  color
axs[0, 0].set_title("Mixture of Gaussian Blobs")

axs[0, 1].scatter(X_aniso[:, 0], X_aniso[:, 1], c=y)
axs[0, 1].set_title("Anisotropically Distributed Blobs")

axs[1, 0].scatter(X_varied[:, 0], X_varied[:, 1], c=y_varied)
axs[1, 0].set_title("Unequal Variance")

axs[1, 1].scatter(X_filtered[:, 0], X_filtered[:, 1], c=y_filtered)
axs[1, 1].set_title("Unevenly Sized Blobs")

# plt.suptitle("Ground truth clusters").set_y(0.95)
# plt.show()



from sklearn.cluster import KMeans, k_means

common_params = {
    "init": "k-means++",  # default
    "n_init": "auto",
    "random_state": 170,
}

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))

# n_clusters 指定要形成的簇的数量以及要生成的质心 默认8  即K = 8 
# max_iter  k-means算法单次运行的最大迭代次数  默认300
# n_init=5 独立随机初始化n_init的运行次数, 对于稀疏的高维问题，建议进行多次运行
## 当' n_init='auto' '时，运行的次数取决于init的值:如果使用' init='random' '或' init '是可调用的，
## 则为10; 如果使用' init='k-means++' '或' init '是类似数组的,则为1
y_pred = KMeans(n_clusters=3, **common_params).fit_predict(X)
# y_pred = KMeans(init="k-means++", n_clusters=2, n_init=4, random_state=0).fit_predict(X)
print(y_pred, y_pred.shape)
print(np.unique(y_pred))
axs[0, 0].scatter(X[:, 0], X[:, 1], c=y_pred)
axs[0, 0].set_title("Non-optimal Number of Clusters")


y_pred = KMeans(n_clusters=3, **common_params).fit_predict(X_aniso)
axs[0, 1].scatter(X_aniso[:, 0], X_aniso[:, 1], c=y_pred)
axs[0, 1].set_title("Anisotropically Distributed Blobs")


y_pred = KMeans(n_clusters=3, **common_params).fit_predict(X_varied)
axs[1, 0].scatter(X_varied[:, 0], X_varied[:, 1], c=y_pred)
axs[1, 0].set_title("Unequal Variance")

y_pred = KMeans(n_clusters=3, **common_params).fit_predict(X_filtered)
axs[1, 1].scatter(X_filtered[:, 0], X_filtered[:, 1], c=y_pred)
axs[1, 1].set_title("Unevenly Sized Blobs")


# y_pred = KMeans(n_clusters=3, n_init=10, random_state=random_state).fit_predict(
#     X_filtered
# )

# plt.scatter(X_filtered[:, 0], X_filtered[:, 1], c=y_pred)






# X = np.array([[1, 2], [1, 4], [1, 0],
#         [10, 2], [10, 4], [10, 0]])
# kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(X)
# print(kmeans.labels_)

# kmeans.predict([[0, 0], [12, 3]])
# kmeans.cluster_centers_

# axs[0, 1].scatter(X[:, 0], X[:, 1], c=[1, 1, 1, 0, 0, 0])
# axs[0, 1].set_title("2222")


plt.suptitle("Unexpected KMeans clusters").set_y(0.95)
plt.show()