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
