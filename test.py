from compare3_MC.mc import MC

from network import Network

net=Network('networks/')
sub,que=net.get_networks("sub-ts.txt",10)
req=que[2]
mc=MC(0.83,0,0)
mc.run(sub,req)
# print(mc.LA(req))