import graphviz
import numpy as np
from sklearn import tree
from sklearn.datasets import load_iris

#### 分类


# iris = load_iris()
# clf = tree.DecisionTreeClassifier(random_state=0, criterion="entropy")
# clf = clf.fit(iris.data, iris.target)


# # dot_data = tree.export_graphviz(clf, out_file=None)
# # graph = graphviz.Source(dot_data)
# # graph.render("iris")


# dot_data = tree.export_graphviz(clf, out_file=None,
#                      feature_names=iris.feature_names,  
#                       class_names=iris.target_names,  
#                      filled=True, rounded=True,  
#                       special_characters=True)  
# graph = graphviz.Source(dot_data)  

# graph.render("iris")


X = np.array([7.2, 8.8, 15, 9.2, 8.4, 7.6, 11, 10.2, 18, 20]).reshape([-1,1])
y = np.array([1,1,0,0,1,1,0,1,0,0])

clf = tree.DecisionTreeClassifier(random_state=0, criterion="entropy")
clf = clf.fit(X, y)

dot_data = tree.export_graphviz(clf, out_file=None,
                     feature_names=['w'],  
                      class_names=['not Cat', 'Cat'],  
                     filled=True, rounded=True,  
                      special_characters=True)  
graph = graphviz.Source(dot_data)  

graph.render("iris")