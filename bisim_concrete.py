# -*- coding: utf-8 -*-
# import sys
# print(sys.path)
import qlts_concrete as qlts
from qlts_concrete import tt, ff, tau
from z3 import And, Or, simplify, BoolRef
import pprint as pp
import numpy as np
# import sympy as sp
import flow_network as fn
import gc
import time
import copy


def reset_qlts():
    qlts.op = {}
    qlts.meas = {}
    qlts.qLTS = []
    qlts.transitions = []
    qlts.snapshots = []
    qlts.initial_state = {}
    qlts.transition = []
    qlts.snapshot = []
    qlts.regx = []
    qlts.regq = []
    qlts.regx_val = {}
    qlts.regq_val = []
    qlts.mat_size = 0
    qlts.state = 0
    qlts.statement = ""


# Input information
in_1 = ''
out_1 = ''
qlts_1 = []
op_1 = {}
transitions_1 = []
snapshot_1 = []
initial_state_1 = {}
regx_1 = []
regq_1 = []
regx_val_1 = {}
regq_val_1 = []
mat_size = 0
state_1 = 0
statement_1 = ""
in_2 = ''
out_2 = ''
qlts_2 = []
op_2 = {}
transitions_2 = []
snapshot_2 = []
initial_state_2 = {}
regx_2 = []
regq_2 = []
regx_val_2 = {}
regq_val_2 = []
mat_size = 0
state_2 = 0
statement_2 = ""

# Auxiliary variable
timer = time.time()
comm_actions = ['!', '.!', '?', '.?']
invisible_actions = ['measurement', 'operation', 'matched', 'silent']
epsilon = 0.1
accuracy = 2

# Tables for record the status of the state pairs
NonBisim = []
Bisim = []
Assumed = []

# If the assumption is wrong, do the Bis() again with updated NonBisim and Bisim sets
class WrongAssumptionError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class DifferentDepthException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def Bisimulation(t, u):
    global timer, NonBisim, Bisim
    timer = time.time()
    NonBisim = []
    res = False
    # print("//Check Bisimulation\nStart: ")
    try:
        res = Bis(t, u)
    except WrongAssumptionError as e:
        print(e)
        res = Bis(t, u)
    except DifferentDepthException as e:
        print(e)
    finally:
        # print("//Check Bisimulation\nResult: ", res[0])
        if len(NonBisim) > 10:
            print("NonBisim: ", len(NonBisim))
        else:
            print("NonBisim: ", NonBisim)
        if len(Bisim) > 10:
            print("Bisim: ", len(Bisim))
        else:
            print("Bisim: ", Bisim)
        if res == False:
            print("Not Bisimilar")
        else:
            print("Bisimilar")
        cost_time = time.time() - timer
        print(cost_time)
    return res


def Bis(t, u):
    global Bisim, Assumed
    Visited = []
    Bisim = []
    Assumed = []
    return Match(t, u, Visited)


def Match(t, u, Visited):
    global NonBisim, Bisim, Assumed
    # print("Match Snapshot: ", end='')
    # print(t,u)
    b = True
    delta = {}
    theta = {}
    alpha_set = get_act(t, u)
    # print("Alpha : ",alpha_set)
    if alpha_set is None:
        NonBisim.append((t, u))
        return False
    for alpha in alpha_set:
        match_action_res = MatchAction(alpha, t, u, Visited)
        b = And(b, match_action_res)
    # Theta result
    # Quantum variable equality qv(t)==qv(u)
    b_qveq = (set(regq_1).issubset(set(regq_2))
              or set(regq_2).issubset(set(regq_1)))
    # Density operator equality E==F
    sn_t = snapshot_1[t]
    sn_u = snapshot_2[u]
    dens_t = sn_t['density operator']
    dens_u = sn_u['density operator']
    b_supereq = superoperator_equivalence(dens_t, dens_u)
    b_cond = And(b_qveq, b_supereq)
    # print("---------------------Conditions: ",b_cond)
    b = simplify(And(b, b_cond))
    # NonBisim result
    if b == False:
        NonBisim.append((t, u))
        if (t, u) in Assumed:
            raise WrongAssumptionError('This Assumption is wrong.')
    elif b == True:
        Bisim.append((t, u))
    else:
        print("Problem exists on the boolean value theta.")
    # print("Match ",(t,u)," result")
    # print("======================= (1)boolean: ",b)
    # print("======================= (1)boolean: ",b_qveq)
    # print("======================= (1)boolean: ",b_supereq)
    # if len(NonBisim) < 10:
    # 	print("======================= (2)Table NonBisim: ",NonBisim)
    # else:
    # 	print("======================= (2)Table Nonbisim: ",len(NonBisim)," items")
    # if len(Bisim) < 10:
    # 	print("======================= (3)Table Bisim: ",Bisim)
    # else:
    # 	print("======================= (3)Table: Bisim",len(Bisim)," items")
    return b


