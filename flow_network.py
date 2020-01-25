# -*- coding: utf-8 -*-
import graphviz
import copy
from graphviz import Digraph
import scipy as sp
import scipy.optimize as opt
import numpy as np 
import re
import pprint as pp

# @param remain_edges         Remaining edges not used.
# @param visited_vertexes     Set of vertexes visited.
# @param visited_distrs       Set of vertexes distributions visited.
# @param s                    Start point(not only source point).
# @param t                    Sink point.
# @param action               Given action.
# @param path                 Transitions of allowed paths.
# @param temp_path            Transitions not sure if they are in the allowed paths.
# @param flag                 Flag for before/after the given action: 0-before, 1-after.
# 
# Use DFS to find all the weak transitions in the transition system of the given action.
# 
# @return A set of allowed transitions.
# 
def allow_path(remain_edges,visited_vertexes,s,t,action,path,temp_path,flag):
      visited_vertexes.append(s)
      exist = False
      transitions = [tr for tr in remain_edges if tr[0] == s]
      if (len(transitions) == 0) & (flag == 1):
            return True
      if action != "tau":
            for transition in transitions:
                  for tr in path:
                        if (transition[0]==tr[0]) & (transition[1]==tr[1]):
                              path.append(transition)
                              break
                  for tr in temp_path:
                        if (transition[0]==tr[0]) & (transition[1]==tr[1]):
                              temp_path.append(transition)
                              break
                  if transition[1] in visited_vertexes:
                        temp_path.append(transition)
                  elif (transition[2] == action) & (flag == 0):
                        next_path = []
                        next_path.append(transition)
                        remain_edges.remove(transition)
                        res = allow_path(remain_edges,visited_vertexes,transition[1],t,action,next_path,temp_path,1)
                        if(res):
                              path.extend(next_path)
                        exist = exist or res
                  elif (transition[2] == "tau") & (flag == 0):
                        next_path = []
                        next_path.append(transition)
                        remain_edges.remove(transition)
                        res = allow_path(remain_edges,visited_vertexes,transition[1],t,action,next_path,temp_path,flag)
                        if(res):
                              path.extend(next_path)
                        exist = exist or res
                  elif (transition[2] == "tau") & (flag == 1):
                        next_path = []
                        next_path.append(transition)
                        remain_edges.remove(transition)
                        res = allow_path(remain_edges,visited_vertexes,transition[1],t,action,next_path,temp_path,flag)
                        if (res):
                              path.extend(next_path)
                        exist = exist or res
                  elif (transition[2] != "tau") & (flag == 1):
                        exist = True
      elif action == "tau":
            for transition in transitions:
                  for tr in path:
                        if (transition[0]==tr[0]) & (transition[1]==tr[1]):
                              path.append(transition)
                              break
                  for tr in temp_path:
                        if (transition[0]==tr[0]) & (transition[1]==tr[1]):
                              temp_path.append(transition)
                              break
                  if (transition[1] in visited_vertexes):
                        temp_path.append(transition)
                  elif (transition[2] == action):
                        next_path = []
                        next_path.append(transition)
                        remain_edges.remove(transition)
                        res = allow_path(remain_edges,visited_vertexes,transition[1],t,action,next_path,temp_path,1)
                        if (res):
                              path.extend(next_path)
                        exist = exist or res
                  elif (transition[2] != action):
                        exist = True
      if exist:
            path_loop = [tr for tr in temp_path if tr[1] == s]
            path.extend(path_loop)
      return exist

# 
# Append transitions and corresponding vertexes if they are not contained in the list.
# 
def add_transition(edges,vertexes,transition):
      if transition not in edges:
            edges.append(transition)
      if transition[0] not in vertexes:
            vertexes.append(transition[0])
      if transition[1] not in vertexes:
            vertexes.append(transition[1])

# @param transitions           Allowed transitions.
# @param equivalence           Equivalence relation of the vertexes.
# @param action                The given action to conduct.
# @param s                     The start vertex (the source vertex could be -1).
# @param t                     The sink vertex (should be the number of vertexes plus 1).
# 
# Construct the flow network transitions by given allowed path.
# 
# @return A set of network edges.
#
def constr_trans(transitions,equivalence,action,s,t):
      if action != "tau":
            return constr_trans_a(transitions,equivalence,s,t)
      elif action == "tau":
            return constr_trans_tau(transitions,equivalence,s,t)

