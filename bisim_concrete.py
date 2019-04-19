import sys
print(sys.path)
import qlts_concrete as qlts
from qlts_concrete import tt,ff,tau
from z3 import *
import pprint
import numpy as np
import sympy as sp
import gc
import time

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

#First qLTS
try:
	in_1 = input('file 1 name > ')
	out_1 = input('output file 1 name > ')
	# in_1 = "examples/concreteBB84.txt"
	# out_1 = "parse_output/concreteBB84.gv"
	qlts_1 = qlts.qlts(in_1,out_1)
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
#Reset all of the global variable
reset_qlts()
#Second qLTS
try:
	in_2 = input('file 2 name > ')
	out_2 = input('output file 2 name > ')
	# in_2 = "examples/concreteBB84-spec.txt"
	# out_2 = "parse_output/concreteBB84-spec.gv"
	qlts_2 = qlts.qlts(in_2,out_2)
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
	statement_2  = qlts.statement
	# print("Second qLTS has been built, then check the bisimulation.")
except EOFError:
	exit()

timer = 0

def Bisim(t,u):
	global timer
	timer = time.time()
	# print("//Check Bisimulation\nStart: ")
	res = Match(t,u,[])
	# print("//Check Bisimulation\nResult: ",res[0])
	if len(res[1]) > 10:
		print("NonBisim: ",len(res[1]))
	else:
		print("NonBisim: ",res[1])
	if len(res[2]) > 10:
		print("Bisim: ",len(res[2]))
	else:
		print("Bisim: ",res[2])
	if res[0]==False:
		print("Not Bisimilar")
	else:
		print("Bisimilar")
	timer = time.time() - timer
	print(timer)
	return res

def Match(t,u,W):
	#print("Match.")
	#print(t,u)
	mgb = True
	N = []
	B = []
	delta = {}
	theta = {}
	if W.__contains__((t,u)):
		mgb = True
		N = []
		B.append((t,u))
	else:
		gammas = get_Act(t,u)
		#print("Gamma : ",gammas)
		if gammas is None:
			N.append((t,u))
			return (ff,N,B)
		for gamma in gammas:
			match_action_res = MatchAction(gamma,t,u,W)
			mgb = And(mgb,match_action_res[0])
			N = list(set(N+match_action_res[1]))
			B = list(set(B+match_action_res[2]))
	# Theta result
	# Quantum variable equality qv(t)==qv(u)
	b_qveq = (set(regq_1).issubset(set(regq_2)) or set(regq_2).issubset(set(regq_1)))
	# Density operator equality E==F
	sn_t = snapshot_1[t]
	sn_u = snapshot_2[u]
	dens_t = sn_t['density operator']
	dens_u = sn_u['density operator']
	b_supereq = superoperator_equivalence(dens_t,dens_u)
	b_cond = And(b_qveq,b_supereq)
	#print("---------------------Distribution elements Table: ",O)
	#print("---------------------Conditions: ",b_cond)
	mgb = simplify(And(mgb,b_cond))
	# NonBisim result
	if mgb==False:
		N.append((t,u))
	elif mgb==True:
		B.append((t,u))
	else:
		print("Problem exists on the boolean value theta.")
	# print("Match ",(t,u)," result")
	# print("======================= (1)boolean: ",mgb)
	# if len(N) < 10:
	# 	print("======================= (2)Table: ",N)
	# else:
	# 	print("======================= (2)Table: ",len(N)," items")
	# if len(B) < 10:
	# 	print("======================= (2)Table: ",B)
	# else:
	# 	print("======================= (2)Table: ",len(B)," items")
	return (mgb,N,B)

