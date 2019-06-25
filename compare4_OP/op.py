import networkx as nx
import numpy as np
import math
import copy
from itertools import islice


class OP:
    def __init__(self):
        pass

    def run(self, sub, req):
        node_map, link_map = {}, {}
        sub_reqs=self.cut_req_graph(req)
        agent_nodes={}
        snode_mapped=[]
        for sub_req in sub_reqs:
            agent_node=self.select_agent(sub_req)
            agent_node_nr=self.node_rank(sub_req)[agent_node]
            agent_nodes.update({agent_node:agent_node_nr})
        sub_nodes_nr=self.node_rank(sub)
        sub_nodes_nr=sorted(sub_nodes_nr.items(),key=lambda item:item[1],reverse=True)
        agent_nodes=sorted(agent_nodes.items(),key=lambda item:item[1],reverse=True)
        for i in range(len(agent_nodes)):
            vnode_id=agent_nodes[i][0]
            for j in range(sub.number_of_nodes()):
                snode_id=sub_nodes_nr[j][0]
                if req.nodes[vnode_id]['cpu']<=sub.nodes[snode_id]['cpu_remain']\
                        and snode_id not in snode_mapped:
                    node_map.update({vnode_id:snode_id})
                    snode_mapped.append(snode_id)
                    break
                else:
                    continue
        if len(node_map) == len(agent_nodes):
            for ag_node, _ in agent_nodes:
                for i in range(len(sub_reqs)):
                    if ag_node in sub_reqs[i].nodes:
                        sort_links=self.sort_link(sub_reqs[i])
                        sn_id=node_map[ag_node]
                        node_tree=self.generate_tree(sub,sn_id)
                        for e,_ in sort_links:
                            for i in range(2):
                                if e[i]!=ag_node:
                                    leaf=e[i]
                            for d in range(len(node_tree)):
                                for sn_candi in node_tree[d]:
                                    if sn_candi in snode_mapped or\
                                            sub.nodes[sn_candi]['cpu_remain']<req.nodes[leaf]['cpu']:
                                        continue
                                    for path in nx.all_shortest_paths(sub,sn_id,sn_candi):
                                        if DC.get_path_bw(sub, path) >= req[e[0]][e[1]]['bw'] \
                                                and DC.get_path_delay(sub, path) <= req.graph['delay']:
                                            link_map.update({e: path})
                                            node_map.update({leaf:sn_candi})
                                            snode_mapped.append(sn_candi)
                                            break
                                        else:
                                            continue
                                    if link_map.__contains__(e):
                                        break
                                if link_map.__contains__(e):
                                    break
        if len(node_map)==req.number_of_nodes():
            sub_link = []
            for e in req.edges:
                sub_link.append(e)
            for srq in sub_reqs:
                for e in srq.edges:
                    sub_link.remove(e)
            for e in sub_link:
                sn_from = node_map[e[0]]
                sn_to = node_map[e[1]]
                if nx.has_path(sub, source=sn_from, target=sn_to):
                    for path in DC.k_shortest_path(sub, sn_from, sn_to, 5):
                        if DC.get_path_bw(sub, path) >= req[e[0]][e[1]]['bw'] \
                                and DC.get_path_delay(sub, path) <= req.graph['delay']:
                            link_map.update({e: path})
                            break
                        else:
                            continue
        return node_map, link_map

    def select_agent(self,req):
        max_nr=0
        agent_node=None
        rankz=self.node_rank(req)
        for i in req.nodes:
            if rankz[i]>max_nr:
                agent_node=i
                max_nr = rankz[i]
        return agent_node

    def sort_link(self,graph):
        link_need={}
        for e in graph.edges:
            link_need.update({e:graph[e[0]][e[1]]['bw']})
        link_need=sorted(link_need.items(),key=lambda item:item[1],reverse=True)
        return link_need

    def generate_tree(self,sub,node):
        node_tree={}
        deepth=0
        nodes=[node,]
        nodes_in_tree=[node,]
        while deepth<5:
            for snode in nodes:
                nodes_copy = []
                for i in nx.neighbors(sub,snode):
                    if i not in nodes_in_tree:
                        node_tree.setdefault(deepth, []).append(i)
                        nodes_copy.append(i)
                        nodes_in_tree.append(i)
                nodes=nodes_copy
            deepth += 1
        return node_tree

    def node_rank(self,graph):
        if graph.number_of_nodes()>50:
            n = graph.number_of_nodes()
            cpu_kind='cpu_remain'
        else:
            n = 22
            cpu_kind='cpu'
        total_cap=0
        rankb,ranka=[0 for i in range(n)],[0 for i in range(n)]
        pf, pj = np.zeros((n, n)), np.zeros((n, n))
        for i in graph.nodes:
            graph.nodes[i]['capacity']=graph.nodes[i][cpu_kind]*self.get_sum_bw(graph,i)
            total_cap += graph.nodes[i]['capacity']
        for i in graph.nodes:
            rankb[i] = graph.nodes[i]['capacity'] / total_cap
            for j in graph.nodes:
                pj[i][j] = graph.nodes[j]['capacity'] / total_cap
        for u in graph.nodes:
            total_pf = 0
            for w in nx.neighbors(graph, u):
                total_pf += graph.nodes[w]['capacity']
            for v in nx.neighbors(graph, u):
                pf[u][v] = graph.nodes[v]['capacity'] / total_pf
        eps, cnt = 1.0, 0
        while eps > 1e-6:
            eps=0
            cnt += 1
            for v in graph.nodes:
                pjz,pfz=0,0
                for u in graph.nodes:
                    pjz += pj[u][v]*rankb[u]*0.15
                for u in nx.neighbors(graph, v):
                    pfz += pf[u][v]*rankb[u]*0.85
                ranka[v] = pjz + pfz
                eps += (ranka[v] - rankb[v])**2
                rankb[v] = ranka[v]
            eps=math.sqrt(eps)
        node_rank={}
        for i in range(len(ranka)):
            node_rank.update({i:ranka[i]})
        return node_rank

    def get_sum_bw(self, graph, u, kind='bw'):
        """计算一个节点的相邻链路带宽和"""

        if graph.number_of_nodes()>50:
            kind="bw_remain"
        bw_sum = 0
        for v in graph.neighbors(u):
            bw_sum += graph[u][v][kind]
        return bw_sum

    def cut_req_graph(self, req):
        cen_node = {}
        graphs={}
        for i,j in nx.degree(req):
            cen_node.update({i: j})
        cen_node=sorted(cen_node.items(),key=lambda item:item[1],reverse=True)
        while len(cen_node)>1:
            for k, v in cen_node:
                for u in nx.neighbors(req, k):
                    if nx.degree(req)[u] <= v and (u,nx.degree(req)[u]) in cen_node:
                        graphs.setdefault(k, []).append(u)
                        cen_node.pop(cen_node.index((u,nx.degree(req)[u])))
                if graphs.__contains__(k) and len(graphs[k])>0:
                    cen_node.pop(cen_node.index((k, v)))
        simple_reqs = [[] for i in range(len(graphs))]
        count=0
        length=20
        for v,k in graphs.items():
            simple_reqs[count]=[v,]+k
            length=min(length,len(k))
            count+=1
        if len(cen_node)>0:
            last_node=cen_node[0][0]
            simple_reqs[-1].append(last_node)
        sub_reqs=[]
        for i in range(len(simple_reqs)):
            sub_req=copy.deepcopy(req)
            for j in range(req.number_of_nodes()):
                if j not in simple_reqs[i]:
                    sub_req.remove_node(j)
            sub_reqs.append(sub_req)

        return sub_reqs

    @staticmethod
    def k_shortest_path(graph, source, target, k=5):
        """K最短路径算法"""
        return list(islice(nx.shortest_simple_paths(graph, source, target), k))

    @staticmethod
    def get_path_bw(sub, path):
        """找到一条路径中带宽资源最小的链路并返回其带宽资源值"""

        bandwidth = 1000
        head = path[0]
        for tail in path[1:]:
            if sub[head][tail]['bw_remain'] <= bandwidth:
                bandwidth = sub[head][tail]['bw_remain']
            head = tail
        return bandwidth

    @staticmethod
    def get_path_delay(sub, path):
        """calculate delay for path"""

        sum_delay = 0
        head = path[0]
        for tail in path[1:]:
            sum_delay += sub[head][tail]['dl']
            head = tail
        return sum_delay




