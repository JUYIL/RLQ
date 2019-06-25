import networkx as nx
import numpy as np
import math


class MC:
    def __init__(self,gamma,omega):
        self.gamma=gamma
        self.omega=omega
        self.alpha=(1-self.omega)/2
        self.gu_node = []

    def run(self, sub, req):

        vv = self.LA(req)
        vs = self.LA(sub)
        node_map, snode_mapped = self.no_pinned_map(sub, req)
        for vnode in req.nodes:
            if vnode not in node_map.keys():
                zv = self.MCRP(req, list(node_map.keys()))
                zs = self.MCRP(sub, snode_mapped)
                ns = sub.number_of_nodes()
                nv = req.number_of_nodes()
                xsd = list(self.similiar(vv, vs, zv, zs, ns, nv)[vnode])
                xsds={}
                for i in range(ns):
                    xsds.update({i:xsd[i]})
                xsds = sorted(xsds.items(), key=lambda item:item[1])
                for snode,_ in xsds:
                    if req.nodes[vnode]['cpu'] <= sub.nodes[snode]['cpu_remain']\
                            and snode not in snode_mapped:
                        node_map.update({vnode:snode})
                        snode_mapped.append(snode)
                        break
                    else:
                        continue
        return node_map

    def no_pinned_map(self,sub,req):
        node_map = {}
        snode_mapped = []
        vv = self.LA(req)
        vs = self.LA(sub)
        vv = sorted(vv.items(), key=lambda item:item[1], reverse=True)
        vs = sorted(vs.items(), key=lambda item:item[1], reverse=True)
        for vnode, _ in vv[:1]:
            for snode, _ in vs:
                if req.nodes[vnode]['cpu'] <= sub.nodes[snode]['cpu_remain']:
                    node_map.update({vnode:snode})
                    snode_mapped.append(snode)
                    break
                else:
                    continue
        return node_map, snode_mapped

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
        Res, Vrb = [], []
        for i in range(n):
            res=CBL[i] / total_cbl
            Res.append(res)
            Vrb.append(res)
        pzy=np.zeros((n,n))
        for i in range(n):
            total_res = 0
            for u in nx.neighbors(graph, i):
                total_res += Res[u]
            for j in range(n):
                if (i,j) in graph.edges:
                    pzy[i][j]=Res[j] / total_res
        Vra = [0 for i in range(n)]
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
        return node_rank

    def MCRP(self,graph,pinned):

        n=graph.number_of_nodes()
        Rew, pzy = np.zeros((n,n)),np.zeros((n,n))
        for m in pinned:
            for i in range(n):
                if m==i:
                    Rew[m][i]=1
        for e in graph.edges:
            pzy[e[0]][e[1]] = 1 / nx.degree(graph,e[0])
            pzy[e[1]][e[0]] = 1 / nx.degree(graph,e[1])
        Zrb, Zra = np.zeros((n,n)),np.zeros((n,n))
        for m in pinned:
            eps = 1.0
            while eps > 1e-6:
                eps = 0
                for v in graph.nodes:
                    zr_right = 0
                    for u in graph.nodes:
                        zr_right += pzy[v][u] * Zrb[m][u]
                    Zra[m][v] = Rew[m][v] + self.gamma * zr_right
                    eps += (Zrb[m][v] - Zra[m][v]) ** 2
                    Zrb[m][v] = Zra[m][v]
                eps = math.sqrt(eps)
        return Zra

    def similiar(self,vv,vs,zv,zs,ns,nv):
        mv=max(vv.values())
        for k,v in vv.items():
            vv[k]=v/mv
        ms = max(vs.values())
        for k, v in vs.items():
            vs[k] = v / ms
        zv=zv/np.max(zv)
        zs=zs/np.max(zs)
        pinned=self.gu_node
        xsd=np.zeros((ns,ns))
        for v in range(nv):
            for u in range(ns):
                dz=self.omega*((vv[v]-vs[u])**2)
                dy=0
                for i in pinned:
                    dy+=self.alpha*((zv[i][v]-zs[i][u])**2)
                xsd[v][u]=(dz+dy)**(1/2)
        return xsd


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

    # @staticmethod
    # def get_path_delay(sub, path):
    #     """calculate delay for path"""
    #
    #     sum_delay = 0
    #     head = path[0]
    #     for tail in path[1:]:
    #         sum_delay += sub[head][tail]['dl']
    #         head = tail
    #     return sum_delay
    #
    # @staticmethod
    # def k_shortest_path(graph, source, target, k=5):
    #     """K最短路径算法"""
    #     return list(islice(nx.shortest_simple_paths(graph, source, target), k))
    #
    # @staticmethod
    # def get_path_bw(sub, path):
    #     """找到一条路径中带宽资源最小的链路并返回其带宽资源值"""
    #
    #     bandwidth = 1000
    #     head = path[0]
    #     for tail in path[1:]:
    #         if sub[head][tail]['bw_remain'] <= bandwidth:
    #             bandwidth = sub[head][tail]['bw_remain']
    #         head = tail
    #     return bandwidth
    # def pinnede_node_map(self,sub,req):
    #     node_map = {}
    #     snode_mapped = []
    #     self.gu_node = []
    #     for i in range(2):
    #         self.gu_node.append(random.choice(list(req.nodes)))
    #     vnode1 = self.gu_node[0]
    #     for snode in sub.nodes:
    #         if sub.nodes[snode]['cpu_remain'] >= req.nodes[vnode1]['cpu']:
    #             node_map.update({vnode1:snode})
    #             snode_mapped.append(snode)
    #             break
    #         else:
    #             continue
    #     vnode2 = self.gu_node[1]
    #     for snode in sub.nodes:
    #         if sub.nodes[snode]['cpu_remain'] >= req.nodes[vnode2]['cpu'] \
    #                 and snode not in snode_mapped:
    #             if nx.has_path(sub, source=snode_mapped[0], target=snode):
    #                 for path in MC.k_shortest_path(sub, snode_mapped[0], snode, 5):
    #                     if MC.get_path_delay(sub, path) <= req.graph['delay']:
    #                         node_map.update({vnode2:snode})
    #                         snode_mapped.append(snode)
    #                         break
    #                     else:
    #                         continue
    #         if len(node_map)==2:
    #             break
    #         else:
    #             continue
    #     return node_map,snode_mapped