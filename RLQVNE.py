from network import Network
import networkx as nx

net=Network('networks/')
sub,que=net.get_networks('sub-ts.txt',0)
for path in nx.edges(sub):
    print(sub[path[0]][path[1]]['dl'])