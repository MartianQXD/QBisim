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
Find .deg/.tar/.zip file of zliblg-dev, python and dependent packages in lib.

1. Install zliblg-dev. Click the zlib1g-dev_1.2.11.dfsg-0ubuntu2_amd64.deb.

2. Install Python 3.7.
    
Install bzip2:
    tar -zxf  bzip2-1.0.6.tar.gz 
    cd bzip2-1.0.6  
    make -f  Makefile-libbz2_so 
    make && make install
Install Python:
    tar -zxvf Python-3.7.6.tgz
    cd Python-3.7.6
    ./configure --prefix=/usr/local/python3.7 --enable-shared
    make
    sudo make install
    sudo rm -r /usr/bin/python3
    sudo ln -s /usr/local/python3.7/bin/python3 /usr/bin/python3
    sudo cp -R /usr/local/python3.7/lib/* /usr/lib
    sudo ln -s /usr/local/python3.7/bin/pip3 /usr/bin/pip
    sudo cp /usr/lib/python3/dist-packages/lsb_release.py /usr/local/python3.7/lib/python3.7
    cd ..

3. Install packages in order
wheel:
    tar -zxvf wheel-0.33.6.tar.gz
    cd wheel-0.33.6
    sudo python3 setup.py install
    cd ..
numpy:
    sudo pip install numpy-1.17.4-cp37-cp37m-manylinux1_x86_64.whl
pandas:
    sudo pip install pytz-2019.3-py2.py3-none-any.whl
    sudo pip install six-1.13.0-py2.py3-none-any.whl
    sudo pip install python_dateutil-2.8.0-py2.py3-none-any.whl
    sudo pip install pandas-0.25.3-cp37-cp37m-manylinux1_x86_64.whl
scipy:
    sudo pip install scipy-1.4.1-cp37-cp37m-manylinux1_x86_64.whl
graphviz:
    sudo pip install pyparsing-2.4.6-py2.py3-none-any.whl
    tar -zxvf pydot3-1.0.9.tar.gz
    cd pydot3-1.0.9
    sudo python3 setup.py install
    cd ..
    sudo pip install graphviz-0.13.2-py2.py3-none-any.whl

## How to run
1. Open a Terminal at the same directory and execute:
  
    python test_all.py

To see the result of all communication protocol examples. (Change the initial value of variables in files to test each case.)
And

    python test_all_QKD.py
    
To see the result of all QKD protocol examples. 

Or

1. Open a Terminal at the same directory and execute: 

    python test.py

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

And the generated pLTSs can be found in folder "parse_output" as "concrete1-1.gv" and "weak_concrete1-2.gv".

## Input Files and Correspoonding Output Files

##### For Weak Bisimulation
Input             | Output                       | Remark
concrete1-1.txt   | weak_concrete1-2.txt         | Teleportation protocol. Change the initial value of [q,q1,q2] in both files to test each case.
concrete2-1.txt   | concrete2-2.txt
concrete3-1.txt   | weak_concrete3-2.txt         | SDC protocol. Change the initial value of x in both files to test each case.
concrete3-1-m.txt | weak_concrete3-2-m.txt       | SDC protocol (modified). Change the initial value of x in both files to test each case.
concrete4-1.txt   | weak_concrete4-2.txt         | Secret sharing protocol. Change the initial value of [q,q1,q2,q3] in both files to test each case.
concreteBB84.txt  | weak_concreteBB84-spec.txt
concreteB92.txt   | weak_concreteB92-spec.txt
concreteE91.txt   | weak_concreteE91-spec.txt

##### For Strong Bisimulation
Input             | Output                       | Remark
concrete1-1.txt   | concrete1-2.txt              | Teleportation protocol. Change the initial value of [q,q1,q2] in both files to test each case.
concrete2-1.txt   | concrete2-2.txt
concrete3-1.txt   | concrete3-2.txt              | SDC protocol. Change the initial value of x in both files to test each case.
concrete3-1-m.txt | concrete3-2-m.txt            | SDC protocol (modified). Change the initial value of x in both files to test each case.
concrete4-1.txt   | concrete4-2.txt              | Secret sharing protocol. Change the initial value of [q,q1,q2,q3] in both files to test each case.
concreteBB84.txt  | concreteBB84-spec.txt
concreteB92.txt   | concreteB92-spec.txt
concreteE91.txt   | concreteE91-spec.txt
concreteBB84-     | concreteBB84-eavesdropper    | Terminate in a early time-point reuslting Not Bisimilar.
eavesdropper.txt  | -spec.txt                    | 
concreteBB84-     | concreteBB84-eavesdropper    | Around 1 hour.
eavesdropper-m.txt| -spec-m.txt                  | 