/*
    X091.m

    This is based on Box's code from his Github repo. It sets up the various
    ingredients required for the spectacular finale, a bespoke Mordell-Weil sieve.
    Various bits of this code take several hours to complete.

    At the time of committing this code, it is not known if the final call to
    MWSieve actually returns true. If it does not, one can try changing the primes
    and hoping for the best.

*/

load "boxozmansiksek.m";

X,ws:=ModCrvQuot(91,[],[91]); //Just a few minutes.
w:=ws[1];
assert Genus(X) eq 7;

cusps:=PointSearch(X,500);
numcusps := #cusps;
Dtors:=[Place(cusps[i])-Place(cusps[1]) : i in [2..4]];

p:=11;
Xp:=ChangeRing(X,GF(p));
JFp,phi,psi:=JacobianFp(Xp);
redDtors:=[JFp!psi(reduce(X,Xp,DD)) : DD in Dtors];
A:=sub<JFp | redDtors>;

C,projC:=CurveQuotient(AutomorphismGroup(X,[w]));  // takes a few hours
C,h:=SimplifiedModel(C);
XtoC:=Expand(projC*h);
assert Genus(C) eq 2;
ptsC:=Setseq(Points(C : Bound:=1000));
J:=Jacobian(C);
ptsJ:=[pt-ptsC[2] : pt in ptsC];

for pt in ptsJ do
	if Order(pt) eq 3 then
		Q3 := pt;  // this is a generator for the torsion subgroup which we actually don't need anyway
		break;
	end if;
end for;

Q1:=ptsJ[1];
Q2:=ptsJ[4];
bas,M:=ReducedBasis([Q1,Q2]);
assert #bas eq 2;//This shows J(C)(\Q) has rank 2;
//We will show that Q1,Q2 are a basis using Stoll's algorithm
N:=Orthogonalize(M);
absbd:=Ceiling(Exp((N[1,1]^2+N[1,2]^2+N[2,1]^2+N[2,2]^2)/4+HeightConstant(J)));
//J(C)(\Q) is generated by P1,P2 and all points of height up to absbd.
PtsUpToAbsBound:=Points(J : Bound:=absbd);
assert ReducedBasis([pt : pt in PtsUpToAbsBound]) eq [Q1,Q2]; //This shows Q1,Q2 are a basis.

D1:=Pullback(XtoC,Place(ptsC[1])-Place(ptsC[2]));
D2:=Pullback(XtoC,Place(ptsC[4])-Place(ptsC[2]));
bp:=Pullback(XtoC,Place(ptsC[2]));

B:=AbelianGroup([2,168]);
tf,isomm:=IsIsomorphic(A,B);
assert &and[isomm(A.i) eq B.i : i in [1,2]];
Z3:=FreeAbelianGroup(3);
hh:=hom<Z3-> A | redDtors>;
assert hh(-39*Z3.1 - 77*Z3.2) eq A.1;
assert hh(13*Z3.1 + 26*Z3.2) eq A.2;

divs:=[D1,D2,-39*Dtors[1] - 77*Dtors[2],13*Dtors[1]+26*Dtors[2]];

genusC:=Genus(C);
final_A:=AbelianGroup([0,0,2,168]);
I:=2;
auts:=[Transpose(Matrix(w))];

deg2:=Setseq({Pullback(XtoC,Place(c_point)) : c_point in ptsC} join {Place(pt1) + Place(pt2) : pt1 in cusps, pt2 in cusps});  // takes about 14 hours
deg2npb:=[Place(pt1) + Place(pt2) : pt1 in cusps, pt2 in cusps | not w(pt1) eq pt2]; // takes several hours, less than 12
deg2pb:=[DD : DD in deg2 | not DD in deg2npb]; //We split into pullbacks and non-pullbacks.  // takes a few hours

load "quadptssieve.m";
primes:=[17, 11, 23, 19, 29];
// MWSieve(deg2,primes,X,final_A,divs,auts,genusC,deg2pb,deg2npb,I,bp); //Returns true if we have indeed found all deg 2 pts.

jacs:=[]; // This will be a list of J(X)(\F_p) for p in primes.
divlist:=[[]: i in [1..#divs]]; // divlist[i] is a list of the divisors reduce(X,Xp,div[i]).


for p in [43, 67] do
p;
Fp:=GF(p);
Xpp:=ChangeRing(X,Fp);
CGp,phi_cg,psi_cg:=ClassGroup(Xpp);
Z:=FreeAbelianGroup(1);
degr:=hom<CGp->Z | [ Degree(phi_cg(a))*Z.1 : a in OrderedGenerators(CGp)]>;
JFp:=Kernel(degr); // This is isomorphic to J_X(\F_p).
Append(~jacs,JFp);
for i in [1..#divs] do
Dip:=JFp!psi_cg(reduce(X,Xpp,divs[i]));
Dipseq:=Eltseq(Dip);
Dipseq:=Dipseq cat [0*i : i in [1..(100-#Dipseq)]]; //We convert divisors into a sequence of length 100 in order to save them in a list
Append(~divlist[i],Dipseq);
end for;
end for;
primes:=[17, 11, 23, 19, 29, 31, 37, 43, 67];
MWSieveShort(deg2,primes,X,final_A,divs,auts,genusC,deg2pb,deg2npb,I,bp,jacs,divlist);

// reset

jacs:=[];
divlist:=[[]: i in [1..#divs]];
primes:=[43, 67, 11, 37, 17, 31, 23, 19, 29, 71];

for p in primes do
p;
Fp:=GF(p);
Xpp:=ChangeRing(X,Fp);
CGp,phi_cg,psi_cg:=ClassGroup(Xpp);
Z:=FreeAbelianGroup(1);
degr:=hom<CGp->Z | [ Degree(phi_cg(a))*Z.1 : a in OrderedGenerators(CGp)]>;
JFp:=Kernel(degr); // This is isomorphic to J_X(\F_p).
Append(~jacs,JFp);
for i in [1..#divs] do
Dip:=JFp!psi_cg(reduce(X,Xpp,divs[i]));
Dipseq:=Eltseq(Dip);
Dipseq:=Dipseq cat [0*i : i in [1..(100-#Dipseq)]]; //We convert divisors into a sequence of length 100 in order to save them in a list
Append(~divlist[i],Dipseq);
end for;
end for;
MWSieveShort(deg2,primes,X,final_A,divs,auts,genusC,deg2pb,deg2npb,I,bp,jacs,divlist);
