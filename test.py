import numpy as np

X = np.load("./data/data_train/X_val.npy", allow_pickle=False)
print("Shape:", X.shape)
print("Min:", X.min())
print("Max:", X.max())
print("NaN:", np.isnan(X).any())