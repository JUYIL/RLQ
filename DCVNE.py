import tensorflow as tf
n=tf.train.NewCheckpointReader('./Mine/nodemodel/nodemodel.ckpt')
a=n.get_tensor('conv/weights')
b=n.get_tensor('conv/bias')
print(a,b)

# from network import *
# c=0
# n=0
# for i in range(100):
#     for j in range(100):
#         path=Network.k_shortest_path(sub,i,j,k=1)[0]
#         c=Evaluation.calculate_delay(sub, path)
#         n=max(0,c)
#         print(c)
# print(n)