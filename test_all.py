# -*- coding: utf-8 -*-
import sys
sys.path.append("lib")
print(sys.version)
print(sys.path)

import bisim_concrete as bisim
import time

print("Weak Bisimulation Test")
print("===================\nTeleportation")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete-tele.txt", "parse_output/concrete-tele.gv",
          "examples/weak_concrete-tele-spec.txt", "parse_output/weak_concrete-tele-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
print("===================\nSDC, x=1")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete-sdc.txt", "parse_output/concrete-sdc.gv",
          "examples/weak_concrete-sdc-spec.txt", "parse_output/weak_concrete-sdc-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
print("===================\nSDC modified, x=5")
qlts_timer = time.time()
bisim.init_qLTS("examples/weak_concrete-sdc-m.txt", "parse_output/weak_concrete-sdc-m.gv",
          "examples/weak_concrete-sdc-spec-m.txt", "parse_output/weak_concrete-sdc-spec-m.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
print("===================\nSecret Sharing")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete-ss.txt", "parse_output/concrete-ss.gv",
          "examples/weak_concrete-ss-spec.txt", "parse_output/weak_concrete-ss-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
