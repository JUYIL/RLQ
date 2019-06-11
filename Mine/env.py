import gym
from gym import spaces
import copy
import networkx as nx
import numpy as np
from network import Network


class NodeEnv(gym.Env):

    def __init__(self, sub):
        self.count = -1
        self.n_action = sub.number_of_nodes()
        self.sub = copy.deepcopy(sub)
        self.origin_sub=copy.deepcopy(sub)
        self.action_space = spaces.Discrete(self.n_action)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.n_action, 9), dtype=np.float32)
        self.state = None
        self.actions = []
        self.degree = []
        for i in nx.degree_centrality(sub).values():
            self.degree.append(i)
        self.cln = []
        for j in nx.closeness_centrality(sub).values():
            self.cln.append(j)
        dl, jt, pl = [], [], []
        for u in range(self.n_action):
            dl.append(Network.calculate_adjacent_delay(self.sub, u))
            jt.append(Network.calculate_adjacent_jitter(self.sub, u))
            pl.append(self.sub.nodes[u]['pl'])
        self.dl = (dl - np.min(dl)) / (np.max(dl) - np.min(dl))
        self.jt = (jt - np.min(jt)) / (np.max(jt) - np.min(jt))
        self.pl = (pl - np.min(pl)) / (np.max(pl) - np.min(pl))
        self.vnr = None

    def set_sub(self, sub):
        self.sub = copy.deepcopy(sub)

    def set_vnr(self, vnr):
        self.vnr = vnr

    def step(self, action):
        self.actions.append(action)
        self.count = self.count + 1
        cpu_remain, que_remain, bw_all_remain, avg_dst = [], [], [], []

        for u in range(self.n_action):
            adjacent_bw = Network.calculate_adjacent_bw(self.sub, u, 'bw_remain')
            if u == action:
                self.sub.nodes[action]['cpu_remain'] -= self.vnr.nodes[self.count]['cpu']
                adjacent_bw -= Network.calculate_adjacent_bw(self.vnr, self.count)
            cpu_remain.append(self.sub.nodes[u]['cpu_remain'])
            que_remain.append(self.sub.nodes[u]['queue_remain'])
            bw_all_remain.append(adjacent_bw)

            sum_dst = 0
            for v in self.actions:
                sum_dst += nx.shortest_path_length(self.sub, source=u, target=v)
            sum_dst /= (len(self.actions) + 1)
            avg_dst.append(sum_dst)

        cpu_remain = (cpu_remain - np.min(cpu_remain)) / (np.max(cpu_remain) - np.min(cpu_remain))
        que_remain = (que_remain - np.min(que_remain)) / (np.max(que_remain) - np.min(que_remain))
        bw_all_remain = (bw_all_remain - np.min(bw_all_remain)) / (np.max(bw_all_remain) - np.min(bw_all_remain))
        avg_dst = (avg_dst - np.min(avg_dst)) / (np.max(avg_dst)-np.min(avg_dst))

        # for e in self.sub.edges:
        #     uti = 1-self.sub[e[0]][e[1]]['bw_remain'] / self.sub[e[0]][e[1]]['bw']
        #     self.sub[e[0]][e[1]]['dl'] = self.origin_sub[e[0]][e[1]]['dl'] + (7 * uti)
        #     self.sub[e[0]][e[1]]['jt'] = self.origin_sub[e[0]][e[1]]['jt'] + (3 * uti)
        # dl, jt = [], []
        # for u in range(self.n_action):
        #     dl.append(Network.calculate_adjacent_delay(self.sub, u))
        #     jt.append(Network.calculate_adjacent_jitter(self.sub, u))
        # dl = (dl - np.min(dl)) / (np.max(dl) - np.min(dl))
        # jt = (jt - np.min(jt)) / (np.max(jt) - np.min(jt))
        #
        # self.state = (cpu_remain, que_remain, bw_all_remain,
        #               self.degree, avg_dst, self.cln,
        #               dl, jt, self.pl)

        self.state = (cpu_remain, que_remain, bw_all_remain,
                      self.degree, avg_dst, self.cln,
                      self.dl, self.jt, self.pl)
        return np.vstack(self.state).transpose(), 0.0, False, {}

    def reset(self):
        """获得底层网络当前最新的状态"""
        self.count = -1
        self.actions = []
        cpu_remain, que_remain, bw_all_remain = [], [], []
        for u in range(self.n_action):
            cpu_remain.append(self.sub.nodes[u]['cpu_remain'])
            que_remain.append(self.sub.nodes[u]['queue_remain'])
            bw_all_remain.append(Network.calculate_adjacent_bw(self.sub, u, 'bw_remain'))

        cpu_remain = (cpu_remain - np.min(cpu_remain)) / (np.max(cpu_remain) - np.min(cpu_remain))
        que_remain = (que_remain - np.min(que_remain)) / (np.max(que_remain) - np.min(que_remain))
        bw_all_remain = (bw_all_remain - np.min(bw_all_remain)) / (np.max(bw_all_remain) - np.min(bw_all_remain))
        avg_dst = np.zeros(self.n_action).tolist()
        # for e in self.sub.edges:
        #     uti = 1-self.sub[e[0]][e[1]]['bw_remain'] / self.sub[e[0]][e[1]]['bw']
        #     self.sub[e[0]][e[1]]['dl'] = self.origin_sub[e[0]][e[1]]['dl'] + (7 * uti)
        #     self.sub[e[0]][e[1]]['jt'] = self.origin_sub[e[0]][e[1]]['jt'] + (3 * uti)
        # dl, jt = [], []
        # for u in range(self.n_action):
        #     dl.append(Network.calculate_adjacent_delay(self.sub, u))
        #     jt.append(Network.calculate_adjacent_jitter(self.sub, u))
        # dl = (dl - np.min(dl)) / (np.max(dl) - np.min(dl))
        # jt = (jt - np.min(jt)) / (np.max(jt) - np.min(jt))
        # self.state = (cpu_remain, que_remain, bw_all_remain,
        #               self.degree, avg_dst, self.cln,
        #               dl, jt, self.pl)

        self.state = (cpu_remain, que_remain, bw_all_remain,
                      self.degree, avg_dst, self.cln,
                      self.dl, self.jt, self.pl)

        # cpu_all, que_all, packet_loss = [], [], []
        # for u in range(self.n_action):
        #     cpu_all.append(self.sub.nodes[u]['cpu'])
        #     que_all.append(self.sub.nodes[u]['queue'])
        #     packet_loss.append(self.sub.nodes[u]['pl'])
        # self.cpu_all = (cpu_all - np.min(cpu_all)) / (np.max(cpu_all) - np.min(cpu_all))
        # self.que_all = (que_all - np.min(que_all)) / (np.max(que_all) - np.min(que_all))
        # self.packet_loss = (packet_loss - np.min(packet_loss)) / (np.max(packet_loss) - np.min(packet_loss))
        return np.vstack(self.state).transpose()

    def render(self, mode='human'):
        pass
