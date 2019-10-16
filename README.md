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