def MatchAction(alpha, t, u, Visited):
    global NonBisim, Bisim
    # print("Match Action: ", end='')
    # print(alpha,t,u)
    b_list = []
    b_list_ = []
    b_conjunction = None
    pair = (t, u)
    if pair not in Visited:
        Visited.append(pair)
    if alpha == "silent":
        trans_t_list = [transition for transition in transitions_1 if transition[0] == t and (
            transition[3] == 'silent' or transition[3] == 'measurement' or transition[3] == 'operation')]
        trans_u_list = [transition for transition in transitions_2 if transition[0] == u and (
            transition[3] == 'silent' or transition[3] == 'measurement' or transition[3] == 'operation')]
        b = np.ones((len(trans_t_list), len(trans_u_list)), dtype=BoolRef)
        for i in range(len(trans_t_list)):
            trans_t = trans_t_list[i]
            for j in range(len(trans_u_list)):
                trans_u = trans_u_list[j]
                matchdistribution_res = ()
                matchdistribution_res = MatchDistribution(
                    trans_t[1], trans_u[1], Visited)
                b[i, j] = matchdistribution_res
        for i in range(len(trans_t_list)):
            b_disjunction = None
            for j in range(len(trans_u_list)):
                if b_disjunction == None:
                    b_disjunction = bool(b[i, j])
                else:
                    b_disjunction = Or(b_disjunction, bool(b[i, j]))
            if b_conjunction is None:
                b_conjunction = b_disjunction
            else:
                b_conjunction = And(b_conjunction, b_disjunction)
        for j in range(len(trans_u_list)):
            b_disjunction = None
            for i in range(len(trans_t_list)):
                if b_disjunction == None:
                    b_disjunction = bool(b[i, j])
                else:
                    b_disjunction = Or(b_disjunction, bool(b[i, j]))
            if b_conjunction is None:
                b_conjunction = b_disjunction
            else:
                b_conjunction = And(b_conjunction, b_disjunction)
    else:
        trans_t_list = []
        trans_u_list = []
        # Cooperate with the code in MatchAction() to avoid the matching cause the by silent actions
        # which indeed is caused by communications
        if alpha == 'matched':
            trans_t_list = [transition for transition in transitions_1 if transition[0] == t and (
                transition[3] == 'silent' or transition[3] == 'matched')]
            trans_u_list = [transition for transition in transitions_2 if transition[0] == u and (
                transition[3] == 'silent' or transition[3] == 'matched')]
        else:
            trans_t_list = [transition for transition in transitions_1 if transition[0] == t and (
                transition[3] != 'silent' and transition[3] != 'matched')]
            trans_u_list = [transition for transition in transitions_2 if transition[0] == u and (
                transition[3] != 'silent' and transition[3] != 'matched')]
        b = np.ones((len(trans_t_list), len(trans_u_list)), dtype=BoolRef)
        for i in range(len(trans_t_list)):
            trans_t = trans_t_list[i]
            for j in range(len(trans_u_list)):
                trans_u = trans_u_list[j]
                match_res = ()
                match_res = Match(trans_t[1], trans_u[1], Visited)
                b[i, j] = match_res
                if alpha == "!" or alpha == ".!":
                    # 动作为Output时的特殊情况，保存输出变量
                    e_1 = ''
                    e_2 = ''
                    (e_1, e_2) = output_parallel_variables(trans_t, trans_u)
                    b_new = (e_1 == e_2)
                    if b_new == False:
                        b[i, j] = False
        for i in range(len(trans_t_list)):
            b_disjunction = None
            for j in range(len(trans_u_list)):
                if b_disjunction == None:
                    b_disjunction = bool(b[i, j])
                else:
                    b_disjunction = Or(b_disjunction, bool(b[i, j]))
            if b_conjunction is None:
                b_conjunction = b_disjunction
            else:
                b_conjunction = And(b_conjunction, b_disjunction)
        for j in range(len(trans_u_list)):
            b_disjunction = None
            for i in range(len(trans_t_list)):
                if b_disjunction == None:
                    b_disjunction = bool(b[i, j])
                else:
                    b_disjunction = Or(b_disjunction, bool(b[i, j]))
            if b_conjunction is None:
                b_conjunction = b_disjunction
            else:
                b_conjunction = And(b_conjunction, b_disjunction)
    # print(b_conjunction)
    if b_conjunction == None:
        print("Model Error, no next transition in the qLTS.")
        return
    b_res = simplify(b_conjunction)
    # print("Match ",(t,u)," action result")
    # print("============================= (1)boolean: ",b_res)
    # if len(N) < 10:
    # 	print("============================= (2)Table N: ",N)
    # else:
    # 	print("============================= (2)Table N: ",len(N)," items")
    # if len(B) < 10:
    # 	print("============================= (2)Table B: ",B)
    # else:
    # 	print("============================= (2)Table B: ",len(B)," items")
    return b_res


def MatchDistribution(t, u, Visited):
    global NonBisim, Bisim
    # print("Match Distribution.")
    # print(t,u)
    b = None
    # 构造分布
    delta = {}
    theta = {}
    distr_elements = []
    candidate = []
    for transition in transitions_1:
        for another_transition in transitions_2:
            if transition[0] == t and another_transition[0] == u:
                t_ = transition[1]
                u_ = another_transition[1]
                if transition[2] == "tau":
                    t_prob = 1
                else:
                    t_prob = transition[2]
                if another_transition[2] == "tau":
                    u_prob = 1
                else:
                    u_prob = another_transition[2]
                delta.update({(t_, 't'): t_prob})
                theta.update({(u_, 'u'): u_prob})
                if (t_, 't') not in distr_elements:
                    distr_elements.append((t_, 't'))
                if (u_, 'u') not in distr_elements:
                    distr_elements.append((u_, 'u'))
                match_res = ()
                match_res = Match(t_, u_, Visited)
                candidate.append((t_, u_))
                # print(match_res,T_union)
                # print("Distribution b: ",match_res[0])
                if b is None:
                    b = match_res
                else:
                    b = Or(b, match_res)
    # Prepare the generation of equivalence relations, mark the elements in N with its owner qLTS
    T_disjoint_union = Close(candidate, Visited)
    # Build equivalence relation
    R = equivalence_relation(T_disjoint_union)
    # print(distr_elements,T_union,delta,theta,R)
    b_res = Check(distr_elements, T_disjoint_union, delta, theta, R)
    if b is not None:
        b_res = simplify(And(b, b_res))
    # print("Match ",(t,u)," distribution result")
    # print("============================= (1)boolean: ",b_res)
    # if len(N) < 10:
    # 	print("============================= (2)Table N: ",N)
    # else:
    # 	print("============================= (2)Table N: ",len(N)," items")
    # if len(B) < 10:
    # 	print("============================= (2)Table B: ",B)
    # else:
    # 	print("============================= (2)Table B: ",len(B)," items")
    return b_res