def constr_trans_a(transitions,equivalence,s,t):
      network_edges = [('-1',str(s)),(str(s)+"_a",str(s)+"_bot")]
      network_vertexes = ['-1',str(s),str(s)+"_a",str(s)+"_bot"]
      rho = {}
      equivalence_member = set([r for (l,r) in equivalence])
      if s in equivalence_member:
            equivalence_class = [l for (l,r) in equivalence if r == s]
            for corresponding_vertex in equivalence_class:
                  bottom_vertex = str(s)+"_bot"
                  corresponding_vertex = str(corresponding_vertex)+"_R"
                  add_transition(network_edges,network_vertexes,(bottom_vertex,corresponding_vertex))
                  if (corresponding_vertex,t) not in network_edges:
                        add_transition(network_edges,network_vertexes,(corresponding_vertex,str(t)))
      count = 0
      for transition in transitions:
            prob = transition[3]
            # transition index
            trans = str(count)
            if prob < 1:
                  s = len(transition)
                  if len(transition) != 5:
                        Warning("A distribution required.")
                  else:
                        distr_name = transition[4]
                        if distr_name not in rho.keys():
                              rho[distr_name] = count
                              count += 1
                        trans = str(rho[distr_name])
            elif prob > 1:
                  Warning("The probability of the transition is abnormal.")
            else:
                  count += 1
            if transition[2] == "tau":
                  # L1
                  inter_vertex = str(transition[0])+"_tr"+trans
                  add_transition(network_edges,network_vertexes,(str(transition[0]),inter_vertex))
                  add_transition(network_edges,network_vertexes,(inter_vertex,str(transition[1]),str(prob)))
                  # L2
                  origin_vertex = str(transition[0])+"_a"
                  inter_vertex = str(transition[0])+"_atr"+trans
                  target_vertex = str(transition[1])+"_a"
                  bottom_vertex = str(transition[1])+"_bot"
                  add_transition(network_edges,network_vertexes,(origin_vertex,inter_vertex))
                  add_transition(network_edges,network_vertexes,(inter_vertex,target_vertex,str(prob)))
                  add_transition(network_edges,network_vertexes,(target_vertex,bottom_vertex))
            elif transition[2] != "tau":
                  # La
                  inter_vertex = str(transition[0])+"_atr"+trans
                  target_vertex = str(transition[1])+"_a"
                  bottom_vertex = str(transition[1])+"_bot"
                  add_transition(network_edges,network_vertexes,(str(transition[0]),inter_vertex))
                  add_transition(network_edges,network_vertexes,(inter_vertex,target_vertex,str(prob)))
                  add_transition(network_edges,network_vertexes,(target_vertex,bottom_vertex))
            if transition[1] in equivalence_member:
                  equivalence_class = [l for (l,r) in equivalence if r == transition[1]]
                  for corresponding_vertex in equivalence_class:
                        bottom_vertex = str(transition[1])+"_bot"
                        corresponding_vertex = str(corresponding_vertex)+"_R"
                        add_transition(network_edges,network_vertexes,(bottom_vertex,corresponding_vertex))
                        if (corresponding_vertex,t) not in network_edges:
                              add_transition(network_edges,network_vertexes,(corresponding_vertex,str(t)))
      return (network_edges,network_vertexes)

def constr_trans_tau(transitions,equivalence,s,t):
      network_edges = [('-1',str(s)),(str(s),str(s)+"_bot")]
      network_vertexes = ['-1',str(s),str(s)+"_bot"]
      rho = {}
      equivalence_member = set([r for (l,r) in equivalence])
      if s in equivalence_member:
            equivalence_class = [l for (l,r) in equivalence if r == s]
            for corresponding_vertex in equivalence_class:
                  bottom_vertex = str(s)+"_bot"
                  corresponding_vertex = str(corresponding_vertex)+"_R"
                  add_transition(network_edges,network_vertexes,(bottom_vertex,corresponding_vertex))
                  if (corresponding_vertex,t) not in network_edges:
                        add_transition(network_edges,network_vertexes,(corresponding_vertex,str(t)))
      count = 0
      for transition in transitions:
            prob = transition[3]
            # transition index
            trans = str(count)
            if prob < 1:
                  s = len(transition)
                  if len(transition) != 5:
                        Warning("A distribution required.")
                  else:
                        distr_name = transition[4]
                        if distr_name not in rho.keys():
                              rho[distr_name] = count
                              count += 1
                        trans = str(rho[distr_name])
            elif prob > 1:
                  Warning("The probability of the transition is abnormal.")
            else:
                  count += 1
            # L1
            inter_vertex = str(transition[0])+"_tr"+trans
            add_transition(network_edges,network_vertexes,(str(transition[0]),inter_vertex))
            add_transition(network_edges,network_vertexes,(inter_vertex,str(transition[1]),str(prob)))
            # L_bot
            bottom_vertex = str(transition[1])+"_bot"
            add_transition(network_edges,network_vertexes,(str(transition[1]),bottom_vertex))
            if transition[1] in equivalence_member:
                  equivalence_class = [l for (l,r) in equivalence if r == transition[1]]
                  for corresponding_vertex in equivalence_class:
                        bottom_vertex = str(transition[1])+"_bot"
                        corresponding_vertex = str(corresponding_vertex)+"_R"
                        add_transition(network_edges,network_vertexes,(bottom_vertex,corresponding_vertex))
                        if (corresponding_vertex,t) not in network_edges:
                              add_transition(network_edges,network_vertexes,(corresponding_vertex,str(t)))
      return (network_edges,network_vertexes)

