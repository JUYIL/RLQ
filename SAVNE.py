import numpy as np
import os


class SA:
    def __init__(self,t):
        self.t=t

    # def run(self, sub, vnr):
    #     node_map = {}
    #     sub_copy=copy.deepcopy(sub)
    #     for v_node in vnr_grc_vector:
    #         v_id = v_node[0]
    #         for s_node in sub_grc_vector:
    #             s_id = s_node[0]
    #             if s_id not in node_map.values() and \
    #                     sub.net.nodes[s_id]['cpu_remain'] > vnr.nodes[v_id]['cpu']:
    #                 node_map.update({v_id: s_id})
    #                 tmp=sub_copy.nodes[s_id]['cpu_remain']-vnr.nodes[v_id]['cpu']
    #                 sub_copy.nodes[s_id]['cpu_remain']=round(tmp,6)
    #                 break
    #     return node_map

    def create_data_file(self, sub, req):
        """run LP"""

        num1 = sub.number_of_nodes()
        num2 = req.number_of_nodes()
        num3 = num1 + num2
        type='type1'
        data_file='LP/%s.dat' % type
        mode_file='LP/%s.mod' % type
        out_file='LP/%s.out' % type
        # make all sub nodes untouched
        for i in range(num1):
            sub.nodes[i]['touched'] = False
        # get sub bw_remain matrix
        bw_matrix=self.get_bw_matrix(sub, num3)
        # get valid sub node for req
        count=num2
        for i in range(num2):
            valid_node_count,valid_node_list=self.find_nodes_with_constrain(sub,req,i)
            if valid_node_count==0:
                count -= 1
                print('valid node count is 0')
                break
            for j in range(len(valid_node_list)):
                bw_matrix[valid_node_list[j]][num1+i]=\
                    bw_matrix[num1+i][valid_node_list[j]]=1000000
        if count != num2:
            print('node map filed')
            return -1
        # create data file
        with open(data_file, 'w') as f:
            f.write("data;\n\n")
            # substrate node set
            f.write("set N:=")
            for i in range(num1):
                f.write(" %d" % i)
            f.write(";\n")
            # req node set
            f.write("set M:=")
            for i in range(num2):
                f.write(" %d" % (num1+i))
            f.write(";\n")
            # req edge set
            f.write("set F:=")
            for i in range(req.number_of_edges()):
                f.write(" f%d" % i)
            f.write(";\n\n")
            # cpu resource of the sub and req nodes
            f.write("param p:=\n")
            for i in range(num1):
                f.write("%d\t%.4lf\n" % (i, sub.nodes[i]['cpu_remain']))
            for i in range(num2):
                f.write("%d\t%.4lf\n" % ((num1 + i), req.nodes[i]['cpu']))
            f.write(";\n\n")
            # bandwidth resource of the sub and req edges
            f.write("param b:\n")
            for i in range(num3):
                f.write("%d " % i)
            f.write(":=\n")
            for i in range(num3):
                f.write("%d " % i)
                for j in range(num3):
                    f.write("%.4lf " % bw_matrix[i][j])
                f.write("\n")
            f.write(";\n\n")
            # flow source
            f.write("param fs:=\n")
            ii=0
            for e in req.edges:
                f.write("f%d %d\n" % (ii, (e[0]+num1)))
                ii+=1
            f.write(";\n\n")
            # flow destination
            f.write("param fe:=\n")
            ii=0
            for e in req.edges:
                f.write("f%d %d\n" % (ii, (e[1]+num1)))
                ii+=1
            f.write(";\n\n")
            # flow requirements
            f.write("param fd:=\n")
            ii = 0
            for e in req.edges:
                f.write("f%d %.4lf\n" % (ii, req[e[0]][e[1]]['bw']))
                ii += 1
            f.write(";\n\n")
            f.write("end;\n\n")
        # call glpsol
        print('run glpsol')
        os.system("glpsol --model %s --data %s --output %s --tmlim 2" % (mode_file,data_file,out_file))



    def read_out_file(self, out_file,num):

        result_matrix = np.zeros((num, num))
        line_num=100000
        with open(out_file) as f:
            lines = f.readlines()
            _, result = lines[4].split()
            if result != "OPTIMAL":
                return -1
            while line_num < len(lines):
                line = lines[line_num]
                list1 = [x for x in line.split()]
                if len(list1) == 0:
                    pass
                else:
                    string = list1[1]
                    if string[:2] != "f[":
                        pass
                    else:
                        fid, fs, ft = string[2:-1].split(",")
                        if len(list1) == 2:
                            line_num += 1
                            line = lines[line_num]
                            list1 = [x for x in line.split()]
                        fval = float(list1[-1])
                        result_matrix[fs][ft] += fval
                        line_num += 1




    def get_bw_matrix(self,sub,num):
        """get sub bw_remain matrix"""

        bw_matrix=np.zeros((num, num))
        for e in sub.edges:
            bw_matrix[e[0]][e[1]] = bw_matrix[e[1]][e[0]] = sub[e[0]][e[1]]['bw_remain']
        return bw_matrix

    def find_nodes_with_constrain(self,sub,req,node_id):
        """find sub nodes for each req node with cpu constrain"""

        count=0
        valid_node_id=[]
        for i in range(req.number_of_nodes()):
            if sub.nodes[i]['cpu_remain'] >= req.nodes[node_id]['cpu'] and\
                    sub.nodes[i]['touched'] is False:
                valid_node_id.append(i)
                count += 1
        return count, valid_node_id

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
