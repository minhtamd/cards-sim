import numpy as np

arr = np.array([[[i*2*j for k in range(2)] for i in range(4)] for j in range(5)])

arr = arr[:,1:,0]-arr[:,:-1,0]
print(arr)
print(np.average(arr, axis=0))