def Close(pairs, Visited):
    global NonBisim, Bisim, Assumed
    disjoint_union = []
    for pair in pairs:
        if pair in NonBisim:
            continue
        elif pair in Bisim:
            if ((pair[0], 't'), (pair[1], 'u')) not in disjoint_union:
                disjoint_union.append(((pair[0], 't'), (pair[1], 'u')))
        elif pair in Visited:
            if (pair[0], pair[1]) not in Assumed:
                Assumed.append((pair[0], pair[1]))
        else:
            res = Match(pair[0], pair[1], Visited)
            if res == True:
                if ((pair[0], 't'), (pair[1], 'u')) not in disjoint_union:
                    disjoint_union.append(((pair[0], 't'), (pair[1], 'u')))
    return disjoint_union


def Check(distr_elements, T_disjoint_union, delta, theta, R):
    # print("Check.")
    # print("Distribution elements: ",distr_elements)
    # print("Disjoint Unions: ",T_disjoint_union)
    # pp.pprint(delta)
    # pp.pprint(theta)
    b = True
    equivalence_classes = []
    if len(T_disjoint_union) == 0:
        # print("Warning: No pair in distribution matched.")
        b = False
        # Compute equivalence class
    for s in distr_elements:
        # pp.pprint(s)
        equivalence_class = set()
        for relation in R:
            if relation[0] == s:
                equivalence_class.add(relation[1])
        if not ((equivalence_class in equivalence_classes) or (equivalence_class == set())):
            equivalence_classes.append(equivalence_class)
        # if len(equivalence_classes) < 5:
        # 	print("Equivalence classes: ",equivalence_classes)
        # else:
        # 	print("Equivalence classes: ",len(equivalence_classes)," items")
    for equivalence_class in equivalence_classes:
        # pp.pprint(equivalence_class)
        # Check equivalence class
        # Distinguish the owner qLTS from the mark
        m_t = 0.0
        m_u = 0.0
        for ele in equivalence_class:
            if ele[1] == 't':
                if ele in delta:
                    m_t = m_t + delta[ele]
            if ele[1] == 'u':
                if ele in theta:
                    m_u = m_u + theta[ele]
        m_t = np.around(m_t, decimals=2)
        m_u = np.around(m_u, decimals=2)
        if not m_t == m_u:
            b = False
        # 	print("======",m_t,m_u)
        # print("Check result: ",b)
    return b

# Compute the equivalence relation


def equivalence_relation(T_union):
    T = set(T_union)
    R = set()
    R = R | T
    # print(R)
    for tup in T:
        R.add(tup[::-1])
    # print(R)
    T = R | T
    for (a, b) in T:
        for (c, d) in T:
            if b == c and ((a, d) not in T):
                R.add((a, d))
    # print(R)
    return R


def get_act(t, u):
    global timer
    gammas = set()
    # TODO: Optimize later, use t_count and u_count directly (Not test yet)
    t_count = [transition for transition in transitions_1 if transition[0] == t]
    u_count = [transition for transition in transitions_2 if transition[0] == u]
    # print(t_count,u_count)
    if (len(t_count) == 0 and len(u_count) != 0) or (len(t_count) != 0 and len(u_count) == 0):
        cost_time = time.time() - timer
        print(cost_time)
        raise DifferentDepthException("Different Depth. Not Bisimilar.")
    for transition in transitions_1:
        for another_transition in transitions_2:
            # Cooperate with the code in MatchAction() to avoid the matching cause the by silent actions
            # which indeed is caused by communications
            if transition[0] == t and another_transition[0] == u:
                if (transition[3] in invisible_actions) and (another_transition[3] in invisible_actions):
                    if (transition[3] == 'matched' or transition[3] == 'silent') and (another_transition[3] == 'matched' or another_transition[3] == 'silent'):
                        gammas.add('matched')
                    else:
                        gammas.add('silent')
                elif transition[3] == another_transition[3]:
                    if (transition[3] == '!' and another_transition[3] == '!') or (transition[3] == '?' and another_transition[3] == '?') or (transition[3] == '.!' and another_transition[3] == '.!') or (transition[3] == '.?' and another_transition[3] == '.?'):
                        (c1, c2) = parallel_channel(
                            transition, another_transition)
                        if c1 == c2:
                            gammas.add(transition[3])
                    else:
                        gammas.add(transition[3])
    if (len(t_count) > 0 and len(u_count) > 0 and len(gammas) == 0):
        # print("No pair of actions in the next step are the same. Not Bisimilar.")
        return None
    return gammas


def superoperator_equivalence(E, F):
    # print(E)
    # print(F)
    b = True
    dem = mat_size
    E_trace = 0
    F_trace = 0
    for i in range(dem):
        E_trace = E_trace+E[i, i]
        F_trace = F_trace+F[i, i]
    E_trace = np.around(E_trace, decimals=accuracy)
    F_trace = np.around(F_trace, decimals=accuracy)
    # print("Trace of E:",E_trace)
    # print("Trace of F:",F_trace)
    if not ((E_trace < (F_trace + epsilon**accuracy)) & (E_trace > (F_trace - epsilon**accuracy))):
        b = False
    # print("Equivalence result:",b)
    return b


