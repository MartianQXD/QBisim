# QBisim
A tool for verifying bisimulation of quantum programs.

How to run:

1. Open a Terminal at the same directory and execute: 
 
```
python bisim_concrete.py
```
2. Choose the module for checking strong bisimulation or weak bisimulation.

```
Weak
```
3. Input the program paths and result paths of the examples in order, such as: 

```
examples/concrete1-1.txt

parse_output/concrete1-1.gv

examples/weak_concrete1-2.txt

parse_output/weak_concrete1-2.gv
```
If module for checking strong bisimulation is chosen, the second file should be 

```
examples/concrete1-2.txt

parse_output/concrete1-2.gv
```
where the difference is there are several "tau" actions added into the program.
And the result will print in the terminal like:

```
NonBisim:  []

Bisim:  22

Bisimilar

0.13887596130371094
```

And the generated pLTSs can be found in folder "parse_output" as "concrete1-1.gv.pdf" and "weak_concrete1-2.gv.pdf".

<!--<img src="parse_output/concrete1-1.gv.pdf" height="1000"/>
<img src="parse_output/concrete1-2.gv.pdf" height="1000"/>-->

#### Input Files and Correspoonding Output Files

##### For Weak Bisimulation
Input | Output | Remark
-|-|-
concrete1-1.txt | weak_concrete1-2.txt
concrete2-1.txt | concrete2-2.txt
concrete3-1.txt | weak_concrete3-2.txt | Change the initial value of $x$ in both files to test each case
concrete3-1-m.txt | weak_concrete3-2-m.txt
concrete4-1.txt | weak_concrete4-2.txt
concreteBB84.txt | weak_concreteBB84-spec.txt
concreteB92.txt | weak_concreteB92-spec.txt
concreteE91.txt | weak_concreteE91-spec.txt

##### For Strong Bisimulation
Input | Output | Remark
-|-|-
concrete1-1.txt | concrete1-2.txt
concrete2-1.txt | concrete2-2.txt
concrete3-1.txt | concrete3-2.txt | Change the initial value of $x$ in both files to test each case.
concrete3-1-m.txt | concrete3-2-m.txt
concrete4-1.txt | concrete4-2.txt
concreteBB84.txt | concreteBB84-spec.txt
concreteB92.txt | concreteB92-spec.txt
concreteE91.txt | concreteE91-spec.txt
concreteBB84-eavesdropper.txt | concreteBB84-eavesdropper-spec.txt | Terminate in a early time-point reuslting $\texttt{Not Bisimilar}$.
concreteBB84-eavesdropper-m.txt | concreteBB84-eavesdropper-spec-m.txt | Around 1 hour.