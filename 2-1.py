import numpy as np

print('A')
M = np.array(range(2, 27))
print(M)    # A

print('\nB')
M = M.reshape((5,5))
print(M)    # B

print('\nC')
M[:5, :1] = 0
print(M)    # C

print('\nD')
M = M@M     # == np.matmul(M, M)
print(M)    # D

print('\nE')
v = M[0,:]
v_mag = np.sqrt(v@v)
print(v_mag)    # E