def superoperator_distribution_equivalence(lst):
    # print(lst)
    superoperator_size = mat_size**2
    E = np.zeros([superoperator_size, superoperator_size])
    F = np.zeros([superoperator_size, superoperator_size])
    t_list = []
    u_list = []
    for pair in lst:
        t_distribution = pair[0]
        u_distribution = pair[1]
        E0 = snapshot_1[t_distribution]['density operator']
        F0 = snapshot_2[u_distribution]['density operator']
        for transition in transitions_1:
            for another_transition in transitions_2:
                if transition[0] == t_distribution and another_transition[0] == u_distribution:
                    t_ = transition[1]
                    u_ = another_transition[1]
                    if t_ not in t_list:
                        E = E + snapshot_1[t_]['density operator']
                        t_list.append(t_)
                    if u_ not in u_list:
                        F = F + snapshot_2[u_]['density operator']
                        u_list.append(u_)
    if superoperator_equivalence(E, F) == True:
        matched_list = []
        for t_ in t_list:
            for u_ in u_list:
                matched_list.append((t_, u_))
        # print(matched_list)
        return matched_list
    return []


def output_parallel_variables(trans_t, trans_u):
    action_t = trans_t[2]
    action_u = trans_u[2]
    # variable_t = ''
    # variable_u = ''
    # for i in range(len(action_t)):
    #	if action_t[i] == '!' or action_t[i:i+1] == '.!':
    #		variable_t = action_t[i+1:len(action_t)]
    # for i in range(len(action_u)):
    #	if action_u[i] == '!' or action_u[i:i+1] == '.!':
    #		variable_u = action_u[i+1:len(action_u)]
    # print(variable_t,variable_u)
    # return (variable_t,variable_u)
    return (action_t, action_u)


# Check if there is the same channel used
def parallel_channel(trans_t, trans_u):
    action_t = trans_t[2]
    action_u = trans_u[2]
    a_t = trans_t[3]
    a_u = trans_u[3]
    for i in range(len(action_t)):
        if action_t[i] == a_t or action_t[i:i+1] == a_t:
            channel_t = action_t[0:i]
    for i in range(len(action_u)):
        if action_u[i] == a_u or action_u[i:i+1] == a_u:
            channel_u = action_u[0:i]
    # print(channel_t,channel_u)
    return (channel_t, channel_u)


def Weak_Bisimulation(t, u):
    global timer, NonBisim, Bisim
    timer = time.time()
    NonBisim = []
    res = False
    # print("//Check Bisimulation\nStart: ")
    try:
        res = Bis_Weak(t, u)
    except WrongAssumptionError as e:
        print(e)
        res = Bis_Weak(t, u)
    finally:
        # print("//Check Bisimulation\nResult: ", res)
        if len(NonBisim) > 10:
            print("NonBisim: ", len(NonBisim))
        else:
            print("NonBisim: ", NonBisim)
        if len(Bisim) > 10:
            print("Bisim: ", len(Bisim))
        else:
            print("Bisim: ", Bisim)
        if res == False:
            print("Not Weak Bisimilar")
        else:
            print("Weak Bisimilar")
        cost_time = time.time() - timer
        print(cost_time)
    return res


def Bis_Weak(t, u):
    global Bisim, Assumed
    Visited = []
    Bisim = []
    Assumed = []
    return Match_Weak(t, u, Visited)


def Match_Weak(t, u, Visited):
    global NonBisim, Bisim, Assumed
    # print("Match Weak.", end='')
    # print(t, u)
    b = True
    delta = {}
    theta = {}
    # Visited = Visited U {(t, u)}
    pair = (t, u)
    if pair not in Visited:
        Visited.append(pair)
    next_actions = get_weak_act(t, u)
    # print("Alpha : ", next_actions)
    # First direction: for each t --a-> t', find u ==a=> u'
    for next_action in next_actions[0]:
        match_action_res = MatchAction_Weak(next_action, t, u, Visited)
        b = And(b, match_action_res)
    # Second direction: for each u --a-> u', find t ==a=> t'
    for next_action in next_actions[1]:
        match_action_res = MatchAction_Weak_Reverse(next_action, u, t, Visited)
        b = And(b, match_action_res)
    # Theta result
    # Quantum variable equality qv(t)==qv(u)
    b_qveq = (set(regq_1).issubset(set(regq_2))
              or set(regq_2).issubset(set(regq_1)))
    # Density operator equality E==F
    sn_t = snapshot_1[t]
    sn_u = snapshot_2[u]
    dens_t = sn_t['density operator']
    dens_u = sn_u['density operator']
    b_supereq = superoperator_equivalence(dens_t, dens_u)
    b_cond = And(b_qveq, b_supereq)
    # print("---------------------Conditions: ", b_cond)
    b = simplify(And(b, b_cond))
    # NonBisim result
    if b == False:
        NonBisim.append((t, u))
        if (t, u) in Assumed:
            raise WrongAssumptionError(
                "This assumption in weak bisimulation checking is wrong.")
    elif b == True:
        Bisim.append((t, u))
    else:
        print("Problem exists on the boolean value theta.") 
    # print("Match ",(t,u)," result")
    # print("======================= (1)boolean: ",b)
    # print("======================= (1)boolean: ",b_qveq)
    # print("======================= (1)boolean: ",b_supereq)
    # if len(N) < 10:
    #     print("======================= (2)Table: ", N)
    # else:
    #     print("======================= (2)Table: ", len(N), " items")
    # if len(B) < 10:
    #     print("======================= (2)Table: ", B)
    # else:
    #     print("======================= (2)Table: ", len(B), " items")
    return b


