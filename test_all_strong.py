# -*- coding: utf-8 -*-
import sys
sys.path.append("lib")
print(sys.version)
print(sys.path)

import bisim_concrete as bisim
import time

print("Strong Bisimulation Test")
print("===================\nTeleportation")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete1-1.txt", "parse_output/concrete1-1.gv",
          "examples/concrete1-2.txt", "parse_output/concrete1-2.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nSDC")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete3-1.txt", "parse_output/concrete3-1.gv",
          "examples/concrete3-2.txt", "parse_output/concrete3-2.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete3-1-m.txt", "parse_output/concrete3-1-m.gv",
          "examples/concrete3-2-m.txt", "parse_output/concrete3-2-m.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nSecret Sharing")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete4-1.txt", "parse_output/concrete4-1.gv",
          "examples/concrete4-2.txt", "parse_output/concrete4-2.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