# 
# Check the condition through solving a linear programming problem.
# 
def solve_lp(network_edges,network_vertexes,distribution,s,t,n_e,n_v):
      vNum = len(network_vertexes)
      eNum = len(network_edges)
      # c
      c = np.array([1]*eNum)
      # b
      condition = 0
      index_source = 0
      new_row = np.zeros((1,eNum))
      A = np.zeros((1,eNum))
      A[condition][index_source] = 1
      b = np.array([1])
      condition = condition + 1
      for v in network_vertexes:
            if re.match(r'(.*)_R$',v) is not None:
                  A = np.vstack((A,new_row))
                  index_sink = network_edges.index((str(v),str(t)))
                  A[condition][index_sink] = 1
                  distr_prob = 0
                  for ele in distribution:
                        if (str(ele[0])+"_R") == v:
                              distr_prob = distr_prob + ele[1]
                  b = np.hstack((b,np.array([distr_prob])))
                  condition = condition + 1
      # print("First step：" + str(condition) + " conditions.")
      # A
      # flow conservation
      for v in network_vertexes:
            if (v == '-1') or (v == str(t)):
                  continue
            A = np.vstack((A,new_row))
            edge_end_v = [tr for tr in network_edges if tr[1]==v]
            edge_start_v = [tr for tr in network_edges if tr[0]==v]
            for e in edge_end_v:
                  index_input = network_edges.index(e)
                  A[condition][index_input] = 1
            for e in edge_start_v:
                  index_output = network_edges.index(e)
                  A[condition][index_output] = -1
            b = np.hstack((b,np.array([0])))
            condition = condition + 1
      # print("Second step：" + str(condition) + " conditions.")
      # balancing factor
      for v in network_vertexes:
            if (re.match(r'(.*)_tr(\d*)$',v) is not None) | (re.match(r'(.*)_atr(\d*)$',v) is not None):
                  edge_end_v = None
                  for t in network_edges:
                        if t[1]==v:
                               edge_end_v = t
                  if edge_end_v is None:
                        break
                  edge_start_v = [tr for tr in network_edges if tr[0]==v]
                  index_input = network_edges.index(edge_end_v)
                  for e in edge_start_v:
                        A = np.vstack((A,new_row))
                        index_output = network_edges.index(e)
                        prob = float(e[2])
                        A[condition][index_input] = -1*prob
                        A[condition][index_output] = 1
                        b = np.hstack((b,np.array([0])))
                        condition = condition + 1
      # print("Third step：" + str(condition) + " conditions.")
      # bounds
      f_bound = (0,None)
      bounds = (f_bound,)*eNum
      # linear programming
      res = opt.linprog(c,A_eq=A,b_eq=b,bounds=bounds,options={'disp':False})
      return res

# @param graph        Transition system.
# @param edges        Set of edges in the graph.
# @param vertexes     Set of vertexes in the graph.
# @param action       Given action.
# @param vnum         Number of vertexes.
# 
# Construct the flow network for the given action.
# 
# @return A flow network constructed by all the allow weak transitions.
# 
# def constr_network(edges,vertexes,action,equiv,vnum):
#       # Source and sink
#       s = 0
#       t = vnum

#       # Edges(=transitions here) and vertexes(=snapshots here) set of the network
#       network = []
#       network_trans = []
#       network_snapshot = []
#       remain_edges = copy.deepcopy(edges)
#       remian_vertexes = copy.deepcopy(vertexes)

#       # Main: Construct the flow network
#       path = []
#       if allow_path(remain_edges,[],s,t,action,path,[],0):
#             print(path)
#       print("\n")

#       flow_network = constr_trans(path,equiv,"tau",s,t)
#       print("Flow network: ")
#       pp.pprint(flow_network)
#       e = flow_network[0]
#       v = flow_network[1]

#       # Print network
#       dot = Digraph(comment = "The Flow Network")
#       dot.attr('node', fontsize='35')
#       dot.attr('edge', fontsize='40')
#       for transition in e:
#             if len(transition)>2:
#                   dot.edge(str(transition[0]),str(transition[1]),str(transition[2]))
#             else:
#                   dot.edge(str(transition[0]),str(transition[1]))
#       dot.render("networkflow_temp_output.gv",view=False)
#       network.append(e, v)
#       return network