def MatchAction_Weak(alpha, t, u, Visited):
    global NonBisim, Bisim
    # print("Match Action Weak.")
    # print(alpha, t, u)
    theta = []
    b_res = None
    if alpha in invisible_actions:
        # Check the step condition
        # for each t -> t', find u => u'
        trans_t_list = [tr for tr in transitions_1 if (
            tr[0] == t) & (tr[3] in invisible_actions)]
        for transition in trans_t_list:
            allow_transitions = []
            allow_snapshots = []
            # Construct the graph of allow transitions G
            remain_edges = copy.deepcopy(transitions_2)
            remain_vertexes = copy.deepcopy(snapshot_2)
            res = constr_graph(remain_edges, [], u, len(
                remain_vertexes), "tau", allow_transitions, allow_snapshots, [], 0, 0)
            if not res:
                theta.append(False)
                break
            if (transition[3] == "measurement") | (transition[3] == "operation"):
                # Distribution rho, rho = t'
                rho = []
                pairs = []
                trans_distribution = [
                    tr for tr in transitions_1 if tr[0] == transition[1]]
                for distr_member in trans_distribution:
                    t_ = distr_member[1]
                    t_prob = 0
                    if distr_member[2] == "tau":
                        t_prob = 1
                    else:
                        t_prob = distr_member[2]
                    rho.append((t_, t_prob))
                    # Collect the pairs (t', u') for further matching
                    # The empty transition can make system stay at t so that u' = u
                    pairs.append((distr_member[1], u))
                    # Other states u'_i
                    for trans_u in allow_transitions:
                        pairs.append((distr_member[1], trans_u[1]))
            elif (transition[3] == "matched") | (transition[3] == "silent"):
                # Next snapshot t' (one point distribution _t')
                rho = [(transition[1], 1)]
                # The empty transition can make system stay at t so that u' = u
                pairs = [(transition[1], u)]
                # Other states u'_i
                for trans_u in allow_transitions:
                    pairs.append((transition[1], trans_u[1]))
            # Build equivalence relation
            disjoint_union = Close_Weak(pairs, Visited)
            R = disjoint_union
            # LP(G,rho,u,alpha,R)
            solution = SolveLP(allow_transitions, allow_snapshots,
                               rho, u, len(snapshot_2), "tau", R)
            # Result is kept as theta_i
            theta.append(solution)
    elif alpha in comm_actions:
        # Check the step condition
        # for each t -> t', find u => u'
        trans_t_list = [tr for tr in transitions_1 if (
            tr[0] == t) & (tr[3] not in invisible_actions)]
        for transition in trans_t_list:
            allow_transitions = []
            allow_snapshots = []
            # Construct the graph of allow transitions G
            remain_edges = copy.deepcopy(transitions_2)
            remain_vertexes = copy.deepcopy(snapshot_2)
            res = constr_graph(remain_edges, [], u, len(
                remain_vertexes), transition[2], allow_transitions, allow_snapshots, [], 0, 0)
            if not res:
                theta.append(False)
                break
            # Next snapshot u' (one point distribution _u')
            rho = [(transition[1], 1)]
            pairs = []
            # Other states u'_i
            for trans_u in allow_transitions:
                pairs.append((transition[1], trans_u[1]))
            # Build equivalence relation
            disjoint_union = Close_Weak(pairs, Visited)
            R = disjoint_union
            # LP(G,rho,u,alpha,R)
            solution = SolveLP(allow_transitions, allow_snapshots,
                               rho, u, len(snapshot_2), transition[2], R)
            # Result is kept as theta_i
            theta.append(solution)
    b_res = generate_condition_conjunction(theta)
    # print("Match ", (t, u), " action result")
    # print("============================= (1)boolean: ", b_res)
    # if len(N) < 10:
    #     print("============================= (2)Table N: ", N)
    # else:
    #     print("============================= (2)Table N: ", len(N), " items")
    # if len(B) < 10:
    #     print("============================= (2)Table B: ", B)
    # else:
    #     print("============================= (2)Table B: ", len(B), " items")
    return b_res


def MatchAction_Weak_Reverse(alpha, u, t, Visited):
    global NonBisim, Bisim
    # print("Match Action Weak.")
    # print(alpha, t, u)
    theta = []
    b_res = None
    if alpha in invisible_actions:
        # Check the step condition
        # for each u -> u', find t => t'
        trans_u_list = [tr for tr in transitions_2 if (
            tr[0] == u) & (tr[3] in invisible_actions)]
        for transition in trans_u_list:
            allow_transitions = []
            allow_snapshots = []
            # Construct the graph of allow transitions G
            remain_edges = copy.deepcopy(transitions_1)
            remain_vertexes = copy.deepcopy(snapshot_1)
            res = constr_graph(remain_edges, [], t, len(
                remain_vertexes), "tau", allow_transitions, allow_snapshots, [], 0, 0)
            if not res:
                theta.append(False)
                break
            if (transition[3] == "measurement") | (transition[3] == "operation"):
                # Distribution sigma, sigma = u'
                sigma = []
                pairs = []
                trans_distribution = [
                    tr for tr in transitions_2 if tr[0] == transition[1]]
                for distr_member in trans_distribution:
                    u_ = distr_member[1]
                    u_prob = 0
                    if distr_member[2] == "tau":
                        u_prob = 1
                    else:
                        u_prob = distr_member[2]
                    sigma.append((u_, u_prob))
                    # Collect the pairs (t', u') for further matching
                    # The empty transition can make system stay at t so that u' = u
                    pairs.append((t, distr_member[1]))
                    # Other states u'_i
                    for trans_t in allow_transitions:
                        pairs.append((trans_t[1], distr_member[1]))
            elif (transition[3] == "matched") | (transition[3] == "silent"):
                # Next snapshot t' (one point distribution _t')
                sigma = [(transition[1], 1)]
                # The empty transition can make system stay at t so that u' = u
                pairs = [(t, transition[1])]
                # Other states u'_i
                for trans_t in allow_transitions:
                    pairs.append((trans_t[1], transition[1]))
            # Build equivalence relation
            disjoint_union = Close_Weak(pairs, Visited)
            R = []
            for pair in disjoint_union:
                R.append((pair[1], pair[0]))
            # LP(G,rho,u,alpha,R)
            solution = SolveLP(allow_transitions, allow_snapshots,
                               sigma, t, len(snapshot_1), "tau", R)
            # Result is kept as theta_i
            theta.append(solution)
    elif alpha in comm_actions:
        # Check the step condition
        # for each t -> t', find u => u'
        trans_u_list = [tr for tr in transitions_2 if (
            tr[0] == u) & (tr[3] not in invisible_actions)]
        for transition in trans_u_list:
            allow_transitions = []
            allow_snapshots = []
            # Construct the graph of allow transitions G
            remain_edges = copy.deepcopy(transitions_1)
            remain_vertexes = copy.deepcopy(snapshot_1)
            res = constr_graph(remain_edges, [], t, len(
                remain_vertexes), transition[2], allow_transitions, allow_snapshots, [], 0, 0)
            if not res:
                theta.append(False)
                break
            # Next snapshot u' (one point distribution _u')
            sigma = [(transition[1], 1)]
            pairs = []
            # Other states u'_i
            for trans_u in allow_transitions:
                pairs.append((trans_u[1], transition[1]))
            # Build equivalence relation
            disjoint_union = Close_Weak(pairs, Visited)
            R = []
            for pair in disjoint_union:
                R.append((pair[1], pair[0]))
            # LP(G,rho,u,alpha,R)
            solution = SolveLP(allow_transitions, allow_snapshots,
                               sigma, t, len(snapshot_1), transition[2], R)
            # Result is kept as theta_i
            theta.append(solution)
    b_res = generate_condition_conjunction(theta)
    # print("Match ", (t, u), " action result")
    # print("============================= (1)boolean: ", b_res)
    # if len(N) < 10:
    #     print("============================= (2)Table N: ", N)
    # else:
    #     print("============================= (2)Table N: ", len(N), " items")
    # if len(B) < 10:
    #     print("============================= (2)Table B: ", B)
    # else:
    #     print("============================= (2)Table B: ", len(B), " items")
    return b_res


