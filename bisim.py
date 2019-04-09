import sys
print(sys.path)
import qlts
from qlts import tt,ff,tau
from z3 import *
import pprint
import numpy as np
import sympy as sp
import gc

def reset_qlts():
	qlts.qLTS = []
	qlts.op = {}
	qlts.transitions = []
	qlts.snapshots = []
	qlts.initial_snapshot = {}
	qlts.transition = []
	qlts.snapshot = []
	qlts.regx = []
	qlts.regq = []
	qlts.state = 0
	qlts.statement = ""

#生成第一个qLTS
try:
	#in_1 = input('file 1 name > ')
	#out_1 = input('output file 1 name > ')
	in_1 = "examples/program3-1.txt"
	out_1 = "parse_output/program3-1.gv"
	qlts_1 = qlts.qlts(in_1,out_1)
	op_1 = qlts.op
	qLTS_index = len(qlts.qLTS)-1
	transitions_1 = qlts.transitions[qLTS_index]
	snapshot_1 = qlts.snapshots[qLTS_index]
	initial_snapshot_1 = qlts.initial_snapshot
	regx_1 = qlts.regx
	regq_1 = qlts.regq
	state_1 = qlts.state
	statement_1 = qlts.statement
	#把经典信息变量声明为符号类型对象，供eval()函数调用
	#sym_1 = sp.var(regx_1)
	#print(sym_1)
	print("First qLTS has been built, please input the next one.")
except EOFError:
	exit()
#Reset所有全局变量
reset_qlts()
#生成第二个qLTS
try:
	#in_2 = input('file 2 name > ')
	#out_2 = input('output file 2 name > ')
	in_2 = "examples/program3-2.txt"
	out_2 = "parse_output/program3-2.gv"
	qlts_2 = qlts.qlts(in_2,out_2)
	op_2 = qlts.op
	qLTS_index = len(qlts.qLTS)-1
	transitions_2 = qlts.transitions[qLTS_index]
	snapshot_2 = qlts.snapshots[qLTS_index]
	initial_snapshot_2 = qlts.initial_snapshot
	regx_2 = qlts.regx
	regq_2 = qlts.regq
	state_2 = qlts.state
	statement_2  = qlts.statement
	#把经典信息变量声明为符号类型对象，供eval()函数调用
	#sym_2 = sp.var(regx_2)
	#print(sym_2)
	print("Second qLTS has been built, then check the bisimulation.")
except EOFError:
	exit()

#Table for elements of matched distribution
O = []

def Bisim(t,u):
	print("//Check Bisimulation\nStart: ")
	res = Match(t,u,True,[])
	print("//Check Bisimulation\nResult: ")
	pprint.pprint(res[0])
	pprint.pprint(res[1])
	s = Solver()
	s.add(Not(res[0]))
	if s.check()==sat:
		print("Not Bisimilar")
		print("Counterexample: ",s.model())
	else:
		print("Bisimilar")
	return res

def Match(t,u,b,W):
	print("Match.")
	print(t,u,b)
	mgb = True
	T = []
	delta = {}
	theta = {}
	if W.__contains__((t,u)):
		mgb = True
		T = []
		delta = {}
		theta = {}
	else:
		gammas = get_Act(t,u)
		print("Gamma : ",gammas)
		for gamma in gammas:
			match_action_res = MatchAction(gamma,t,u,b,W)
			mgb = And(mgb,match_action_res[0])
			T = list(set(T+match_action_res[1]))
			#delta.update(match_action_res[2])
			#theta.update(match_action_res[3])
	#T result
	T.append((t,u,simplify(And(b,mgb))))
	#theta result
	#Quantum variable equality qv(t)==qv(u)
	b_qveq = (set(regq_1).issubset(set(regq_2)) or set(regq_2).issubset(set(regq_1)))
	#Superoperator equality E==F
	sn_t = snapshot_1[t]
	sn_u = snapshot_2[u]
	superoperator_t = sn_t['combined superoperator']
	superoperator_u = sn_u['combined superoperator']
	b_supereq = superoperator_equivalence(superoperator_t,superoperator_u)
	b_cond = Or(Solve(t,u),And(b_qveq,b_supereq))
	#print("---------------------Distribution elements Table: ",O)
	#print("---------------------Conditions: ",b_cond)
	mgb = simplify(And(mgb,b_cond))
	print("Match ",(t,u)," result")
	print("======================= (1)boolean: ",mgb)
	if len(T) < 10:
		print("======================= (2)Table: ",T)
	else:
		print("======================= (2)Table: ",len(T)," items")
	return (mgb,T,delta,theta)

