# QBisim
A tool for verifying bisimulation of quantum programs.

How to run:

1. Open a Terminal at the same directory and execute: 
 
```
python bisim_concrete.py
```

2. Input the program paths and result paths of the examples in order, such as: 

```
examples/concrete1-1.txt

parse_output/concrete1-1.gv

examples/concrete1-2.txt

parse_output/concrete1-2.gv
```
And the result will print in the terminal like:

```
NonBisim:  []

Bisim:  22

Bisimilar

0.01887989044189453
```

And the generated pLTSs can be found in folder "parse_output" as following:

<!--<img src="parse_output/concrete1-1.gv.pdf" height="1000"/>
<img src="parse_output/concrete1-2.gv.pdf" height="1000"/>-->
