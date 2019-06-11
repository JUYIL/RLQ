import numpy as np
import copy


class SA:
    def __init__(self, damping_factor, sigma):
        self.damping_factor = damping_factor
        self.sigma = sigma
        self.migrate_success = False
        self.no_solution = False

    def run(self, sub, vnr):
        node_map = {}
        sub_copy=copy.deepcopy(sub.net)
        for v_node in vnr_grc_vector:
            v_id = v_node[0]
            for s_node in sub_grc_vector:
                s_id = s_node[0]
                if s_id not in node_map.values() and \
                        sub.net.nodes[s_id]['cpu_remain'] > vnr.nodes[v_id]['cpu']:
                    node_map.update({v_id: s_id})
                    tmp=sub_copy.nodes[s_id]['cpu_remain']-vnr.nodes[v_id]['cpu']
                    sub_copy.nodes[s_id]['cpu_remain']=round(tmp,6)
                    break
        return node_map

    def get_average_bw(self, req):
        """get average_bw for req"""

        pass

    def get_req_type(self, req):
        """get req type based on delay and bandwidth"""
        sum = 0
        for vlink in req.edges:
            sum += req[vlink[0]][vlink[1]]['bw']
        req_av_bw = sum / req.number_of_edges()

        band, delay = 25, 100
        if req.graph['delay'] >= delay:
            req_type = 1
        elif req_av_bw <= band:
            req_type = 2
        else:
            req_type = 3
        return req_type
