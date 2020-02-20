# QBisim
A tool for verifying bisimulation of quantum programs.

## Install packages
1. [z3-slover](https://pypi.org/project/z3-solver/)
2. [graphviz](https://pypi.org/project/graphviz/)
3. [ply](https://pypi.org/project/ply/)
4. [pandas](https://pypi.org/project/pandas/)
5. [numpy](https://pypi.org/project/numpy/)
6. [scipy](https://pypi.org/project/scipy/)

#### Offline
Find .deg/.tar/.zip files in lib. Install packages in order.
1. numpy:
Double click to install:

    libblas3_3.7.1-4ubuntu1_amd64.deb
    libgfortran4_7.4.0-1ubuntu1_18.04.1_amd64.deb
    liblapack3_3.7.1-4ubuntu1_amd64.deb
    python3-numpy_1.13.3-2ubuntu1_amd64.deb

2. pandas:
Double click to install:

    python3-pandas-lib_0.22.0-4_amd64.deb
    python3-pandas_0.22.0-4_all.deb

3. scipy:
Double click to install:

    python3-decorator_4.1.2-1_all.deb
    python3-scipy_0.19.1-2ubuntu1_amd64.deb

4. graphviz:
Double click to install:

    libann0_1.1.2+doc-6_amd64.deb
    libcdt5_2.40.1-2_amd64.deb
    libcgraph6_2.40.1-2_amd64.deb
    libpathplan4_2.40.1-2_amd64.deb
    libgts-0.7-5_0.7.6+darcs121130-4_amd64.deb
    libgvc6_2.40.1-2_amd64.deb
    libgvpr2_2.40.1-2_amd64.deb
    liblab-gamut1_2.40.1-2_amd64.deb
    graphviz_2.40.1-2_amd64.deb
    python3-graphviz_0.8.4-2_all.deb
    python3-pyparsing_2.2.0+dfsg1-2_all.deb
    python3-pydot_1.2.3-1_all.deb

## How to run
1. Open a Terminal at the QBisim directory and execute test files such as:
  
    sudo python3 test_all.py

to see the result of all communication protocol examples.

Futhermore, use
    
    sudo python3 -W ignore test_all.py

to ignore the warning from python linear programming function. 
The warning message from ply (at the beginning of the execution) is print by itself.

The output in the terminal

    Weak Bisimulation Test
    ===================

means that the experiments start.

Then the result will be shown in the format:

    <Protocol name>
    pLTS size:  <implementation pLTS size>
    pLTS size:  <specification pLTS size>
    pLTS Generate in <total running time of generating two pLTSs>
    NonBisim:  <size of the set NonBisim>
    Bisim:  <size of the set Bisim>
    <wether two pLTSs are weak bisimilar>
    <running time of checking algorithm>
    ===================

e.g.
    Teleportation
    pLTS size:  34
    pLTS size:  3
    pLTS Generate in  0.30704784393310547
    NonBisim:  22
    Bisim:  22
    Weak Bisimilar
    1.1541142463684082
    ===================

(The SDC will return two results as a problem of the model is found in the first one and it is corrected in the second.)

And we can change the initial value of variables in files to test each case. 
For example, 
    1. Open "/examples/concrete1-1.txt"
    2. Modify the input qubits from
        [q,q1,q2] = 0.8660254038*[000] + 0.5000000000*[100]
       to
        [q,q1,q2] = [100]
    3. Run the test file again

Furthermore, we can use

    sudo python3 test_all_QKD.py
    
to see the results of all QKD protocol examples.

2. To see the result of strong bisimulation checking. Please run the file with a suffix '_strong'.
  
    sudo python3 test_all_strong.py
    sudo python3 test_all_QKD_strong.py

Or

1. Open a Terminal at the same directory and execute: 

    sudo python3 test.py

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

    pLTS size:  34
    pLTS size:  3
    pLTS Generate in  0.30704784393310547
    NonBisim:  22
    Bisim:  22
    Weak Bisimilar
    1.1541142463684082

And the generated pLTSs can be found in folder "parse_output" as "concrete1-1.gv" and "weak_concrete1-2.gv".

## Input Files and Correspoonding Output Files

##### For Weak Bisimulation
Input                   | Output                        | Remark
concrete-basic.txt      | concrete-basic-spec.txt
concrete-sdc.txt        | weak_concrete-sdc-spec.txt    | SDC protocol. Change the initial value of x in both files to test each case.
weak_concrete-sdc-m.txt | weak_concrete-sdc-spec-m.txt  | SDC protocol (modified). Change the initial value of x in both files to test each case.
concrete-tele.txt       | weak_concrete-tele-spec.txt   | Teleportation protocol. Change the initial value of [q,q1,q2] in both files to test each case.
concrete-ss.txt         | weak_concrete-ss-spec.txt     | Secret sharing protocol. Change the initial value of [q,q1,q2,q3] in both files to test each case.
concreteBB84.txt        | weak_concreteBB84-spec.txt
concreteB92.txt         | weak_concreteB92-spec.txt
concreteE91.txt         | weak_concreteE91-spec.txt
concreteBB84-           | weak_concreteBB84-            | Around 15 hours.
eavesdropper-m.txt      | eavesdropper-spec-m.txt                   | 

##### For Strong Bisimulation
Input                   | Output                        | Remark
concrete-basic.txt      | concrete-basic-spec.txt
concrete-sdc.txt        | concrete-sdc-spec.txt         | SDC protocol. Change the initial value of x in both files to test each case.
concrete-sdc-m.txt      | concrete-sdc-spec-m.txt       | SDC protocol (modified). Change the initial value of x in both files to test each case.
concrete-tele.txt       | concrete-tele-spec.txt        | Teleportation protocol. Change the initial value of [q,q1,q2] in both files to test each case.
concrete-ss.txt         | concrete-ss-spec.txt          | Secret sharing protocol. Change the initial value of [q,q1,q2,q3] in both files to test each case.
concreteBB84.txt        | concreteBB84-spec.txt
concreteB92.txt         | concreteB92-spec.txt
concreteE91.txt         | concreteE91-spec.txt
concreteBB84-           | concreteBB84-eavesdropper     | Terminate in a early time-point reuslting Not Bisimilar.
eavesdropper.txt        | -spec.txt                     | 
concreteBB84-           | concreteBB84-eavesdropper     | Around 1 hour.
eavesdropper-m.txt      | -spec-m.txt                   | 