import random
import math
import os
import numpy as np

# 仿真时间
TOTAL_TIME = 50000

# 网络节点坐标范围
SCALE = 100

# physical网络QOS相关的参数
MINPL=10**(-5)
MAXPL=10**(-2)
MINDL=0
MAXDL=50
MINJT=0
MAXJT=20

# 仅与虚拟网络请求相关的参数
DURATION_MEAN = 1000
MIN_DURATION = 250
DURATION_MEAN_SECOND = 1000
MIN_DURATION_SECOND = 250
MAX_DISTANCE = 20


class Constructor:
    def __init__(self, path):
        self.network_files_dir = path
        if not os.path.exists(self.network_files_dir):
            os.makedirs(self.network_files_dir)
        self.spec_dir = 'generated/spec/'
        self.alt_dir = 'generated/alt/'

    def make_sub_wm(self, node_num, min_res, max_res):
        """生成物理网络文件（基于waxman随机型网络模型）"""
        network_name = 'sub-wm'
        self.generate_network_file(network_name, node_num, min_res, max_res)

    # transits： transit域数量
    # stubs: 每个transit节点连接的stub域数量
    # transit_nodes: 每个transit域中节点数量
    # transit_p: transit域内的连通性
    # stub_nodes: 每个stub域中节点数量
    # stub_p: stub域内的连通性
    def make_sub_ts(self, transits, stubs, transit_nodes, stub_nodes, min_res, max_res):
        """生成物理网络文件（基于Transit-Stub模型）"""

        network_name = 'sub-ts'
        node_num = transits * transit_nodes * (1 + stubs * stub_nodes)
        self.generate_network_file(network_name, node_num, min_res, max_res, transit_nodes=transit_nodes)

    def make_req(self, index, min_res, max_res, node_num, time, duration, qosclass):
        """生成虚拟网络请求文件"""

        network_name = 'req%s' % index
        self.generate_network_file(network_name, node_num, min_res, max_res,
                                   time=time, duration=duration, qosclass=qosclass)

    # possion_mean：虚拟网络请求的到达服从泊松分布，且平均每1000个时间单位内到达的数量为possion_mean个
    # 虚拟节点数量服从[min_num_nodes, max_num_nodes]的均匀分布
    def make_batch_req(self, possion_mean, min_num_nodes, max_num_nodes, min_res, max_res):
        """生成多个虚拟网络请求文件"""

        # 时间间隔
        interval = 1000
        # 虚拟网络请求数量
        req_num = int(possion_mean / interval * TOTAL_TIME)
        # 在一个时间间隔内到达的VNR数量
        req_num_interval = 0
        # 记录该时间间隔内已到达的VNR数量
        count = 0
        # 记录已经经历了多少个时间间隔
        p = 0
        # 每个时间间隔的起始时间
        start = 0

        n1=0.15*req_num
        n2=0.20*req_num
        a=[1,2,3,4]*(int(n1))
        b=[5,6]*(int(n2))
        qos=a+b


        # 按照以下步骤分别生成req_num个虚拟网络请求文件
        for i in range(req_num):

            if count == req_num_interval:
                req_num_interval = 0
                while req_num_interval == 0:
                    req_num_interval = np.random.poisson(possion_mean)
                count = 0
                start = p * interval
                p += 1
            count += 1
            time = start + ((count + 1) / (req_num_interval + 1)) * interval
            duration = MIN_DURATION + int(-math.log(random.random()) * (DURATION_MEAN - MIN_DURATION))
            node_amount = random.randint(min_num_nodes, max_num_nodes)
            qosclass=random.choice(qos)
            qos.remove(qosclass)
            self.make_req(i, min_res, max_res, node_amount, time, duration,qosclass)

    def generate_random_resource(self,node_num, edge_num, min_res, max_res):
        queuerandom, plrandom=[], []
        for i in range(node_num):
            queuerandom.append(random.uniform(min_res,max_res))
            plrandom.append(random.uniform(MINPL,MAXPL))
        queuerandom.sort(reverse=True)
        plrandom.sort()
        bwrandom, dlrandom, jtrandom=[], [], []
        for i in range(edge_num):
            bwrandom.append(random.uniform(min_res,max_res))
            dlrandom.append(random.uniform(MINDL,MAXDL))
            jtrandom.append(random.uniform(MINJT,MAXJT))
        bwrandom.sort(reverse=True)
        dlrandom.sort()
        jtrandom.sort()

        return queuerandom,plrandom,bwrandom,dlrandom,jtrandom


    def generate_network_file(self, network_name, node_num, min_res, max_res,
                                                    time=0, duration=0, transit_nodes=0, qosclass=0):
        """生成网络文件"""

        # 读取alt文件
        if network_name == 'sub-ts':
            alt_filename = 'ts100.alt'
        else:
            alt_filename = '%s.alt' % node_num

        with open(self.alt_dir + alt_filename) as f:
            lines = f.readlines()

        # Step4: 生成网络文件
        print("generate %s" % network_name)
        network_filename = '%s.txt' % network_name
        with open(self.network_files_dir + network_filename, 'w') as network_file:

            coordinates = []

            # Step4-1: 写入网络整体信息
            edge_num = len(lines) - node_num - 6

            if network_name == 'sub-wm' or network_name == 'sub-ts':

                qur, plr, bwr, dlr, jtr = self.generate_random_resource(node_num, edge_num, min_res, max_res)

                # 物理网络信息包括：节点数量、链路数量
                network_file.write("%d %d\n" % (node_num, edge_num))
                # Step4-2: 依次写入节点信息（x坐标，y坐标，节点资源）
                for line in lines[4:4 + node_num]:
                    blocks = line.split()
                    x = int(blocks[2])
                    y = int(blocks[3])
                    coordinates.append((x, y))
                    # cpu = random.uniform(min_res, max_res)
                    queue = random.choice(qur)
                    cpu = random.uniform(0.8,1.2)*queue
                    packet = plr[qur.index(queue)]
                    qur.remove(queue)
                    plr.remove(packet)

                    # 属于transit-stub模型网络的特殊操作
                    if network_name == 'sub-ts' and len(coordinates) <= transit_nodes:
                        network_file.write("%d %d %f %f %f\n" % (x, y, 100 + cpu, 100 + queue, packet))
                        continue

                    network_file.write("%d %d %f %f %f\n" % (x, y, cpu, queue, packet))

                # Step4-3: 依次写入链路信息（起始节点，终止节点，带宽资源，时延）

                for line in lines[6 + node_num:]:
                    from_id, to_id, length, a = [int(x) for x in line.split()]
                    distance = self.calculate_dis(coordinates[from_id], coordinates[to_id])
                    bw = random.choice(bwr)
                    delay = dlr[bwr.index(bw)]
                    jitter = jtr[bwr.index(bw)]

                    # 属于transit-stub模型网络的特殊操作
                    if network_name == 'sub-ts':
                        if from_id < transit_nodes and to_id < transit_nodes:
                            network_file.write(
                                "%d %d %f %f %f %f\n" % (from_id, to_id, 100 + bw, delay, jitter, distance))
                            continue
                        if from_id < transit_nodes or to_id < transit_nodes:
                            network_file.write(
                                "%d %d %f %f %f %f\n" % (from_id, to_id, 50 + bw, delay, jitter, distance))
                            continue

                    network_file.write("%d %d %f %f %f %f\n" % (from_id, to_id, bw, delay, jitter, distance))
            else:

                if qosclass==1:
                    band, dll, jt, pl = 5, 50, 10, 0.0001
                elif qosclass==2:
                    band, dll, jt, pl = 20, 100, 10, 0.0001
                elif qosclass==3:
                    band, dll, jt, pl = 5, 150, 30, 0.001
                elif qosclass==4:
                    band, dll, jt, pl = 40, 200, 50, 0.001
                elif qosclass==5:
                    band, dll, jt, pl = 45, 1000, 1000, 1
                else:
                    band, dll, jt, pl = 5, 1000, 1000, 1


                delay = random.uniform(dll-10, dll)
                jitter = random.uniform(jt-5, jt)

                # 虚拟网络信息包括：节点数量、链路数量、到达时间、持续时间、可映射范围
                network_file.write("%d %d %d %d %d %d %d %d\n" % (node_num, edge_num, time, duration,
                                                                  delay,jitter, pl, MAX_DISTANCE))

                # Step4-2: 依次写入节点信息（x坐标，y坐标，节点资源）
                for line in lines[4:4 + node_num]:
                    blocks = line.split()
                    x = int(blocks[2])
                    y = int(blocks[3])
                    coordinates.append((x, y))
                    # cpu = random.uniform(min_res, max_res)
                    queue = random.uniform(min_res, max_res)
                    cpu = random.uniform(0.8, 1.2) * queue
                    network_file.write("%d %d %f %f\n" % (x, y, cpu, queue))

                # Step4-3: 依次写入链路信息（起始节点，终止节点，带宽资源，时延）

                for line in lines[6 + node_num:]:
                    from_id, to_id, length, a = [int(x) for x in line.split()]
                    distance = self.calculate_dis(coordinates[from_id], coordinates[to_id])
                    bw = random.uniform(band-5, band+5)
                    network_file.write("%d %d %f %f\n" % (from_id, to_id, bw, distance))



    @staticmethod
    def calculate_dis(coordinate1, coordinate2):
        """给定两个节点坐标，求解它们之间的欧氏距离"""
        return math.sqrt(pow(coordinate1[0] - coordinate2[0], 2) + pow(coordinate1[1] - coordinate2[1], 2))


if __name__ == '__main__':

    constructor = Constructor('networks/')

    # 生成节点数为100，连通率为0.5的随机型物理网络
    # constructor.make_sub_wm(100, 50, 100)

    # 生成节点数为1×4×(1+3×8)=100，连通率为0.5的Transit-Stub型物理网络
    # constructor.make_sub_ts(1, 3, 4, 8, 50, 100)

    # 用于单级映射场景
    # 平均每1000个时间单位内到达40个虚拟网络请求，且虚拟节点数服从2~10的均匀分布，请求资源服从0~50的均匀分布
    # constructor.make_batch_req(40, 2, 10, 0, 50)
