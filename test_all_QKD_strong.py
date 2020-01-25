# -*- coding: utf-8 -*-
import sys
sys.path.append("lib")
print(sys.version)
print(sys.path)

import bisim_concrete as bisim
import time

print("Strong Bisimulation Test")
print("===================\nBB84")
qlts_timer = time.time()
bisim.init_qLTS("examples/concreteBB84.txt", "parse_output/concreteBB84.gv",
          "examples/concreteBB84-spec.txt", "parse_output/concreteBB84-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nBB84 with an eavesdropper")
qlts_timer = time.time()
bisim.init_qLTS("examples/concreteBB84-eavesdropper-m.txt", "parse_output/concreteBB84-eavesdropper-m.gv",
          "examples/concreteBB84-eavesdropper-spec-m.txt", "parse_output/concreteBB84-eavesdropper-spec-m.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nB92")
qlts_timer = time.time()
bisim.bisim.init_qLTS("examples/concreteB92.txt", "parse_output/concreteB92.gv",
          "examples/concreteB92-spec.txt", "parse_output/concreteB92-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
print("===================\nE91")
qlts_timer = time.time()
bisim.init_qLTS("examples/concreteEPR.txt", "parse_output/concreteEPR.gv",
          "examples/concreteEPR-spec.txt", "parse_output/concreteEPR-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Bisimulation(0, 0)
