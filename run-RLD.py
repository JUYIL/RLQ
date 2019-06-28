from algorithm import Algorithm
from analysis import Analysis


if __name__ == '__main__':

    tool = Analysis('results_algorithm/')
    name = 'RLD'
    algorithm = Algorithm(name, param=10)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-wm.txt',
                                req_num=1000)
    tool.save_evaluations(algorithm.evaluation, '%s.txt' % name)
    print(runtime)
# 489 ts
# 899 wm
