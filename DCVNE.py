# import tensorflow as tf
# n=tf.train.NewCheckpointReader('./Mine/nodemodel/nodemodel.ckpt')
# a=n.get_tensor('conv/weights')
# b=n.get_tensor('conv/bias')
# print(a,b)

# from network import *
# import numpy as np
# req=que[0]
# from SAVNE import SA
# s=SA(2)
# s.create_data_file(sub,req)

# out_file='LP/type1.out'
# k=0
# line_num=241347
# with open(out_file) as f:
#             lines = f.readlines()
#             while line_num < len(lines):
#                 line = lines[line_num]
#                 list1 = [x for x in line.split()]
#                 if len(list1) == 0:
#                     pass
#                 else:
#                     string = list1[1]
#                     if string[:2] != "f[":
#                         pass
#                     else:
#                         fid, fs, ft = string[2:-1].split(",")
#                         if len(list1) == 2:
#                             line_num += 1
#                             line = lines[line_num]
#                             list1 = [x for x in line.split()]
#                         fval = float(list1[-1])
#                         print(fid, fs, ft, fval)
#                         line_num += 1
#                         k+=1
#                         if k >5:
#                             break

