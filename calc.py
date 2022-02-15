import math

x = 4
y = 3
z = 5
list = []

for i in range(0, x):
    for j in range(0, y):
        for k in range(0, z):
            # print('[',i,j,k,']')
            list.append(math.pow(2,i)*math.pow(3,j)*math.pow(5,k))

list.sort()
print(list)
