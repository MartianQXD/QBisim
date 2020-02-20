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
bisim.init_qLTS("examples/concrete-tele.txt", "parse_output/concrete-tele.gv",
          "examples/concrete-tele-spec.txt", "parse_output/concrete-tele-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nSDC, x=1")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete-sdc.txt", "parse_output/concrete-sdc.gv",
          "examples/concrete-sdc-spec.txt", "parse_output/concrete-sdc-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nSDC modified, x=5")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete-sdc-m.txt", "parse_output/concrete-sdc-m.gv",
          "examples/concrete-sdc-spec-m.txt", "parse_output/concrete-sdc-spec-m.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nSecret Sharing")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete-ss.txt", "parse_output/concrete-ss.gv",
          "examples/concrete-ss-spec.txt", "parse_output/concrete-ss-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