def Close_Weak(pairs, Visited):
    global NonBisim, Bisim, Assumed
    disjoint_union = []
    for pair in pairs:
        if pair in NonBisim:
            continue
        elif pair in Bisim:
            if pair not in disjoint_union:
                disjoint_union.append(pair)
        elif pair in Visited:
            if pair not in Assumed:
                Assumed.append(pair)
        else:
            res = Match_Weak(pair[0], pair[1], Visited)
            if res == True:
                if pair not in disjoint_union:
                    disjoint_union.append(pair)
    return disjoint_union


def SolveLP(transitions, snapshots, distribution, s, t, action, equivalence):
    flow_network = fn.constr_trans(transitions, equivalence, action, s, t)
    edges = flow_network[0]
    vertexes = flow_network[1]
    res = fn.solve_lp(edges, vertexes, distribution, -1, t,
                      len(transitions), len(snapshots)+2)
    # print(res)
    if res.success == None:
        return False
    return res.success


def get_weak_act(t, u):
    t_next_transition = [
        transition for transition in transitions_1 if transition[0] == t]
    u_next_transition = [
        transition for transition in transitions_2 if transition[0] == u]
    t_next_action = [transition[3] for transition in t_next_transition]
    u_next_action = [transition[3] for transition in u_next_transition]
    t_alpha_set = set()
    u_alpha_set = set()
    for action in comm_actions:
        if (action in t_next_action):
            t_alpha_set.add(action)
        if (action in u_next_action):
            u_alpha_set.add(action)
    for action in invisible_actions:
        if (action in t_next_action):
            t_alpha_set.add("silent")
        if (action in u_next_action):
            u_alpha_set.add("silent")
    return (t_alpha_set, u_alpha_set)

#
# Adjust the transitions tuples of the pLTS for later invoking.
# At the same time, return the set of u' that reachable through the weak transition.
# * Similar to allow_path in flow_network.
#