def MatchAction(gamma,t,u,b,W):
	print("Match Action.")
	print(gamma,t,u,b)
	b_list = []
	b_list_ = []
	T = []
	#构造分布
	delta = {}
	theta = {}
	b_conjunction = None
	if gamma=="silent":
		if len(O)==0:
			PreSolve(t,u)
		trans_t_list = [transition for transition in transitions_1 if transition[0]==t and transition[4]=='silent']
		trans_u_list = [transition for transition in transitions_2 if transition[0]==u and transition[4]=='silent']
		mgb = np.ones((len(trans_t_list),len(trans_u_list)),dtype=BoolRef)
		pair = (t,u)
		if not (W.__contains__(pair)):
			W.append(pair)
		for i in range(len(trans_t_list)):
			for j in range(len(trans_u_list)):
				trans_t = trans_t_list[i]
				trans_u = trans_u_list[j]
				b_i = True
				b_j = True
				if trans_t[2] is not tt:
					b_i = trans_t[2]
				b_list.append(b_i)
				if trans_u[2] is not tt:
					b_j = trans_u[2]
				b_list_.append(b_j)
				b_new = And(b,b_i,b_j)
				matchdistribution_res = ()
				matchdistribution_res = MatchDistribution(trans_t[1],trans_u[1],simplify(b_new),W)
				mgb[i,j] = matchdistribution_res[0]
				T = list(set(T)|set(matchdistribution_res[1]))
				#sub_delta = matchdistribution_res[2]
				#delta.update(sub_delta)
				#sub_theta = matchdistribution_res[3]
				#theta.update(sub_theta)
		for i in range(len(trans_t_list)):
			b_disjunction = None
			for j in range(len(trans_u_list)):
				if b_disjunction==None:
					b_disjunction = And(b_list_[j],mgb[i,j])
				else:
					b_disjunction = Or(b_disjunction,And(b_list_[j],mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = Implies(b_list[i],b_disjunction)
			else:
				b_conjunction = And(b_conjunction,(Implies(b_list[i],b_disjunction)))
		for j in range(len(trans_u_list)):
			b_disjunction = None
			for i in range(len(trans_t_list)):
				if b_disjunction==None:
					b_disjunction = And(b_list[i],mgb[i,j])
				else:
					b_disjunction = Or(b_disjunction,And(b_list[i],mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = Implies(b_list[i],b_disjunction)
			else:
				b_conjunction = And(b_conjunction,(Implies(b_list_[j],b_disjunction)))
	else:
		trans_t_list = []
		trans_u_list = []
		#配合get_Act中暂时添加的部分，避免遇到经communication产生的silent时依然尝试匹配分布
		if gamma=='matched':
			trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[4]=='silent' or transition[4]=='matched')]
			trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[4]=='silent' or transition[4]=='matched')]
		else:
			trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[4]!='silent' and transition[4]!='matched')]
			trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[4]!='silent' and transition[4]!='matched')]
		#pprint.pprint(trans_t_list)
		#pprint.pprint(trans_u_list)
		mgb = np.ones((len(trans_t_list),len(trans_u_list)),dtype=BoolRef)
		pair = (t,u)
		#动作为Output时的特殊情况，保存输出变量
		e_1 = ''
		e_2 = ''
		if not (W.__contains__(pair)):
			W.append(pair)
		for i in range(0,len(trans_t_list)):
			for j in range(0,len(trans_u_list)):
				trans_t = trans_t_list[i]
				trans_u = trans_u_list[j]
				b_i = True
				b_j = True
				if trans_t[2] is not tt:
					b_i = trans_t[2]
				b_list.append(b_i)
				if trans_u[2] is not tt:
					b_j = trans_u[2]
				b_list_.append(b_j)
				b_new = And(b,b_i,b_j)
				match_res = ()
				if gamma=="!" or gamma==".!":
					(e_1,e_2) = output_parallel_variables(trans_t,trans_u)
					b_new = And(b_new,e_1==e_2)
				match_res = Match(trans_t[1],trans_u[1],simplify(b_new),W)
				mgb[i,j] = match_res[0]
				T = list(set(T)|set(match_res[1]))
				#sub_delta = match_res[2]
				#delta.update(sub_delta)
				#sub_theta = match_res[3]
				#theta.update(sub_theta)
		for i in range(len(trans_t_list)):
			b_disjunction = None
			for j in range(len(trans_u_list)):
				if gamma=="!" or gamma==".!":
					if b_disjunction==None:
						b_disjunction = And(b_list_[j],mgb[i,j],e_1==e_2)
					else:
						b_disjunction = Or(b_disjunction,And(b_list_[j],mgb[i,j],e_1==e_2))
				else:
					if not b_disjunction:
						b_disjunction = And(b_list_[j],mgb[i,j])
					else:
						b_disjunction = Or(b_disjunction,And(b_list_[j],mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = Implies(b_list[i],b_disjunction)
			else:
				b_conjunction = And(b_conjunction,(Implies(b_list[i],b_disjunction)))
		for j in range(len(trans_u_list)):
			b_disjunction = False
			for i in range(len(trans_t_list)):
				if gamma=="!" or gamma==".!":
					if b_disjunction==None:
						b_disjunction = And(b_list[i],mgb[i,j],e_1==e_2)
					else:
						b_disjunction = Or(b_disjunction,And(b_list[i],mgb[i,j],e_1==e_2))
				else:
					if not b_disjunction:
						b_disjunction = And(b_list[i],mgb[i,j])
					else:
						b_disjunction = Or(b_disjunction,And(b_list[i],mgb[i,j]))
			if b_conjunction is None:
				b_conjunction = Implies(b_list_[j],b_disjunction)
			else:
				b_conjunction = And(b_conjunction,(Implies(b_list_[j],b_disjunction)))
	#print(b_conjunction)
	b_res = simplify(b_conjunction)
	print("Match ",(t,u)," action result")
	print("============================= (1)boolean: ",b_res)
	if len(T) < 10:
		print("============================= (2)Table: ",T)
	else:
		print("============================= (2)Table: ",len(T)," items")
	return (b_res,T,delta,theta)

def MatchDistribution(t,u,b,W):
	print("Match Distribution.")
	print(t,u,b)
	T = []
	mgb = None
	#构造分布
	delta = {}
	theta = {}
	new_delta = {}
	new_theta = {}
	distr_elements = []
	for transition in transitions_1:
		for another_transition in transitions_2:
			if transition[0]==t and another_transition[0]==u:
				t_ = transition[1]
				u_ = another_transition[1]
				t_superoperator = snapshot_1[t_]['superoperator']
				#t_superoperator = np.kron(t_krausoperator,t_krausoperator.conjugate())
				delta.update({(t_,'t') : t_superoperator})
				u_superoperator = snapshot_2[u_]['superoperator']
				#u_superoperator = np.kron(u_krausoperator,u_krausoperator.conjugate())
				theta.update({(u_,'u') : u_superoperator})
				if not distr_elements.__contains__((t_,'t')):
					distr_elements.append((t_,'t'))
				if not distr_elements.__contains__((u_,'u')):
					distr_elements.append((u_,'u'))
				match_res = ()
				match_res = Match(t_,u_,b,W)
				#print(match_res,T_union)
				print("Distribution mgb: ",match_res[0])
				if mgb is None:
					mgb = match_res[0]
				else:
					mgb = Or(mgb,match_res[0])
				T = list(set(T)|set(match_res[1]))
				#sub_delta = match_res[2]
				#for key in sub_delta:
				#	sub_delta[key] = np.around(np.dot(sub_delta[key],t_krausoperator),decimals=3)
				#	if not distr_elements.__contains__((key,'t')):
				#		distr_elements.append(key)
				#new_delta.update(sub_delta)
				#sub_theta = match_res[3]
				#for key in sub_theta:
				#	sub_theta[key] = np.around(np.dot(sub_theta[key],u_krausoperator),decimals=3)
				#	if not distr_elements.__contains__((key,'u')):
				#		distr_elements.append(key)
				#new_theta.update(sub_theta)
	#构造等价关系的准备工作，T中的pair标记所属的qLTS，disjoint union
	#根据b来决定pair集合的内容
	T_disjoint_union = []
	for t_map in T:
		assertion = Implies(b,t_map[2])
		if z3_imply_check(assertion) is True:
			T_disjoint_union.append(((t_map[0],'t'), (t_map[1],'u')))
	#构造等价关系
	R = equivalence_relation(T_disjoint_union)
	#更新分布（与子分布的combination）
	#if new_delta and new_theta:
	#	delta = new_delta
	#	theta = new_theta
	#print(distr_elements,T_union,delta,theta,R)
	check_result = Check(distr_elements,T_disjoint_union,delta,theta,R)
	b_res = simplify(And(mgb,check_result))
	#b_res = check_result
	print("Match ",(t,u)," distribution result")
	print("============================= (1)boolean: ",b_res)
	if len(T) < 10:
		print("============================= (2)Table: ",T)
	else:
		print("============================= (2)Table: ",len(T)," items")
	return (b_res,T,delta,theta)

def Check(distr_elements,T_disjoint_union,delta,theta,R):
	print("Check.")
	print("Distribution elements: ",distr_elements)
	#pprint.pprint(delta)
	#pprint.pprint(theta)
	b = True
	equivalence_classes = []
	if len(T_disjoint_union) is 0:
		print("Warning: No pair in distribution matched.")
		b = False
	#计算等价类
	for s in distr_elements:
		#pprint.pprint(s)
		equivalence_class = set()
		for relation in R:
			if relation[0] == s:
				equivalence_class.add(relation[1])
		if not (equivalence_classes.__contains__(equivalence_class) or equivalence_class==set()):
			equivalence_classes.append(equivalence_class)
	if len(equivalence_classes) < 3:
		print("Equivalence classes: ",equivalence_classes)
	else:
		print("Equivalence classes: ",len(equivalence_classes)," items")
	for equivalence_class in equivalence_classes:
		#pprint.pprint(equivalence_class)
		#验证：每个等价类，从两个分布映射的结果相同
		superoperator_size = 0
		if not len(regq_1)==len(regq_2):
			print("Error: registers' size should be equal.")
			exit()
		else:
			superoperator_size = (2**len(regq_1))**2
		m_t = np.zeros([superoperator_size,superoperator_size])
		m_u = np.zeros([superoperator_size,superoperator_size])
		#利用之前的标记分辨属于哪个qLTS
		for ele in equivalence_class:
			if ele[1] == 't':
				if delta.__contains__(ele):
					m_t = m_t + np.around(np.kron(delta[ele],delta[ele].conjugate()),decimals=3)
			if ele[1] == 'u':
				if theta.__contains__(ele):
					m_u = m_u + np.around(np.kron(theta[ele],theta[ele].conjugate()),decimals=3)
		if not (superoperator_equivalence(m_t,m_u)):
			b = False
		#pprint.pprint(m_t)
		#pprint.pprint(m_u)
	print("Check result: ",b)
	return b

#计算等价关系
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
	gammas = set()
	for transition in transitions_1:
		for another_transition in transitions_2:
			#配合MatchAction中暂时添加的部分，避免遇到经communication产生的silent时依然尝试匹配分布
			if transition[0]==t and another_transition[0]==u:
				if transition[4]==another_transition[4]:
					gammas.add(transition[4])
				if (transition[4]=='matched' and another_transition[4]=='silent') or (another_transition[4]=='matched' and transition[4]=='silent'):
					gammas.add('matched')
	return gammas

def superoperator_equivalence(E,F):
	#print(E)
	#print(F)
	b = True
	l = len(regq_1)
	dem = 2**l
	E_diag = E[0::(dem+1),:]
	F_diag = F[0::(dem+1),:]
	#print(E_diag)
	#print(F_diag)
	for i in range(dem):
		E_column = E_diag[:,i*(dem+1)].sum()
		F_column = F_diag[:,i*(dem+1)].sum()
		#print(E_column)
		#print(F_column)
		if not E_column==F_column:
			b = False
	#print("Equivalence result:",b)
	return b

def superoperator_distribution_equivalence(lst):
	print(lst)
	superoperator_size = (2**len(regq_1))**2
	E = np.zeros([superoperator_size,superoperator_size])
	F = np.zeros([superoperator_size,superoperator_size])
	t_list = []
	u_list = []
	for pair in lst:
		t_distribution = pair[0]
		u_distribution = pair[1]
		E0 = snapshot_1[t_distribution]['combined superoperator']
		F0 = snapshot_2[u_distribution]['combined superoperator']
		for transition in transitions_1:
			for another_transition in transitions_2:
				if transition[0]==t_distribution and another_transition[0]==u_distribution:
					t_ = transition[1]
					u_ = another_transition[1]
					if not t_list.__contains__(t_):
						E = E + snapshot_1[t_]['combined superoperator']
						t_list.append(t_)
					if not u_list.__contains__(u_):
						F = F + snapshot_2[u_]['combined superoperator']
						u_list.append(u_)
	if superoperator_equivalence(E,F) is True:
		matched_list = []
		for t_ in t_list:
			for u_ in u_list:
				matched_list.append((t_,u_))
		if len(matched_list)!=0:
			O.append(matched_list)
		print(matched_list)
		return matched_list
	return []

def output_parallel_variables(trans_u,trans_t):
	action_t = trans_t[3]
	action_u = trans_u[3]
	variable_t = ''
	variable_u = ''
	for i in range(len(action_t)):
		if action_t[i] == '!' or action_t[i] == '.!':
			variable_t = action_t[i+1:len(action_t)]
	for i in range(len(action_u)):
		if action_u[i] == '!' or action_u[i] == '.!':
			variable_u = action_u[i+1:len(action_u)]
	#print(variable_t,variable_u)
	return (variable_t,variable_u)

def z3_check(assertion):
	#print(simplify(assertion))
	s = Solver()
	s.add(Not(assertion))
	if s.check()==sat:
		return False
	else:
		return True

def z3_imply_check(assertion):
	s = Solver()
	s.add(assertion)
	if s.check()==sat:
		return True
	else:
		return False

def Solve(t,u):
	for lst in O:
		if lst.__contains__((t,u)):
			return True
	return False

def next_work(todo_list):
	new_todo_list = []
	distr_elements = []
	for pair in todo_list:
		t = pair[0]
		u = pair[1]
		acts = get_Act(pair[0],pair[1])
		for act in acts:
			if act is 'silent':
				trans_t_list = [transition for transition in transitions_1 if transition[0]==t and transition[4]=='silent']
				trans_u_list = [transition for transition in transitions_2 if transition[0]==u and transition[4]=='silent']
				for i in range(len(trans_t_list)):
					for j in range(len(trans_u_list)):
						trans_t = trans_t_list[i]
						trans_u = trans_u_list[j]
						b = And(trans_t[2],trans_u[2])
						b = simplify(b)
						if z3_imply_check(b) is not False:
							distr_elements.append((trans_t[1],trans_u[1]))
			else:
				trans_t_list = []
				trans_u_list = []
				#配合get_Act中暂时添加的部分，避免遇到经communication产生的silent时依然尝试匹配分布
				if act=='matched':
					trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[4]=='silent' or transition[4]=='matched')]
					trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[4]=='silent' or transition[4]=='matched')]
				else:
					trans_t_list = [transition for transition in transitions_1 if transition[0]==t and (transition[4]!='silent' and transition[4]!='matched')]
					trans_u_list = [transition for transition in transitions_2 if transition[0]==u and (transition[4]!='silent' and transition[4]!='matched')]
				#动作为Output时的特殊情况，保存输出变量
				e_1 = ''
				e_2 = ''
				lst = []
				for i in range(0,len(trans_t_list)):
					for j in range(0,len(trans_u_list)):
						trans_t = trans_t_list[i]
						trans_u = trans_u_list[j]
						b = And(trans_t[2],trans_u[2])
						if act=="!" or act==".!":
							(e_1,e_2) = output_parallel_variables(trans_t,trans_u)
							b = And(b_new,e_1==e_2)
						b = simplify(b)
						if z3_imply_check(b) is not False:
							new_todo_list.append((trans_t[1],trans_u[1]))
				O.append(new_todo_list.copy())
	new_todo_list = new_todo_list + superoperator_distribution_equivalence(distr_elements)
	return new_todo_list

def PreSolve(t,u):
	todo_list = [(t,u)]
	t_list = []
	u_list = []
	while(len(todo_list)>0):
		new_todo_list = next_work(todo_list)
		todo_list = new_todo_list.copy()
	return

Bisim(0,0)