from algorithm import Algorithm
from analysis import Analysis


if __name__ == '__main__':

    tool = Analysis('results_algorithm/')
    name = 'RLQ'
    algorithm = Algorithm(name, param=10)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-ts.txt',
                                req_num=1000)
    tool.save_evaluations(algorithm.evaluation, '%s.txt' % name)
    print(runtime)
# import tensorflow as tf
# n=tf.train.NewCheckpointReader('./Mine/nodemodel/nodemodel.ckpt')
# a=n.get_tensor('conv/weights')
# b=n.get_tensor('conv/bias')
# print(a,b)