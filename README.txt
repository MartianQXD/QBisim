# QBisim
A tool for verifying bisimulation of quantum programs.

## Install packages
1. [z3-slover](https://pypi.org/project/z3-solver/)
2. [graphiviz](https://pypi.org/project/graphviz/)

## How to run
1. Open a Terminal at the same directory and execute: 

    python bisim_concrete.py

2. Choose the module for checking strong bisimulation or weak bisimulation.

    Weak

3. Input the program paths and result paths of the examples in order, such as: 

    examples/concrete1-1.txt

    parse_output/concrete1-1.gv

    examples/weak_concrete1-2.txt

    parse_output/weak_concrete1-2.gv

If module for checking strong bisimulation is chosen, while the second file should be 

    examples/concrete1-2.txt

    parse_output/concrete1-2.gv

where the difference is there are several "tau" actions added into the program. (the detail relations between input and output files are shown in the table below)
And the result will print in the terminal like:

    NonBisim:  []
    Bisim:  22
    Bisimilar
    0.13887596130371094

And the generated pLTSs can be found in folder "parse_output" as "concrete1-1.gv.pdf" and "weak_concrete1-2.gv.pdf".

## Input Files and Correspoonding Output Files

##### For Weak Bisimulation
Input             | Output                       | Remark
concrete1-1.txt   | weak_concrete1-2.txt
concrete2-1.txt   | concrete2-2.txt
concrete3-1.txt   | weak_concrete3-2.txt         | Change the initial value of x in both files to test each case
concrete3-1-m.txt | weak_concrete3-2-m.txt
concrete4-1.txt   | weak_concrete4-2.txt
concreteBB84.txt  | weak_concreteBB84-spec.txt
concreteB92.txt   | weak_concreteB92-spec.txt
concreteE91.txt   | weak_concreteE91-spec.txt

##### For Strong Bisimulation
Input             | Output                       | Remark
concrete1-1.txt   | concrete1-2.txt
concrete2-1.txt   | concrete2-2.txt
concrete3-1.txt   | concrete3-2.txt              | Change the initial value of x in both files to test each case.
concrete3-1-m.txt | concrete3-2-m.txt
concrete4-1.txt   | concrete4-2.txt
concreteBB84.txt  | concreteBB84-spec.txt
concreteB92.txt   | concreteB92-spec.txt
concreteE91.txt   | concreteE91-spec.txt
concreteBB84-     | concreteBB84-eavesdropper    | Terminate in a early time-point reuslting Not Bisimilar.
eavesdropper.txt  | -spec.txt                    | 
concreteBB84-     | concreteBB84-eavesdropper    | Around 1 hour.
eavesdropper-m.txt| -spec-m.txt                  | 