from analysis import Analysis
from algorithm import Algorithm
# 5         	0.37612838515546637 	1525.0753908157349  	683.8999999999988
# 10        	0.3711133400200602  	1613.1240510940552  	684.0999999999992
# 15        	0.3510531594784353  	761.4128797054291   	647.3999999999991
# 20        	0.3781344032096289  	755.6144239902496   	674.599999999999

# if __name__ == '__main__':
#
#     tool = Analysis('results_epoch/')
#     epoch = 3
#     algorithm = Algorithm(name='RLQ', param=epoch)
#     runtime = algorithm.execute(network_path='networks/',
#                                     sub_filename='sub-ts.txt',
#                                     req_num=1000)
#     tool.save_evaluations(algorithm.evaluation, '%s.txt' % epoch)
#     qos_loss=algorithm.evaluation.total_loss/algorithm.evaluation.total_accepted
#     tool.save_epoch(epoch, algorithm.evaluation.acc_ratio, runtime, qos_loss)
if __name__ == '__main__':

    tool = Analysis('results_epoch/')
    for i in range(5):
        epoch = (i + 1) * 10
        algorithm = Algorithm(name='RLQ', param=epoch)
        runtime = algorithm.execute(network_path='networks/',
                                    sub_filename='sub-ts.txt',
                                    req_num=1000)
        tool.save_evaluations(algorithm.evaluation, '%s.txt' % epoch)
        qos_loss = algorithm.evaluation.total_loss / algorithm.evaluation.total_accepted

