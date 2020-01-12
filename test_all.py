import sys
sys.path.append("lib")
print(sys.version)
print(sys.path)

import bisim_concrete as bisim
import time

print("Weak Bisimulation Test")
print("===================\nTeleportation")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete1-1.txt", "parse_output/concrete1-1.gv",
          "examples/weak_concrete1-2.txt", "parse_output/weak_concrete1-2.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/concrete2-1.txt", "parse_output/concrete2-1.gv",
#           "examples/concrete2-2.txt", "parse_output/concrete2-2.gv")
# print("pLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
print("===================\nSDC")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete3-1.txt", "parse_output/concrete3-1.gv",
          "examples/weak_concrete3-2.txt", "parse_output/weak_concrete3-2.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
qlts_timer = time.time()
bisim.init_qLTS("examples/weak_concrete3-1-m.txt", "parse_output/weak_concrete3-1-m.gv",
          "examples/weak_concrete3-2-m.txt", "parse_output/weak_concrete3-2-m.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
print("===================\nSecret Sharing")
qlts_timer = time.time()
bisim.init_qLTS("examples/concrete4-1.txt", "parse_output/concrete4-1.gv",
          "examples/weak_concrete4-2.txt", "parse_output/weak_concrete4-2.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
print("===================\nBB84")
qlts_timer = time.time()
bisim.init_qLTS("examples/concreteBB84.txt", "parse_output/concreteBB84.gv",
          "examples/weak_concreteBB84-spec.txt", "parse_output/weak_concreteBB84-spec.gv")
print("pLTS Generate in ", time.time() - qlts_timer)
bisim.Weak_Bisimulation(0,0)
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