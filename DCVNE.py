# import tensorflow as tf
# n=tf.train.NewCheckpointReader('./Mine/nodemodel/nodemodel.ckpt')
# a=n.get_tensor('conv/weights')
# b=n.get_tensor('conv/bias')
# print(a,b)


from network import *
req=que[1000]
print(req.graph['id'])
from compare1_SA.sa import SA
s=SA()
s.run(sub,req)

