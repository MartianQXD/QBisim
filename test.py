# -*- coding: utf-8 -*-
import sys
sys.path.append("lib")
print(sys.version)
print(sys.path)

import bisim_concrete as bisim
import time

checker = input('[Strong/Weak] > ')
in_1 = input('file 1 name > ')
out_1 = input('output file 1 name > ')
in_2 = input('file 2 name > ')
out_2 = input('output file 2 name > ')
qlts_timer = time.time()
bisim.init_qLTS(in_1, out_1, in_2, out_2)
print("pLTS Generate in ", time.time() - qlts_timer)
if (checker=='Strong') or (checker=='strong'):
    bisim.Bisimulation(0, 0)
if (set(checker)==('S','s','T','t','R','r','O','o','N','n','G','g') and len(checker)<8):
    bisim.Bisimulation(0, 0)
if (checker=='Weak') or (checker=='weak'):
    bisim.Weak_Bisimulation(0,0)
if (set(checker)==('W','w','E','e','A','a','K','k') and len(checker)<6):
    bisim.Weak_Bisimulation(0,0)
