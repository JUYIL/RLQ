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

param d{u in NM, v in NM};
/* delay of edge (u,v) */ 

param fs{i in F};
/* flow start points */

param fe{i in F};
/* flow end points */

param fd{i in F};
/* flow bw demands */

param fy{i in F};
/* flow delay demands */

var f{i in F, u in NM, v in NM} >= 0;
/* indicator variable for links */

var x{u in NM, v in NM} >= 0;
/* indicator variable for nodes */

minimize cost: (sum{u in N, v in N} (sum{i in F} f[i, u, v] * fd[i] )  
              + (sum{w in N} (sum{m in M} x[m, w] * p[m]) ));

/* minimum cost */

s.t. cpucon{m in M, w in N}: p[w] >= x[m, w] * p[m];
/* cpu constraint */

s.t. bwcon{u in N, v in N}: (sum{i in F} f[i, u, v] * fd[i]) <= b[u, v] ;
/* bw constraint */

s.t. dlcon{i in F}: sum{u in N, v in N} f[i, u, v] * d[u, v] <= fy[i] ;
/* delay constraint */

s.t. metcon1{m in M}: sum{w in N} x[m, w] = 1;
s.t. metcon2{w in N}: sum{m in M} x[m, w] <= 1;
s.t. metcon3{i in F, u in N}: (sum{v in N} f[i, u, v]) = x[fs[i], u] - x[fe[i], u];
/* meta constraint - (sum{v in N} f[i, v, u]) */

s.t. bincon1{u in NM, v in NM}: x[u, v] = x[v, u];
s.t. bincon2{i in F, u in NM, v in NM}: f[i, u, v] = f[i, v, u];
/* binary constraint */

end;

