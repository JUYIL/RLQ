from algorithm import Algorithm
from analysis import Analysis


if __name__ == '__main__':

    tool = Analysis('results_algorithm/')
    name = 'DC'
    algorithm = Algorithm(name, link_method=3)
    runtime = algorithm.execute(network_path='networks/',
                                sub_filename='sub-ts.txt',
                                req_num=1000)
    tool.save_evaluations(algorithm.evaluation, '%s.txt' % name)
    print(runtime)
#178