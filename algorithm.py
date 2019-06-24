import time
from evaluation import Evaluation
from network import Network
from Mine.agent import RLQ
from Mine_D.agent_d import RLD
from compare1_SA.sa import SA
from compare2_DC.dc import DC
from compare3_MC.mc import MC
import tensorflow as tf


class Algorithm:

    def __init__(self, name, param=10, link_method=1):
        self.name = name
        self.agent = None
        self.param = param
        self.link_method = link_method
        self.evaluation = Evaluation()

    def execute(self, network_path, sub_filename, req_num=1000):
        networks = Network(network_path)
        sub, requests = networks.get_networks(sub_filename, req_num)

        tf.reset_default_graph()
        with tf.Session() as sess:
            self.configure(sub, sess)
            start = time.time()
            self.handle(sub, requests)
            runtime = time.time() - start
        tf.get_default_graph().finalize()

        return runtime

    def configure(self, sub, sess=None):

        if self.name == 'RLQ':
            networks=Network('networks/')
            training_set=networks.get_reqs_for_train(1000)
            agent=RLQ(sub=sub,
                      n_actions=sub.number_of_nodes(),
                      n_features=9,
                      learning_rate=0.05,
                      num_epoch=self.param,
                      batch_size=100)
            agent.train(training_set)
            nodesaver=tf.train.Saver()
            nodesaver.save(agent.sess, './Mine/nodemodel/nodemodel.ckpt')
        elif self.name == 'RLD':
            networks=Network('networks/')
            training_set=networks.get_reqs_for_train(1000)
            agent=RLD(sub=sub,
                      n_actions=sub.number_of_nodes(),
                      n_features=6,
                      learning_rate=0.05,
                      num_epoch=self.param,
                      batch_size=100)
            agent.train(training_set)
            nodesaver=tf.train.Saver()
            nodesaver.save(agent.sess, './Mine_D/nodemodel/nodemodel.ckpt')
        elif self.name == 'SA':
            agent = SA()
        elif self.name == 'DC':
            agent = DC()
        elif self.name == 'MC':
            agent = MC(gamma=0.83)
        else:
            agent=None

        self.agent = agent

    def handle(self, sub, requests):

        for req in requests:
            req_id = req.graph['id']
            if req.graph['type'] == 0:
                print("\nTry to map request%s: " % req_id)
                self.mapping(sub, req)

            if req.graph['type'] == 1:
                Network.recover(sub, req)

    def mapping(self, sub, req):
        """两步映射：先节点映射阶段再链路映射阶段"""

        self.evaluation.total_arrived += 1

        if self.name == "SA":
            print("node mapping...")
            node_map, link_map = self.agent.run(sub,req)
            if len(node_map) == req.number_of_nodes():
                # mapping virtual links
                print("link mapping...")
                if len(link_map) == req.number_of_edges():
                    Network.allocate(sub, req, node_map, link_map)
                    # 更新实验结果
                    self.evaluation.collect(sub, req, link_map)
                    print("Success!")
                    return True
                else:
                    print("Failed to map all links!")
                    return False
            else:
                print("Failed to map all nodes!")
                return False

        elif self.name == "DC":
            print("node mapping...")
            node_map, link_map = self.agent.run(sub,req)
            if len(node_map) == req.number_of_nodes():
                # mapping virtual links
                print("link mapping...")
                if len(link_map) == req.number_of_edges():
                    Network.allocate(sub, req, node_map, link_map)
                    # 更新实验结果
                    self.evaluation.collect(sub, req, link_map)
                    print("Success!")
                    return True
                else:
                    print("Failed to map all links!")
                    return False
            else:
                print("Failed to map all nodes!")
                return False
        else:
            # mapping virtual nodes
            node_map = self.node_mapping(sub, req)

            if len(node_map) == req.number_of_nodes():
                # mapping virtual links
                print("link mapping...")
                link_map = self.link_mapping(sub, req, node_map)
                if len(link_map) == req.number_of_edges():
                    Network.allocate(sub, req, node_map, link_map)
                    # 更新实验结果
                    self.evaluation.collect(sub, req, link_map)
                    print("Success!")
                    return True
                else:
                    print("Failed to map all links!")
                    return False
            else:
                print("Failed to map all nodes!")
                return False




    def node_mapping(self, sub, req):
        """求解节点映射问题"""

        print("node mapping...")

        # 使用指定的算法进行节点映射并得到节点映射集合
        node_map = self.agent.run(sub, req)

        # 返回节点映射集合
        return node_map

    def link_mapping(self, sub, req, node_map):
        if self.link_method == 1:
            # 剪枝后再寻最短路径_DJP
            link_map = Network.cut_then_find_path(sub, req, node_map)
        elif self.link_method == 2:
            # 剪枝后再寻最短路径_D
            link_map = Network.cut_then_find_path_d(sub, req, node_map)
        elif self.link_method == 3:
            # 剪枝后再寻最短路径_mc
            link_map = Network.cut_then_find_path_mc(sub, req, node_map)
        else:
            # K最短路径
            link_map = Network.find_path(sub, req, node_map, 5)

        return link_map


