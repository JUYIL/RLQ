class Evaluation:
    def __init__(self):

        # 处理的虚拟网络请求数
        self.total_arrived = 0
        # 成功接受的虚拟网络请求数
        self.total_accepted = 0
        # 请求接受率
        self.acc_ratio = 0
        # 总收益
        self.total_revenue = 0
        # 总成本
        self.total_cost = 0
        # 总qos_loss
        self.total_loss = 0
        # 平均节点利用率
        self.average_node_stress = 0
        # 平均链路利用率
        self.average_link_stress = 0
        # 每个时刻对应的性能指标元组（请求接受率、平均收益、平均成本、收益成本比、平均节点利用率、平均链路利用率）
        self.metrics = {}

    def collect(self, sub, req, link_map=None):
        """增加对应的评估指标值"""
        self.total_accepted += 1
        self.acc_ratio = self.total_accepted/self.total_arrived
        if link_map is not None:
            self.total_revenue += self.calculate_revenue(req)
            self.total_cost += self.calculate_cost(req, link_map)
            self.average_node_stress += self.calculate_ans(sub)
            self.average_link_stress += self.calculate_als(sub)
            self.total_loss += self.get_qos_class(req)
        self.metrics.update({req.graph['time']: (self.acc_ratio,
                                                 self.total_revenue,
                                                 self.total_cost,
                                                 self.total_revenue / self.total_cost,
                                                 self.average_node_stress / self.total_arrived,
                                                 self.average_link_stress / self.total_arrived)})

    @staticmethod
    def calculate_revenue(req):
        """"映射收益"""
        revenue = 0
        for vn in range(req.number_of_nodes()):
            revenue += req.nodes[vn]['cpu']
        for vl in req.edges:
            revenue += req[vl[0]][vl[1]]['bw']
        return revenue

    @staticmethod
    def calculate_qos_revenue(req):
        """"映射收益"""
        k=Evaluation.get_qos_class(req)
        print(k)
        revenue = 0
        for vn in range(req.number_of_nodes()):
            revenue += (req.nodes[vn]['cpu'] + req.nodes[vn]['queue'])
        for vl in req.edges:
            revenue += req[vl[0]][vl[1]]['bw']
        return revenue*k

    @staticmethod
    def calculate_cost(req, link_map):
        """映射成本"""
        cost = 0
        for vn in range(req.number_of_nodes()):
            cost += req.nodes[vn]['cpu']

        for vl, path in link_map.items():
            link_resource = req[vl[0]][vl[1]]['bw']
            cost += link_resource * (len(path) - 1)
        return cost

    @staticmethod
    def revenue_to_cost_ratio(req, link_map):

        if len(link_map) == req.number_of_edges():
            revenue = Evaluation.calculate_revenue(req)
            cost = Evaluation.calculate_cost(req, link_map)
            return revenue / cost
        else:
            return -1

    @staticmethod
    def r_to_c_ratio_qos(req, link_map):

        if len(link_map) == req.number_of_edges():
            revenue = Evaluation.calculate_qos_revenue(req)
            cost = Evaluation.calculate_cost(req, link_map)
            return revenue / cost
        else:
            return -1

    @staticmethod
    def calculate_delay(sub, path):
        """delay"""
        cost = 0
        head = path[0]
        for tail in path[1:]:
            cost += sub[head][tail]['dl']
            head = tail
        return cost

    @staticmethod
    def calculate_jitter(sub, path):
        """jitter"""
        cost = 0
        head = path[0]
        for tail in path[1:]:
            cost += sub[head][tail]['jt']
            head = tail
        return cost

    @staticmethod
    def calculate_packet_loss(sub, path):
        """packet_loss"""
        cost = 1
        for i in range(len(path)):
            cost *= 1-sub.nodes[path[i]]['pl']
        return 1-cost

    @staticmethod
    def get_qos_class(req):
        vdl = req.graph['delay']
        vpl = req.graph['packetloss']
        if vdl <= 50 and vpl == 0.001:
            k = 1
        elif vdl <= 100 and vpl == 0.001:
            k = 1.2
        elif vdl <= 150 and vpl == 0.01:
            k = 1.3
        elif vdl <= 200 and vpl == 0.01:
            k = 1.4
        else:
            k = 2
        return k

    @staticmethod
    def get_qos_loss(sub, req, link_map):
        vdl = req.graph['delay']
        vjt = req.graph['jitter']
        vpl = req.graph['packetloss']
        sdl, sjt, spl = 0, 0, 0
        for vl, path in link_map.items():
            sdl = max(sdl, Evaluation.calculate_delay(sub, path))
            sjt = max(sjt, Evaluation.calculate_jitter(sub, path))
            spl = max(spl, Evaluation.calculate_packet_loss(sub, path))
        dl_loss = (sdl - vdl) / vdl
        jt_loss = (sjt - vjt) / vjt
        pl_loss = (spl - vpl) / vpl

        small_number = 0
        if dl_loss <= 0:
            dl_loss = small_number
        if jt_loss <= 0:
            jt_loss = small_number
        if pl_loss <= 0:
            pl_loss = small_number
        qos_loss = dl_loss + jt_loss + pl_loss
        return qos_loss

    @staticmethod
    def uti_to_qos(sub, req, link_map):

        if len(link_map) == req.number_of_edges():
            qos_loss = Evaluation.get_qos_loss(sub, req, link_map)
            node_uti = Evaluation.calculate_ans(sub)
            link_uti = Evaluation.calculate_als(sub)
            uti = node_uti*link_uti
            if uti == 0:
                reward = 0
            else:
                reward = uti-qos_loss

            return reward
        else:
            return -1

    @staticmethod
    def get_qos_loss_d(sub, req, link_map):
        vdl = req.graph['delay']
        sdl = 0
        for vl, path in link_map.items():
            sdl = max(sdl, Evaluation.calculate_delay(sub, path))
        dl_loss = (sdl - vdl) / vdl
        if dl_loss <= 0:
            dl_loss = 0
        return dl_loss

    @staticmethod
    def uti_to_qos_d(sub, req, link_map):

        if len(link_map) == req.number_of_edges():
            qos_loss = Evaluation.get_qos_loss_d(sub, req, link_map)
            node_uti = Evaluation.calculate_ans(sub)
            link_uti = Evaluation.calculate_als(sub)
            uti = node_uti * link_uti
            if uti == 0:
                reward = 0
            else:
                reward = uti - qos_loss

            return reward
        else:
            return -1

    @staticmethod
    def rc_to_qos(sub, req, link_map):

        if len(link_map) == req.number_of_edges():
            qos_loss = Evaluation.get_qos_loss(sub, req, link_map)
            r_c = Evaluation.r_to_c_ratio_qos(req, link_map)
            reward = r_c - qos_loss

            return reward
        else:
            return -1

    @staticmethod
    def calculate_ans(sub):
        """节点资源利用率"""
        node_stress = 0
        for i in range(sub.number_of_nodes()):
            node_stress += 1 - sub.nodes[i]['cpu_remain'] / sub.nodes[i]['cpu']
        node_stress /= sub.number_of_nodes()
        return node_stress

    @staticmethod
    def calculate_als(sub):
        """链路资源利用率"""
        link_stress = 0
        for vl in sub.edges:
            link_stress += 1 - sub[vl[0]][vl[1]]['bw_remain'] / sub[vl[0]][vl[1]]['bw']
        link_stress /= sub.number_of_edges()
        return link_stress