def MatchAction(gamma,t,u,W):
	#print("Match Action.")
	# print(gamma,t,u)
	b_list = []
	b_list_ = []
	N = []
	B = []
	b_conjunction = None
	if gamma=="silent" or gamma=="measurement":
		trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[3]=='silent' or transition[3]=='measurement')]
		trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[3]=='silent' or transition[3]=='measurement')]
		mgb = np.ones((len(trans_t_list),len(trans_u_list)),dtype=BoolRef)
		pair = (t,u)
		if not (W.__contains__(pair)):
			W.append(pair)
		for i in range(len(trans_t_list)):
			trans_t = trans_t_list[i]
			for j in range(len(trans_u_list)):
				trans_u = trans_u_list[j]
				matchdistribution_res = ()
				matchdistribution_res = MatchDistribution(trans_t[1],trans_u[1],W)
				mgb[i,j] = matchdistribution_res[0]
				N = list(set(N+matchdistribution_res[1]))
				B = list(set(B+matchdistribution_res[2]))
		for i in range(len(trans_t_list)):
			b_disjunction = None
			for j in range(len(trans_u_list)):
				if b_disjunction==None:
					b_disjunction = bool(mgb[i,j])
				else:
					b_disjunction = Or(b_disjunction,bool(mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = b_disjunction
			else:
				b_conjunction = And(b_conjunction,b_disjunction)
		for j in range(len(trans_u_list)):
			b_disjunction = None
			for i in range(len(trans_t_list)):
				if b_disjunction==None:
					b_disjunction = bool(mgb[i,j])
				else:
					b_disjunction = Or(b_disjunction,bool(mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = b_disjunction
			else:
				b_conjunction = And(b_conjunction,b_disjunction)
	else:
		trans_t_list = []
		trans_u_list = []
		#配合get_Act中暂时添加的部分，避免遇到经communication产生的silent时依然尝试匹配分布
		if gamma=='matched':
			trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[3]=='silent' or transition[3]=='matched')]
			trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[3]=='silent' or transition[3]=='matched')]
		else:
			trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[3]!='silent' and transition[3]!='matched')]
			trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[3]!='silent' and transition[3]!='matched')]
		mgb = np.ones((len(trans_t_list),len(trans_u_list)),dtype=BoolRef)
		pair = (t,u)
		if not (W.__contains__(pair)):
			W.append(pair)
		for i in range(len(trans_t_list)):
			trans_t = trans_t_list[i]
			for j in range(len(trans_u_list)):
				trans_u = trans_u_list[j]
				match_res = ()
				match_res = Match(trans_t[1],trans_u[1],W)
				mgb[i,j] = match_res[0]
				N = list(set(N+match_res[1]))
				B = list(set(B+match_res[2]))
				if gamma=="!" or gamma==".!":
					#动作为Output时的特殊情况，保存输出变量
					e_1 = ''
					e_2 = ''
					(e_1,e_2) = output_parallel_variables(trans_t,trans_u)
					b_new = (e_1==e_2)
					if b_new==False:
						mgb[i,j] = False
		for i in range(len(trans_t_list)):
			b_disjunction = None
			for j in range(len(trans_u_list)):
				if b_disjunction==None:
					b_disjunction = bool(mgb[i,j])
				else:
					b_disjunction = Or(b_disjunction,bool(mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = b_disjunction
			else:
				b_conjunction = And(b_conjunction,b_disjunction)
		for j in range(len(trans_u_list)):
			b_disjunction = None
			for i in range(len(trans_t_list)):
				if b_disjunction==None:
					b_disjunction = bool(mgb[i,j])
				else:
					b_disjunction = Or(b_disjunction,bool(mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = b_disjunction
			else:
				b_conjunction = And(b_conjunction,b_disjunction)
	# print(b_conjunction)
	if b_conjunction==None:
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
	return (b_res,N,B)

def MatchDistribution(t,u,W):
	# print("Match Distribution.")
	# print(t,u)
	N = []
	B = []
	mgb = None
	#构造分布
	delta = {}
	theta = {}
	distr_elements = []
	candidate = []
	for transition in transitions_1:
		for another_transition in transitions_2:
			if transition[0]==t and another_transition[0]==u:
				t_ = transition[1]
				u_ = another_transition[1]
				t_prob = snapshot_1[t_]['probability']
				delta.update({(t_,'t') : t_prob})
				u_prob = snapshot_2[u_]['probability']
				theta.update({(u_,'u') : u_prob})
				if not distr_elements.__contains__((t_,'t')):
					distr_elements.append((t_,'t'))
				if not distr_elements.__contains__((u_,'u')):
					distr_elements.append((u_,'u'))
				match_res = ()
				match_res = Match(t_,u_,W)
				candidate.append((t_,u_))
				#print(match_res,T_union)
				# print("Distribution mgb: ",match_res[0])
				if mgb is None:
					mgb = match_res[0]
				else:
					mgb = Or(mgb,match_res[0])
				N = list(set(N+match_res[1]))
				B = list(set(B+match_res[2]))
	# Prepare the generation of equivalence relations, mark the elements in N with its owner qLTS
	T_disjoint_union = []
	for t_map in candidate:
		if t_map not in N:
			T_disjoint_union.append(((t_map[0],'t'), (t_map[1],'u')))
	# Build equivalence relation
	R = equivalence_relation(T_disjoint_union)
	#print(distr_elements,T_union,delta,theta,R)
	check_result = Check(distr_elements,T_disjoint_union,delta,theta,R)
	b_res = simplify(And(mgb,check_result))
	#b_res = check_result
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
	return (b_res,N,B)

def Check(distr_elements,T_disjoint_union,delta,theta,R):
	# print("Check.")
	# print("Distribution elements: ",distr_elements)
	#print("Disjoint Unions: ",T_disjoint_union)
	#pprint.pprint(delta)
	#pprint.pprint(theta)
	b = True
	equivalence_classes = []
	if len(T_disjoint_union) is 0:
		# print("Warning: No pair in distribution matched.")
		b = False
	#Compute equivalence class
	for s in distr_elements:
		#pprint.pprint(s)
		equivalence_class = set()
		for relation in R:
			if relation[0] == s:
				equivalence_class.add(relation[1])
		if not (equivalence_classes.__contains__(equivalence_class) or equivalence_class==set()):
			equivalence_classes.append(equivalence_class)
	# if len(equivalence_classes) < 5:
	# 	print("Equivalence classes: ",equivalence_classes)
	# else:
	# 	print("Equivalence classes: ",len(equivalence_classes)," items")
	for equivalence_class in equivalence_classes:
		#pprint.pprint(equivalence_class)
		# Check equivalence class
		# Distinguish the owner qLTS from the mark
		m_t = 0.0
		m_u = 0.0
		for ele in equivalence_class:
			if ele[1] == 't':
				if delta.__contains__(ele):
					m_t = m_t + delta[ele]
			if ele[1] == 'u':
				if theta.__contains__(ele):
					m_u = m_u + theta[ele]
		m_t = np.around(m_t,decimals=2)
		m_u = np.around(m_u,decimals=2)
		if not m_t == m_u:
			b = False
	# 	print("======",m_t,m_u)
	# print("Check result: ",b)
	return b

# Compute the equivalence relation
def equivalence_relation(T_union):
    T = set(T_union)
    R = set()
    R = R|T
    #print(R)
    for tup in T:
        R.add(tup[::-1])
    #print(R)
    T = R|T
    for (a,b) in T:
        for (c,d) in T:
            if b == c and ((a,d) not in T):
                R.add((a,d))
    #print(R)
    return R

def get_Act(t,u):
	global timer
	gammas = set()
	t_count = [transition for transition in transitions_1 if transition[0]==t]
	u_count = [transition for transition in transitions_2 if transition[0]==u]
	#print(t_count,u_count)
	if (len(t_count)==0 and len(u_count)!=0) or (len(t_count)!=0 and len(u_count)==0):
		print("Different Depth. Not Bisimilar.")
		timer = time.time() - timer
		print(timer)
		exit(0)
	for transition in transitions_1:
		for another_transition in transitions_2:
			# Cooperate with the code in MatchAction() to avoid the matching cause the by silent actions
			# which indeed is caused by communications
			if transition[0]==t and another_transition[0]==u:
				if transition[3]==another_transition[3]:
					if (transition[3]=='!' and another_transition[3]=='!') or (transition[3]=='?' and another_transition[3]=='?') or (transition[3]=='.!' and another_transition[3]=='.!') or (transition[3]=='.?' and another_transition[3]=='.?'):
						(c1,c2) = parallel_channel(transition,another_transition)
						if c1==c2:
							gammas.add(transition[3])
					else:
						gammas.add(transition[3])
				if (transition[3]=='measurement' and another_transition[3]=='silent') or (another_transition[3]=='measurement' and transition[3]=='silent'):
					gammas.add('silent')
				if (transition[3]=='matched' and another_transition[3]=='silent') or (another_transition[3]=='matched' and transition[3]=='silent'):
					gammas.add('matched')
	if (len(t_count)>0  and len(u_count)>0 and len(gammas)==0):
		# print("No pair of actions in the next step are the same. Not Bisimilar.")
		return None
	return gammas

def superoperator_equivalence(E,F):
	#print(E)
	#print(F)
	b = True
	dem = mat_size
	E_trace = 0
	F_trace = 0
	for i in range(dem):
		E_trace = E_trace+E[i,i]
		F_trace = F_trace+F[i,i]
	E_trace = np.around(E_trace,decimals=2)
	F_trace = np.around(F_trace,decimals=2)
	if not E_trace==F_trace:
		b = False
	#print("Equivalence result:",b)
	return b

def superoperator_distribution_equivalence(lst):
	#print(lst)
	superoperator_size = mat_size**2
	E = np.zeros([superoperator_size,superoperator_size])
	F = np.zeros([superoperator_size,superoperator_size])
	t_list = []
	u_list = []
	for pair in lst:
		t_distribution = pair[0]
		u_distribution = pair[1]
		E0 = snapshot_1[t_distribution]['density operator']
		F0 = snapshot_2[u_distribution]['density operator']
		for transition in transitions_1:
			for another_transition in transitions_2:
				if transition[0]==t_distribution and another_transition[0]==u_distribution:
					t_ = transition[1]
					u_ = another_transition[1]
					if not t_list.__contains__(t_):
						E = E + snapshot_1[t_]['density operator']
						t_list.append(t_)
					if not u_list.__contains__(u_):
						F = F + snapshot_2[u_]['density operator']
						u_list.append(u_)
	if superoperator_equivalence(E,F) is True:
		matched_list = []
		for t_ in t_list:
			for u_ in u_list:
				matched_list.append((t_,u_))
		#print(matched_list)
		return matched_list
	return []

def output_parallel_variables(trans_t,trans_u):
	action_t = trans_t[2]
	action_u = trans_u[2]
	#variable_t = ''
	#variable_u = ''
	#for i in range(len(action_t)):
	#	if action_t[i] == '!' or action_t[i:i+1] == '.!':
	#		variable_t = action_t[i+1:len(action_t)]
	#for i in range(len(action_u)):
	#	if action_u[i] == '!' or action_u[i:i+1] == '.!':
	#		variable_u = action_u[i+1:len(action_u)]
	#print(variable_t,variable_u)
	#return (variable_t,variable_u)
	return (action_t,action_u)

def parallel_channel(trans_t,trans_u):
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
	#print(channel_t,channel_u)
	return (channel_t,channel_u)

Bisim(0,0)