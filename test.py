# from mcnetwork import Network
# import math
# import numpy as np
# net=Network('mcnetworks/')
# sub,_ =net.get_networks("sub-wm.txt",0)
# # sub,que=net.get_networks("sub-wm.txt",10)
# # req=que[5]
# # op=OP()
# # a=op.get_set(sub,req)
# # from functools import reduce
# # fn = lambda x,code=',': reduce(lambda x,y:[str(i)+code+str(j) for i in x for j in y],x)
# # print(fn(a))
# # print(len(fn(a)))
# diis=[]
# i=0
# for e in sub.edges:
#     coor1 = [sub.nodes[e[1]]['x_coordinate'], sub.nodes[e[1]]['y_coordinate']]
#     coor2 = [sub.nodes[e[0]]['x_coordinate'], sub.nodes[e[0]]['y_coordinate']]
#     dis = math.sqrt(pow(coor1[0] - coor2[0], 2) + pow(coor1[1] - coor2[1], 2))
#     diis.append(dis)
#     i+=1
#     print(dis)
# print('-----------')
# print(i)
# print(min(diis))
# print(max(diis))
# print(np.mean(diis))