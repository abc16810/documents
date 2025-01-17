import graphviz
import matplotlib.pyplot as plt
import numpy as np
from sklearn import tree
from sklearn.datasets import load_iris

### 回归




X = [[0, 0], [2, 2]]
y = [0.5, 2.5]
clf = tree.DecisionTreeRegressor()
clf = clf.fit(X, y)
print(clf.predict([[1, 1]]))


# 创建随机数据

# rng = np.random.RandomState(1)

# X = np.sort(5 * rng.rand(80, 1), axis=0)
# y = np.sin(X).ravel()
# y[::5] += 3 * (0.5 - rng.rand(16))


# # Fit regression model
# regr_1 = tree.DecisionTreeRegressor(max_depth=2)
# regr_2 = tree.DecisionTreeRegressor(max_depth=5)
# regr_1.fit(X, y)
# cc = regr_2.fit(X, y)

# # Predict
# X_test = np.arange(0.0, 5.0, 0.01)[:, np.newaxis]
# y_1 = regr_1.predict(X_test)
# y_2 = regr_2.predict(X_test)

# # Plot the results
# plt.figure()
# plt.scatter(X, y, s=20, edgecolor="black", c="darkorange", label="data")
# plt.plot(X_test, y_1, color="cornflowerblue", label="max_depth=2", linewidth=2)
# plt.plot(X_test, y_2, color="yellowgreen", label="max_depth=5", linewidth=2)
# plt.xlabel("data")
# plt.ylabel("target")
# plt.title("Decision Tree Regression")
# plt.legend()
# plt.show()

# dot_data = tree.export_graphviz(cc, out_file=None,
              
#                      filled=True, rounded=True,  
#                       special_characters=True)  
# graph = graphviz.Source(dot_data)  

# graph.render("irisss")




X = np.array([[1,1,1],[0,0,1],[0,1,0],[1,0,1],[1,1,1],[1,1,0],[0,0,0],[1,1,0],[0,1,0],[0,1,0]])
y = np.array([7.2, 8.8, 15, 9.2, 8.4, 7.6, 11, 10.2, 18, 20])


clf = tree.DecisionTreeRegressor(criterion='mse')
clf = clf.fit(X, y)

dot_data = tree.export_graphviz(clf, out_file=None,
                     feature_names=['Ear', 'Face', 'Whiskers'],  
                      class_names=['W'],  
                     filled=True, rounded=True,  
                      special_characters=True)  
graph = graphviz.Source(dot_data)  

graph.render("iris")