def constr_graph(remain_edges, visited_vertexes, s, t, action, path, pvertex, temp_path, distr_count, flag):
    visited_vertexes.append(s)
    exist = False
    transitions = [tr for tr in remain_edges if tr[0] == s]
    if (len(transitions) == 0) & (flag == 1):
        pvertex.append(s)
        return True
    if action == "tau":
        for transition in transitions:
            for tr in path:
                if (transition[0] == tr[0]) & (transition[1] == tr[1]):
                    break
            for transition in temp_path:
                if (transition[0] == tr[0]) & (transition[1] == tr[1]):
                    break
            if transition[1] in visited_vertexes:
                temp_path.append(transition)
            elif transition[2] == "tau":
                # Store as a distribution
                if (transition[3] == "measurement") | (transition[3] == "operation"):
                    distr_count = distr_count + 1
                    target_vertex = transition[1]
                    distr_transitions = [
                        tr for tr in remain_edges if tr[0] == target_vertex]
                    remain_edges.remove(transition)
                    for distr_transition in distr_transitions:
                        next_path = []
                        next_pvertex = []
                        if isinstance(distr_transition[2], int) | isinstance(distr_transition[2], float):
                            prob = distr_transition[2]
                            # Transform the format " 1->1' and 1'->rho " into " 1->rho " directly
                            next_path.append(
                                (transition[0], distr_transition[1], "tau", prob, distr_count))
                        remain_edges.remove(distr_transition)
                        res = constr_graph(
                            remain_edges, visited_vertexes, distr_transition[1], t, action, next_path, next_pvertex, temp_path, distr_count, 1)
                        if res:
                            path.extend(next_path)
                            pvertex.extend(next_pvertex)
                        exist = exist or res
                # Just store the transition
                elif (transition[3] == "matched") | (transition[3] == "silent"):
                    next_path = []
                    next_pvertex = []
                    next_path.append((transition[0], transition[1], "tau", 1))
                    remain_edges.remove(transition)
                    res = constr_graph(
                        remain_edges, visited_vertexes, transition[1], t, action, next_path, next_pvertex, temp_path, distr_count, 1)
                    if res:
                        path.extend(next_path)
                        pvertex.extend(next_pvertex)
                    exist = exist or res
            elif transition[2] != "tau":
                exist = True
    elif action != "tau":
        for transition in transitions:
            for tr in path:
                if (transition[0] == tr[0]) & (transition[1] == tr[1]):
                    break
            for transition in temp_path:
                if (transition[0] == tr[0]) & (transition[1] == tr[1]):
                    break
            if transition[1] in visited_vertexes:
                temp_path.append(transition)
            elif is_same_action(transition[2], action) & (flag == 0):
                next_path = []
                next_pvertex = []
                next_path.append((transition[0], transition[1], action, 1))
                remain_edges.remove(transition)
                res = constr_graph(remain_edges, visited_vertexes,
                                   transition[1], t, action, next_path, next_pvertex, temp_path, distr_count, 1)
                if (res):
                    path.extend(next_path)
                    pvertex.extend(next_pvertex)
                exist = exist or res
            elif (transition[2] == "tau") & ((flag == 0) | (flag == 1)):
                # Store as a distribution
                if (transition[3] == "measurement") | (transition[3] == "operation"):
                    distr_count = distr_count + 1
                    target_vertex = transition[1]
                    distr_transitions = [
                        tr for tr in remain_edges if tr[0] == target_vertex]
                    remain_edges.remove(transition)
                    for distr_transition in distr_transitions:
                        next_path = []
                        next_pvertex = []
                        if isinstance(distr_transition[2], int) | isinstance(distr_transition[2], float):
                            prob = distr_transition[2]
                            # Transform the format " 1->1' and 1'->rho " into " 1->rho " directly
                            next_path.append(
                                (transition[0], distr_transition[1], "tau", prob, distr_count))
                        remain_edges.remove(distr_transition)
                        res = constr_graph(
                            remain_edges, visited_vertexes, distr_transition[1], t, action, next_path, next_pvertex, temp_path, distr_count, flag)
                        if res:
                            path.extend(next_path)
                            pvertex.extend(next_pvertex)
                        exist = exist or res
                # Just store the transition
                elif (transition[3] == "matched") | (transition[3] == "silent"):
                    next_path = []
                    next_pvertex = []
                    next_path.append((transition[0], transition[1], "tau", 1))
                    remain_edges.remove(transition)
                    res = constr_graph(
                        remain_edges, visited_vertexes, transition[1], t, action, next_path, next_pvertex, temp_path, distr_count, flag)
                    if res:
                        path.extend(next_path)
                        pvertex.extend(next_pvertex)
                    exist = exist or res
            elif (not is_same_action(transition[2], action)) & (flag == 1):
                exist = True
    if exist:
        pvertex.append(s)
        path_loop = [tr for tr in temp_path if tr[1] == s]
        path.extend(path_loop)
    return exist


def generate_condition_conjunction(theta):
    b_conjunction = None
    if len(theta) > 0:
        for b in theta:
            if b_conjunction is None:
                b_conjunction = b
            else:
                b_conjunction = And(b_conjunction, b)
        # b_res = simplify(b_conjunction) This function in Z3 module will cause some problem cannot explained
        b_res = b_conjunction
        return b_res
    else:
        return False


def is_same_action(action_t, action_u):
    behavior_t = ''
    channel_t = ''
    behavior_u = ''
    channel_u = ''
    for action in comm_actions:
        for i in range(len(action_t)):
            if (action_t[i] == action) | (action_t[i:i+1] == action):
                behavior_t = action
                channel_t = action_t[0:i]
                break
    for action in comm_actions:
        for ii in range(len(action_u)):
            if (action_u[ii] == action) | (action_u[ii:ii+1] == action):
                behavior_u = action
                channel_u = action_u[0:ii]
                break
    if behavior_t == behavior_u:
        if behavior_t == "!" or behavior_t == ".!":
            # Store the variable of output action
            e_1 = ''
            e_2 = ''
            (e_1, e_2) = output_parallel_variables(action_t, action_u)
            b_new = (e_1 == e_2)
            if b_new == True:
                return (channel_t == channel_u)
        else:
            return (channel_t == channel_u)
    # print(channel_t,channel_u)
    return False


