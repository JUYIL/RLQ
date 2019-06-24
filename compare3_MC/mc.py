import networkx as nx
import numpy as np
import math
from itertools import islice


class MC:
    def __init__(self,gamma):
        self.gamma=gamma
        # self.omega=omega
        # self.alpha=alpha

    def run(self, sub, req):
        node_map = {}
        snode_mapped=[]
        vv = self.LA(req)
        vs = self.LA(sub)
        vv = sorted(vv.items(), key=lambda item:item[1], reverse=True)
        vs = sorted(vs.items(), key=lambda item:item[1], reverse=True)
        for vnode,_ in vv:
            for snode,_ in vs:
                if req.nodes[vnode]['cpu'] <= sub.nodes[snode]['cpu_remain'] \
                        and snode not in snode_mapped:
                    node_map.update({vnode:snode})
                    snode_mapped.append(snode)
                    break
                else:
                    continue
        return node_map

    def LA(self,graph):

        n=graph.number_of_nodes()
        if n>50:
            cpu_kind='cpu_remain'
        else:
            cpu_kind = 'cpu'

        CBL=[]
        total_cbl=0
        for i in range(n):
            cbl_right=self.get_sum_bw_delay(graph,i)
            cbl=graph.nodes[i][cpu_kind]*cbl_right
            CBL.append(cbl)
            total_cbl+=cbl
        Res=[]
        for i in range(n):
            res=CBL[i] / total_cbl
            Res.append(res)
        pzy=np.zeros((n,n))
        for i in range(n):
            total_res = 0
            for u in nx.neighbors(graph, i):
                total_res += Res[u]
            for j in range(n):
                if (i,j) in graph.edges:
                    pzy[i][j]=Res[j] / total_res
        Vrb, Vra = [0 for i in range(n)], [0 for i in range(n)]
        eps, cnt = 1.0, 0
        while eps > 1e-6:
            eps = 0
            cnt += 1
            for v in graph.nodes:
                vr_right = 0
                for u in nx.neighbors(graph, v):
                    vr_right += pzy[v][u] * Vrb[u]
                Vra[v] = (1 - self.gamma) * Res[v] + self.gamma * vr_right
                eps += (Vra[v] - Vra[v]) ** 2
                Vrb[v] = Vra[v]
            eps = math.sqrt(eps)
        node_rank = {}
        for i in range(n):
            node_rank.update({i:Vra[i]})
        # Vra = Vra / np.max(Vra)
        return node_rank

    def MCRP(self,graph):

        n=graph.number_of_nodes()
        Rew=[]

    def similiar(self,vv,vs):
        xsd=[]

    def get_sum_bw_delay(self, graph, u):
        """计算一个节点的相邻链路带宽和"""

        bw_sum = 0
        if graph.number_of_nodes()>50:
            for v in graph.neighbors(u):
                delay=(50-graph[u][v]['dl']) / 50
                bw_sum += graph[u][v]["bw_remain"]*delay
        else:
            for v in graph.neighbors(u):
                bw_sum += graph[u][v]["bw"]

        return bw_sum
