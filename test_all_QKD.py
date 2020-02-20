# -*- coding: utf-8 -*-
import sys
sys.path.append("lib")
print(sys.version)
print(sys.path)

import bisim_concrete as bisim
import time

print("Weak Bisimulation Test")
print("===================\nBB84")
qlts_timer = time.time()
bisim.init_qLTS("examples/concreteBB84.txt", "parse_output/concreteBB84.gv",
          "examples/weak_concreteBB84-spec.txt", "parse_output/weak_concreteBB84-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
# print("===================\nBB84 with an eavesdropper, need several hours")
# qlts_timer = time.time()
# bisim.init_qLTS("examples/concreteBB84-eavesdropper-m.txt", "parse_output/concreteBB84-eavesdropper-m.gv",
#           "examples/weak_concreteBB84-eavesdropper-spec-m.txt", "parse_output/weak_concreteBB84-eavesdropper-spec-m.gv")
# print("pLTS Generate in ", time.time() - qlts_timer)
# bisim.Weak_Bisimulation(0,0)
print("===================\nB92")
qlts_timer = time.time()
bisim.init_qLTS("examples/weak_concreteB92.txt", "parse_output/weak_concreteB92.gv",
          "examples/weak_concreteB92-spec.txt", "parse_output/weak_concreteB92-sepc.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
print("===================\nE91")
qlts_timer = time.time()
bisim.init_qLTS("examples/weak_concreteE91.txt", "parse_output/weak_concreteE91.gv",
          "examples/weak_concreteE91-spec.txt", "parse_output/weak_concreteE91-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
