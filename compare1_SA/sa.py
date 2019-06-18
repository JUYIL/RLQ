import numpy as np
import os
import copy


class SA:
    def __init__(self):
        pass

    def run(self, sub, req):
        node_map = {}
        req_type = self.get_req_type(req)
        sub_cut = self.get_cut_graph(sub,req)
        out_file = self.create_data_file(sub_cut, req, req_type)
        if out_file==-1:
            return node_map
        poss_map = self.read_out_file(out_file)
        print(poss_map)
        if poss_map==-1 or len(poss_map)== 0:
            return node_map
        choosen_id=[]
        for i in range(req.number_of_nodes()):
            candidate=poss_map[i]
            # pro = []
            # for j in range(len(candidate)):
            #     pro.append(candidate[j][1])
            # max_pro = max(pro)
            # ind = pro.index(max_pro)
            # sid=candidate[ind][0]
            # if sid not in choosen_id:
            #     choosen_id.append(sid)
            #     node_map.update({i: sid})
            for j in range(len(candidate)):
                if candidate[j][1]>0:
                    sid = candidate[j][0]
                    if sid not in choosen_id:
                        choosen_id.append(sid)
                        node_map.update({i:sid})
                        break
                    else:
                        continue
        print(node_map)

        return node_map

    def create_data_file(self, sub, req, req_type):
        """run LP"""
        self.num1 = sub.number_of_nodes()
        self.num2 = req.number_of_nodes()
        self.num3 = self.num1 + self.num2
        data_file='compare1_SA/LP/type%d.dat' % req_type
        mode_file='compare1_SA/LP/type%d.mod' % req_type
        out_file='compare1_SA/LP/type%d.out' % req_type
        # get sub bw_remain matrix
        bw_matrix=self.get_bw_matrix(sub)
        # get sub delay matrix
        delay_matrix = self.get_delay_matrix(sub)
        # get valid sub node for req
        # count=self.num2
        # for i in range(self.num2):
        #     valid_node_count,valid_node_list=self.find_nodes_with_constrain(sub,req,i)
        #     if valid_node_count==0:
        #         count -= 1
        #         print('valid node count is 0')
        #         break
            # for j in range(len(valid_node_list)):
            #     bw_matrix[valid_node_list[j]][self.num1+i]=\
            #         bw_matrix[self.num1+i][valid_node_list[j]]=1000000
            #     delay_matrix[valid_node_list[j]][self.num1 + i] = \
            #         delay_matrix[self.num1 + i][valid_node_list[j]] = 0
        # if count != self.num2:
        #     print('node map filed')
        #     return -1
        # create data file
        with open(data_file, 'w') as f:
            f.write("data;\n\n")
            # substrate node set
            f.write("set N:=")
            for i in range(self.num1):
                f.write(" %d" % i)
            f.write(";\n")
            # req node set
            f.write("set M:=")
            for i in range(self.num2):
                f.write(" %d" % (self.num1+i))
            f.write(";\n")
            # req edge set
            f.write("set F:=")
            for i in range(req.number_of_edges()):
                f.write(" f%d" % i)
            f.write(";\n\n")
            # cpu resource of the sub and req nodes
            f.write("param p:=\n")
            for i in range(self.num1):
                f.write("%d\t%.4lf\n" % (i, sub.nodes[i]['cpu_remain']))
            for i in range(self.num2):
                f.write("%d\t%.4lf\n" % ((self.num1 + i), req.nodes[i]['cpu']))
            f.write(";\n\n")
            # bandwidth resource of the sub and req edges
            f.write("param b:\n")
            for i in range(self.num3):
                f.write("%d " % i)
            f.write(":=\n")
            for i in range(self.num3):
                f.write("%d " % i)
                for j in range(self.num3):
                    f.write("%.4lf " % bw_matrix[i][j])
                f.write("\n")
            f.write(";\n\n")
            # delay of the sub edges
            f.write("param d:\n")
            for i in range(self.num3):
                f.write("%d " % i)
            f.write(":=\n")
            for i in range(self.num3):
                f.write("%d " % i)
                for j in range(self.num3):
                    f.write("%.4lf " % delay_matrix[i][j])
                f.write("\n")
            f.write(";\n\n")
            # flow source
            f.write("param fs:=\n")
            ii=0
            for e in req.edges:
                f.write("f%d %d\n" % (ii, (e[0]+self.num1)))
                ii+=1
            f.write(";\n\n")
            # flow destination
            f.write("param fe:=\n")
            ii=0
            for e in req.edges:
                f.write("f%d %d\n" % (ii, (e[1]+self.num1)))
                ii+=1
            f.write(";\n\n")
            # flow requirements
            f.write("param fd:=\n")
            ii = 0
            for e in req.edges:
                f.write("f%d %.4lf\n" % (ii, req[e[0]][e[1]]['bw']))
                ii += 1
            f.write(";\n\n")
            # flow delay
            f.write("param fy:=\n")
            ii = 0
            for e in req.edges:
                f.write("f%d %.4lf\n" % (ii, req.graph['delay']))
                ii += 1
            f.write(";\n\n")
            f.write("end;\n\n")
        # call glpsol
        print('run glpsol')
        os.system("glpsol --model %s --data %s --output %s --tmlim 2" % (mode_file,data_file,out_file))
        return out_file

    def read_out_file(self, out_file):

        # read flow information
        # x_matrix = np.zeros((self.num3, self.num3))
        # flow_matrix = np.zeros((self.num3, self.num3))
        poss_map={}
        with open(out_file) as f:
            lines = f.readlines()
            _, result = lines[4].split()
            if result != "OPTIMAL":
                return -1
            for line in lines[10000:]:
                list2 = [x for x in line.split()]
                if len(list2) == 0 or list2[1][:2] != "x[":
                    pass
                elif list2[1][:2] == "x[":
                    fs, ft = list2[1][2:-1].split(",")
                    fs, ft = int(fs), int(ft)
                    fval = float(list2[3])
                    if fs >= self.num1 > ft and fval > 0:
                        poss_map.setdefault(fs - 100, []).append((ft, fval))
        return poss_map

    def get_bw_matrix(self,sub):
        """get sub bw_remain matrix"""

        bw_matrix=np.zeros((self.num3, self.num3))
        for e in sub.edges:
            bw_matrix[e[0]][e[1]] = bw_matrix[e[1]][e[0]] = sub[e[0]][e[1]]['bw_remain']
        return bw_matrix

    def get_delay_matrix(self,sub):
        """get sub delay matrix"""

        dl_matrix=np.zeros((self.num3, self.num3))
        for e in sub.edges:
            dl_matrix[e[0]][e[1]] = dl_matrix[e[1]][e[0]] = sub[e[0]][e[1]]['dl']
        return dl_matrix


    # def find_nodes_with_constrain(self,sub,req,node_id):
    #     """find sub nodes for each req node with cpu constrain"""
    #
    #     count=0
    #     valid_node_id=[]
    #     for i in range(self.num2):
    #         if sub.nodes[i]['cpu_remain'] >= req.nodes[node_id]['cpu']:
    #             valid_node_id.append(i)
    #             count += 1
    #     return count, valid_node_id

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

    def get_cut_graph(self, sub, req):
        """剪枝操作"""

        resource = 0
        for vLink in req.edges:
            vn_from, vn_to = vLink[0], vLink[1]
            vbw = req[vn_from][vn_to]['bw']
            if vbw>resource:
                resource=vbw

        sub_tmp = copy.deepcopy(sub)
        sub_edges = []
        for sLink in sub_tmp.edges:
            sub_edges.append(sLink)
        for edge in sub_edges:
            sn_from, sn_to = edge[0], edge[1]
            if sub_tmp[sn_from][sn_to]['bw_remain'] <= resource:
                sub_tmp.remove_edge(sn_from, sn_to)
        return sub_tmp