def init_qLTS(path_11, path_12, path_21, path_22):
    global in_1, out_1, qlts_1, op_1, transitions_1, snapshot_1, initial_state_1
    global regx_1, regq_1, mat_size, state_1, statement_1
    global in_2, out_2, qlts_2, op_2, transitions_2, snapshot_2, initial_state_2
    global regx_2, regq_2, state_2, statement_2
    # First qLTS
    try:
        # in_1 = "examples/concrete1-1.txt"
        # out_1 = "parse_output/concrete1-1.gv"
        # in_1 = "examples/weak_concrete3-1-m.txt"
        # out_1 = "parse_output/weak_concrete3-1-m.gv"
        # in_1 = "examples/concrete4-1.txt"
        # out_1 = "parse_output/concrete4-1.gv"
        # in_1 = "examples/concreteBB84.txt"
        # out_1 = "parse_output/concreteBB84.gv"
        in_1 = path_11
        out_1 = path_12
        qlts_1 = qlts.qlts(in_1, out_1)
        op_1 = qlts.op
        qLTS_index = len(qlts.qLTS)-1
        transitions_1 = qlts.transitions[qLTS_index]
        snapshot_1 = qlts.snapshots[qLTS_index]
        initial_state_1 = qlts.initial_state
        regx_1 = qlts.regx
        regq_1 = qlts.regq
        regx_val_1 = qlts.regx_val
        regq_val_1 = qlts.regq_val
        mat_size = qlts.mat_size
        state_1 = qlts.state
        statement_1 = qlts.statement
        # print("First qLTS has been built, please input the next one.")
    except EOFError:
        exit()
    # Reset all of the global variable
    reset_qlts()
    # Second qLTS
    try:
        # in_2 = "examples/weak_concrete1-2.txt"
        # out_2 = "parse_output/weak_concrete1-2.gv"
        # in_2 = "examples/weak_concrete3-2-m.txt"
        # out_2 = "parse_output/weak_concrete3-2-m.gv"
        # in_2 = "examples/weak_concrete4-2.txt"
        # out_2 = "parse_output/weak_concrete4-2.gv"
        # in_2 = "examples/weak_concreteBB84-spec.txt"
        # out_2 = "parse_output/weak_concreteBB84-spec.gv"
        in_2 = path_21
        out_2 = path_22
        qlts_2 = qlts.qlts(in_2, out_2)
        op_2 = qlts.op
        qLTS_index = len(qlts.qLTS)-1
        transitions_2 = qlts.transitions[qLTS_index]
        snapshot_2 = qlts.snapshots[qLTS_index]
        initial_state_2 = qlts.initial_state
        regx_2 = qlts.regx
        regq_2 = qlts.regq
        regx_val_2 = qlts.regx_val
        regq_val_2 = qlts.regq_val
        mat_size = qlts.mat_size
    #	if mat_size != qlts.mat_size:
    #		print("Warning: Registers are of different sizes.")
        state_2 = qlts.state
        statement_2 = qlts.statement
        # print("Second qLTS has been built, then check the bisimulation.")
    except EOFError:
        exit()
    # Reset all of the global variable
    reset_qlts()


# Strong Bisimulation Test
# init_qLTS("examples/concrete1-1.txt", "parse_output/concrete1-1.gv",
#           "examples/concrete1-2.txt", "parse_output/concrete1-2.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concrete2-1.txt", "parse_output/concrete2-1.gv",
#           "examples/concrete2-2.txt", "parse_output/concrete2-2.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concrete3-1.txt", "parse_output/concrete3-1.gv",
#           "examples/concrete3-2.txt", "parse_output/concrete3-2.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concrete3-1-m.txt", "parse_output/concrete3-1-m.gv",
#           "examples/concrete3-2-m.txt", "parse_output/concrete3-2-m.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concrete4-1.txt", "parse_output/concrete4-1.gv",
#           "examples/concrete4-2.txt", "parse_output/concrete4-2.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concreteBB84.txt", "parse_output/concreteBB84.gv",
#           "examples/concreteBB84-spec.txt", "parse_output/concreteBB84-spec.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concreteBB84-eavesdropper.txt", "parse_output/concreteBB84-eavesdropper.gv",
#           "examples/concreteBB84-eavesdropper-spec.txt", "parse_output/concreteBB84-eavesdropper-spec.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concreteBB84-eavesdropper-m.txt", "parse_output/concreteBB84-eavesdropper-m.gv",
#           "examples/concreteBB84-eavesdropper-spec-m.txt", "parse_output/concreteBB84-eavesdropper-spec-m.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concreteB92.txt", "parse_output/concreteB92.gv",
#           "examples/concreteB92-spec.txt", "parse_output/concreteB92-spec.gv")
# Bisimulation(0, 0)
# init_qLTS("examples/concreteEPR.txt", "parse_output/concreteEPR.gv",
#           "examples/concreteEPR-spec.txt", "parse_output/concreteEPR-spec.gv")
# Bisimulation(0, 0)

# Weak Bisimulation Test
# qlts_timer = time.time()
# init_qLTS("examples/concrete1-1.txt", "parse_output/concrete1-1.gv",
#           "examples/weak_concrete1-2.txt", "parse_output/weak_concrete1-2.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/concrete2-1.txt", "parse_output/concrete2-1.gv",
#           "examples/concrete2-2.txt", "parse_output/concrete2-2.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/concrete3-1.txt", "parse_output/concrete3-1.gv",
#           "examples/weak_concrete3-2.txt", "parse_output/weak_concrete3-2.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/weak_concrete3-1-m.txt", "parse_output/weak_concrete3-1-m.gv",
#           "examples/weak_concrete3-2-m.txt", "parse_output/weak_concrete3-2-m.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/concrete4-1.txt", "parse_output/concrete4-1.gv",
#           "examples/weak_concrete4-2.txt", "parse_output/weak_concrete4-2.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/concreteBB84.txt", "parse_output/concreteBB84.gv",
#           "examples/weak_concreteBB84-spec.txt", "parse_output/weak_concreteBB84-spec.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/weak_concreteB92.txt", "parse_output/weak_concreteB92.gv",
#           "examples/weak_concreteB92-spec.txt", "parse_output/weak_concreteB92-sepc.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)
# qlts_timer = time.time()
# init_qLTS("examples/weak_concreteE91.txt", "parse_output/weak_concreteE91.gv",
#           "examples/weak_concreteE91-spec.txt", "parse_output/weak_concreteE91-spec.gv")
# print("qLTS Generate in ", time.time() - qlts_timer)
# Weak_Bisimulation(0,0)

# checker = input('[Strong/Weak] > ')
# in_1 = input('file 1 name > ')
# out_1 = input('output file 1 name > ')
# in_2 = input('file 2 name > ')
# out_2 = input('output file 2 name > ')
# init_qLTS(in_1, out_1, in_2, out_2)
# if (checker=='Strong') or (checker=='strong'):
#     Bisimulation(0, 0)
# if (set(checker)==('S','s','T','t','R','r','O','o','N','n','G','g') and len(checker)<8):
#     Bisimulation(0, 0)
# if (checker=='Weak') or (checker=='weak'):
#     Weak_Bisimulation(0,0)
# if (set(checker)==('W','w','E','e','A','a','K','k') and len(checker)<6):
#     Weak_Bisimulation(0,0)