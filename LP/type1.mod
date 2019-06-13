set N;
/* substrate nodes*/

set M;
/* meta nodes */

set NM := N union M;
/* substrate and meta nodes */

set F;
/* virtual links */

param p{i in NM};
/* cpu of node i */

param b{u in NM, v in NM};
/* bandwidth of edge (u,v) */ 

param c{u in NM, v in NM};
/* cost of edge (u,v) */ 

param fs{i in F};
/* flow start points */

param fe{i in F};
/* flow end points */

param fd{i in F};
/* flow demands */

var f{i in F, u in NM, v in NM} >= 0;
/* flow variable */

var x{u in NM, v in NM} >= 0;
/* indicator variable */

minimize cost: (sum{u in N, v in N} ((sum{i in F} f[i, u, v] / (b[u, v] + 1E-6)))
        + (sum{w in N} ((sum{m in M} (x[m, w] * p[m]))/ (p[w] + 1E-6))));

/* minimum cost multi-commodity flow */

s.t. capcon{u in NM, v in NM}: sum{i in F} (f[i, u, v] + f[i, v, u]) <= b[u,v];
/* capacity constraint */

s.t. demsat1{i in F}: sum{w in NM} f[i, fs[i], w] - sum{w in NM} f[i, w, fs[i]] = fd[i];
s.t. demsat2{i in F}: sum{w in NM} f[i, fe[i], w] - sum{w in NM} f[i, w, fe[i]] = -fd[i];
/* demand satisfaction */

s.t. flocon{i in F, u in NM diff {fs[i], fe[i]}}: sum{w in NM} f[i, u, w] - sum{w in NM} f[i, w, u] = 0;
/* flow conservation */

s.t. cpucon{m in M, w in N}: p[w] >= x[m, w] * p[m];
/* cpu constraint */

s.t. metcon1{u in NM, v in NM}: sum{i in F} f[i, u, v] <= b[u, v] * x[u, v];
s.t. metcon2{u in NM, v in NM}: sum{i in F} f[i, u, v] <= b[u, v] * x[v, u];
s.t. metcon3{m in M}: sum{w in N} x[m, w] = 1;
s.t. metcon4{w in N}: sum{m in M} x[m, w] <= 1;
s.t. metcon5{u in NM, v in NM}: x[u, v] <= b[u,v];
/* meta constraint */

s.t. bincon{u in NM, v in NM}: x[u, v] = x[v, u];
/* binary constraint */

end;

