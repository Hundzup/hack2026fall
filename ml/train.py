import joblib
import numpy as np
from sklearn.linear_model import LinearRegression

# y = 2*x1 + 3*x2 + 5
X = np.array([
    [1, 1], [2, 1], [3, 2], [4, 3],
    [5, 5], [6, 4], [7, 6], [8, 7],
], dtype=float)
y = 2 * X[:, 0] + 3 * X[:, 1] + 5

model = LinearRegression().fit(X, y)
joblib.dump(model, "model.pkl")

print("coef:", model.coef_)
print("intercept:", model.intercept_)
print("saved to model.pkl")