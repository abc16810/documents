
# scikit-learn 中 logistic 回归在 LogisticRegression 类中实现了二分类（binary）、
# 一对多分类（one-vs-rest）及多项式 logistic 回归，并带有可选的 L1 和 L2 正则化

# scikit-learn的逻辑回归在默认情况下使用L2正则化，这样的方式在机器学习领域是常见的，在统计分析领域是不常见的。
# 正则化的另一优势是提升数值稳定性。scikit-learn通过将C设置为很大的值实现无正则化

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression

X = np.array([[0.5,0.5],[1,1],[1.5,0.5],[3,0.5],[2,2],[1,2.5]])
y = np.array([0,0,0,1,1,1])



fig, ax = plt.subplots(figsize=(12,8))
ax.scatter([0.5,1,1.5],[0.5,1,0.5], s=50, c='b', marker='o', label='Admitted')
ax.scatter([3,2,1],[0.5,2,5], s=50, c='r', marker='x', label='Not Admitted')
ax.legend()
ax.set_xlabel('Exam 1 Score')
ax.set_ylabel('Exam 2 Score')
plt.show()


lr_model = LogisticRegression()

lr_model.fit(X,y)

print(lr_model.coef_)
print(lr_model.intercept_)
y_pred = lr_model.predict(X)

print(y_pred)


# 计算准确率
print(lr_model.score(X, y))

