from q_ast import lexer
from parser import parser
from info_parser import info_parser
from graphviz import Digraph
from io import StringIO
from z3 import *
import pprint
import numpy as np
import numpy.matlib
import pandas as pd
import gc

#字典(HashMap)保存operator的名字，根据映射构造矩阵并保存
op = {}
#qLTS
qLTS = []
transitions = []
snapshots = []
#以列表形式保存qLTS的transition和snapshot
initial_snapshot = {}
snapshot = []
transition = []
#Register
regx = []
regq = []
#S
state = 0
#t
statement = ""
#Reserved words
tt=True
ff=False
tau="tau"

def qlts(inputfile,outputfile):
	f = open(inputfile,'r')
	data = f.read()
	global state
	global statement
	lexer.input(data)
	for tok in lexer:
		print(tok.type, tok.value, tok.lineno, tok.lexpos)
	prog = data[0:lexer.info_start-2]
	operator = data[lexer.info_start-1:lexer.info_end]
	print(str(lexer.info_start))
	print(str(lexer.info_end))
	print("Program: "+prog)
	print("Operator Infomation: "+operator)
	print("\n======================Operator Infomation.======================")
	info_result = info_parser.parse(operator)
	tree_print(info_result)
	extract_info(info_result)	
	print("\n======================Start Constructing Graph.======================")
	#创建parser
	result = parser.parse(prog)
	tree_print(result)
	meas_res = {}
	ast_trans2_qLTS(result,state,statement,meas_res)
	print("\n======================        Finished.        ======================")
	pprint.pprint(qLTS)
	pprint.pprint(transitions)
	pprint.pprint(regx)
	pprint.pprint(regq)
	pprint.pprint(op)
	#pprint.pprint(snapshot)
	#画图
	qLTS_index = len(qLTS)-1
	dot = Digraph(comment = "The qLTS "+qLTS[qLTS_index])
	t = transitions[qLTS_index]
	for transition in t:
		if len(transition)>2:
			dot.edge(str(transition[0]),str(transition[1]),str(transition[2])+","+str(transition[3]))
		else:
			dot.edge(str(transition[0]),str(transition[1]))
	print(dot.source)
	s = snapshots[qLTS_index]
	for i in range(len(s)):
		print("State "+str(i))
		pprint.pprint(s[i])
		i = i+1
	#保存结果
	dot.render(outputfile,view=False)

def tree_print(tree):
	print("ID",id(tree),":")
	print(tree.type," ",tree.leaf,end=' ')
	print("Next:",end=' ')
	if tree.children:
		for child in tree.children:
			print(id(child),end=' ')
		for child in tree.children:
			print("")
			tree_print(child)

def parse_bexpr(tree,meas_res):
	if tree.type == 'BinaryOpExpr':
		left = parse_bexpr(tree.children[0],meas_res)
		right = parse_bexpr(tree.children[1],meas_res)
		if tree.leaf == '=':
			assertion = (left==right)
		elif tree.leaf == '+':
			assertion = (left+right)
		elif tree.leaf == '-':
			assertion = (left-right)
		elif tree.leaf == '*':
			assertion = (left*right)
		elif tree.leaf == 'and':
			assertion = And(left,right)
		elif tree.leaf == 'or':
			assertion = Or(left,right)
		elif tree.leaf == '>=':
			assertion = (left>=right)
		elif tree.leaf == '<=':
			assertion = (left<=right)
		elif tree.leaf == '>':
			assertion = (left>right)
		elif tree.leaf == '<':
			assertion = (left<right)
		return assertion
	elif tree.type == 'UnaryOpExpr':
		if tree.leaf == 'not':
			assertion = Not(parse_bexpr(tree.children[0],meas_res))
		return assertion
	elif tree.type == 'Expression':
		if tree.children:
			assertion = parse_bexpr(tree.children[0],meas_res)
			return assertion
		else:
			print("Error: No terms in ().")
			exit()
	else:
		if meas_res.__contains__(tree.leaf):
			return meas_res[tree.leaf]
		if type(tree.leaf) is int:
			return tree.leaf
		return Real(str(tree.leaf))

def constr_reg(process):
	process = process.strip()
	begin = 0
	end = 0
	word_begin = len(process)
	word_end = len(process)
	for i in range(len(process)):
		if process[i] == '(':
			begin = i
		if process[i] == ')':
			end = i
		if process[i] == 'x':
			word_begin = i
		if process[i] == 'q':
			word_begin = i
		if process[i] == ',':
			word_end = i
			if word_end > word_begin:
				if process[word_begin] == 'x':
					bit_name = process[word_begin:word_end].strip()
					if not (regx.__contains__(bit_name)):
						regx.append(bit_name)
				elif process[word_begin] == 'q':
					qbit_name = process[word_begin:word_end].strip()
					if not (regq.__contains__(qbit_name)):
						regq.append(qbit_name)
				else:
					print("Error: the register element should be x (classical bit) or q (quantum bit).")
				word_begin = len(process)
			else:
				print("Error: Syntax error in Process ID.")
		if word_begin < end:
			if process[word_begin] == 'x':
				bit_name = process[word_begin:end].strip()
				if not (regx.__contains__(bit_name)):
					regx.append(bit_name)
			elif process[word_begin] == 'q':
				qbit_name = process[word_begin:end].strip()
				if not (regq.__contains__(qbit_name)):
					regq.append(qbit_name)
			else:
				print("Error: the register element should be x (classical bit) or q (quantum bit).")
	return process[0:begin]

def check_unitary(mat):
	l = len(mat)
	#print(mat)
	#pprint.pprint(np.dot(mat,mat.conjugate().transpose()))
	matH = mat.conjugate().transpose()
	res = np.dot(mat,matH)
	if (res == np.eye(l)).all():
		#pprint.pprint(res)
		return
	else:
		print("Error: Matrix is not unitary.")
		exit(1)

def matrix_presentation(superoperator):
	for i in range(len(superoperator)):
		if superoperator[i] == '[':
			break
	name = superoperator[0:i]
	mat = op[name]
	text = superoperator[i+1:len(superoperator)-1]
	reg = pd.read_csv(StringIO(text)).columns.tolist()
	#print(str(reg)+" transformed by matrix: ")
	res = temp_method_for_building_superoperator(mat,reg)
	return res

#暂时不调整qubit的顺序,只在首尾张量I
def temp_method_for_building_superoperator(mat,reg):
	#print(mat,reg)
	res = []
	l = len(reg)
	lq = len(regq) - len(reg)
	if lq == 0:
		res = np.around(mat,decimals=3)
	elif lq > 0:
		lq_left = 0
		lq_right = 0
		for q in regq:
			if q == reg[0]:
				lq_left = regq.index(q)
				lq_right = lq-lq_left
				break
		if lq_left > 0:
			mat = np.kron(np.eye(2**lq_left),mat)
		if lq_right > 0:
			mat = np.kron(mat,np.eye(2**lq_right))
		res = np.around(mat,decimals=3)
	elif lq < 0:
		print("Error: Too many qubit used much more than the register.")
		exit(1)
	return res

#def normalize(k,s):
#	print("---------")
#	print(k,s)
#	print("---------")
#	l = len(regq)
#	dem = 2**l
#	coeff = 0
#	s_diag = s[0::(dem+1),:]
#	for i in range(dem):
#		coeff = coeff+(s_diag[:,i*(dem+1)].sum())
#	#coeff = s_diag[:,0].sum()
#	if coeff is 0:
#		print("Error: Can not normalize the superoperator.")
#	k = k*coeff
#	new_s = s*coeff**2
#	print("=========")
#	print(coeff,k,new_s)
#	print("=========")
#	return (k,new_s)

#current_bexpr存储ifthen的条件
#meas_res存储Measurement结果的classical bit
def ast_trans2_qLTS(tree,current_state,statement,meas_res,current_bexpr=None):
	global state
	global initial_snapshot
	if tree.type == 'NULL':
		#print("\n--- End of the sequencial process.")
		return (tt,tree.leaf)
	#新添加运算符Next，帮助Parallel的描述
	elif tree.type == 'Next':
		state = 0
		ast_trans2_qLTS(tree.children[0],state,tree.children[0].stmt,meas_res)
		state = 0
		ast_trans2_qLTS(tree.children[1],state,tree.children[1].stmt,meas_res)
		return
	elif tree.type == 'BinaryOpProc':
		if tree.leaf == '+':
			if tree.children:
				#print("Branching")
				ast_trans2_qLTS(tree.children[0],current_state,tree.children[0].stmt,meas_res)
				ast_trans2_qLTS(tree.children[1],current_state,tree.children[1].stmt,meas_res)
			else:
				print("Error: Has no terms for Choice term.")
				exit()
		elif tree.leaf == '||':
			collection = []
			collection.append(tree.children[0].stmt)
			parallelism(collection,state,tree.children[1])
			return
		elif tree.leaf == '.':
			if tree.children:
				#print("\n--- Successfully find a state.")
				current_label = ast_trans2_qLTS(tree.children[0],current_state,tree.children[1].stmt,meas_res)
				bexpr = current_label[0]
				if current_bexpr is not None:
					if bexpr is True:
						bexpr = current_bexpr
					else:
						bexpr = simplify(And(current_bexpr,bexpr))
				if tree.children[0].type == 'Measurement':
					state += 1
					transition.append((current_state,state,bexpr,tau,current_label[2],meas_res.copy()))
					current_superoperator = snapshot[current_state]['combined superoperator']
					new_snapshot = { 'term': statement, 'superoperator': np.eye(2**len(regq)),
									 #'operation': np.eye(2**len(regq)), 
									 'combined superoperator': current_superoperator }
					snapshot.append(new_snapshot)
					#print("Branching")
					text = tree.children[0].leaf
					for i in range(len(text)):
						if text[i] == '[':
							break
					for j in range(len(text)):
						if text[j] == ';':
							break
					qbit = pd.read_csv(StringIO(text[i+1:j])).columns.tolist()
					cbit = pd.read_csv(StringIO(text[j+1:len(text)-1])).columns.tolist()
					current_state = state
					#分支为Set 0 Set 1等，由测量的qubit数决定
					#暂时不调整qubit的顺序,只在首尾张量I,同matrix_presentation()
					l = 2**len(qbit)
					for n in range(l):
						state += 1
						dic = {cbit[0] : n}
						meas_res.update(dic)
						transition.append((current_state,state,current_label[0],
											current_label[1]+"_"+str(n),'silent',meas_res.copy()))
						supop = np.zeros([l,l])
						supop[n,n] = 1
						supop = temp_method_for_building_superoperator(supop,qbit)
						res = np.kron(supop,supop.conjugate())
						#res = np.zeros([(2**len(regq))**2,(2**len(regq))**2])
						#for m in range(l):
						#	kraus = np.zeros([l,l])
						#	kraus[n,m] = 1
						#	kraus = temp_method_for_building_superoperator(kraus,qbit)
						#	kraus_mp = np.kron(kraus,kraus.conjugate())
						#	res = res + kraus_mp
						#pre = np.zeros([l,l])
						#pre[n,:] = 1
						#pre = temp_method_for_building_superoperator(pre,qbit)
						#res = np.kron(pre,pre)
						current_superoperator = snapshot[current_state]['combined superoperator']
						new_superoperator = np.dot(res,current_superoperator)
						new_snapshot = { 'term': tree.children[1].stmt, 'superoperator': supop,
										 #'operation': pre, 
										 'combined superoperator': new_superoperator }
						snapshot.append(new_snapshot)
						next_label = ast_trans2_qLTS(tree.children[1],state,tree.children[1].stmt,meas_res)
				elif tree.children[0].type == 'Superoperator':
					state += 1
					transition.append((current_state,state,bexpr,tau,current_label[2],meas_res.copy()))
					current_superoperator = snapshot[current_state]['combined superoperator']
					new_snapshot = { 'term': statement, 'superoperator': np.eye(2**len(regq)),
									 #'operation': np.eye(2**len(regq)), 
									 'combined superoperator': current_superoperator }
					snapshot.append(new_snapshot)
					current_state = state
					state += 1
					text = tree.children[0].leaf
					mat = matrix_presentation(text)
					res = np.kron(mat,mat.conjugate())
					res = np.around(res,decimals=3)
					current_superoperator = snapshot[current_state]['combined superoperator']
					new_superoperator = np.dot(res,current_superoperator)
					new_snapshot = { 'term': tree.children[1].stmt, 'superoperator': mat,
						 			 #'operation': mat, 
						 			 'combined superoperator': new_superoperator }
					snapshot.append(new_snapshot)
					transition.append((current_state,state,current_label[0],current_label[1],current_label[2],meas_res.copy()))
					next_label = ast_trans2_qLTS(tree.children[1],state,tree.children[1].stmt,meas_res)
				else:
					state += 1
					transition.append((current_state,state,bexpr,current_label[1],current_label[2],meas_res.copy()))
					next_label = ast_trans2_qLTS(tree.children[1],state,tree.children[1].stmt,meas_res)
				return (tt,next_label,current_label[2])
			else:
				print("Error: Has no terms for Prefix term.")
				exit()
		elif tree.leaf == 'def':
			if tree.children:
				#print("\n--- Successfully find a qLTS.")
				qLTS.append(constr_reg(tree.children[0].leaf))
				l = 2**len(regq)
				i = np.eye(l)
				mat = np.kron(i,i.conjugate())
				c = {}
				initial_snapshot = { 'term': tree.children[1].stmt, 'superoperator': i,
									 #'operation': i, 
									 'combined superoperator': mat }
				transition.clear()
				snapshot.clear()
				snapshot.append(initial_snapshot)
				state = 0
				meas_res = {}
				#pprint.pprint(snapshot)
				ast_trans2_qLTS(tree.children[1],current_state,tree.children[1].stmt,meas_res)
				#pprint.pprint(transition)
				s = snapshot.copy()
				t = transition.copy()
				snapshots.append(s)
				transitions.append(t)
				return
			else:
				print("Error: Has no terms for Define term.")
				exit()
	elif tree.type == 'Relabel':
		#print("\n--- Catch a relabel function: "+tree.leaf)
		return tree.leaf
	elif tree.type == 'IfThenElse':
		if tree.children:
			bexpr = parse_bexpr(tree.children[0],meas_res)
			ast_trans2_qLTS(tree.children[1],current_state,tree.children[1].stmt,meas_res,bexpr)
			return
		else:
			print("Error: Has no terms for IfThen term.")
			exit()
	elif tree.type == 'Term':
		if tree.children:
			ast_trans2_qLTS(tree.children[0],state,tree.children[0].stmt,meas_res)
			return
		else:
			print("Error: No terms in ().")
			exit()
	elif tree.type == 'Silent':
		l = 2**len(regq)
		mat = np.eye(l)
		current_superoperator = snapshot[state]['combined superoperator']
		new_snapshot = { 'term': statement, 'superoperator': mat,
						 #'operation': mat, 
						 'combined superoperator': current_superoperator }
		snapshot.append(new_snapshot)
		#print("Silent")
		return (tt,tau,"silent")
	elif tree.type == 'BinaryOpAct':
		l = 2**len(regq)
		mat = np.eye(l)
		current_superoperator = snapshot[state]['combined superoperator']
		new_snapshot = { 'term': statement, 'superoperator': mat,
						 #'operation': mat, 
						 'combined superoperator': current_superoperator }
		snapshot.append(new_snapshot)
		return (tt,tree.stmt,tree.leaf.lower())
	elif tree.type == 'Superoperator':
		#print("\n--- Catch a superoperator (quantum operation): "+tree.leaf)
		return (tt,tree.leaf,"silent")
	elif tree.type == 'Measurement':
		#print("\n--- Catch a measurement: "+tree.leaf)
		return (tt,tree.leaf,"silent")
	elif tree.type == 'Forbidden':
		ast_trans2_qLTS(tree.children[0],state,tree.children[0].stmt,meas_res)
		return
	elif tree.type == 'Name':
		return
	elif tree.type == 'BinaryOpExpr':
		#TODO
		return
	elif tree.type == 'NUMBER':
		return

def get_qubit(reg):
	return reg[1:len(reg)-1]

def qubit2number(qubit):
	n = 0
	i = len(qubit)-1
	for q in qubit:
		n += int(q)*(2**i)
		i = i-1
	return n

def expr2vector(expr):
	if expr.type == 'NoCoeff':
		q = get_qubit(expr.children[0].leaf)
		n = qubit2number(q)
		vec = np.zeros([2**len(q)],dtype=complex)
		vec[n] = 1
		return vec
	elif expr.type == 'Coeff':
		q = get_qubit(expr.children[1].leaf)
		n = qubit2number(q)
		vec = np.zeros([2**len(q)],dtype=complex)
		vec[n] = expr.children[0].leaf
		return vec
	elif expr.type == 'Negative':
		vec = expr2vector(expr.children[0])*(-1)
		return vec
	elif expr.type == 'BinaryOpExpr':
		if expr.leaf == '+':
			vec = expr2vector(expr.children[0])+expr2vector(expr.children[1])
			return vec
		elif expr.leaf == '-':
			vec = expr2vector(expr.children[0])-expr2vector(expr.children[1])
			return vec

def extract_info(tree):
	if tree.type == 'Info':
		print("Infomation.")
		if tree.children:
			extract_info(tree.children[0])
		return
	elif tree.type == 'Next Statements':
		#print("Several statements.")
		if tree.children:
			extract_info(tree.children[0])
			extract_info(tree.children[1])
		return
	elif tree.type == 'Mapping':
		#print("Find a map.")
		if tree.children:
			qubit = get_qubit(tree.children[1].leaf)
			d = 2**len(qubit)
			mat = np.zeros([d,d],dtype=complex)
			mat[:,qubit2number(qubit)]=expr2vector(tree.children[2])
			if op.__contains__(tree.children[0].leaf):
				op[tree.children[0].leaf]+=mat
			else:
				op[tree.children[0].leaf]=mat
		else:
			print("The map need parameters.")
		return
	else:
		print("Something went wrong...")
		return

def parallelism(collection,current_state,tree):
	if tree.leaf=="||":
		collection.append(tree.children[0].stmt)
		return parallelism(collection,current_state,tree.children[1])
	else:
		collection.append(tree.stmt)
		temp_transitions = []
		temp_snapshots = []
		for process_name in collection:
			qlts_index = [x for x in range(len(qLTS)) if qLTS[x] == process_name]
			if len(qlts_index)>1:
				print("Error: Reduplicate qLTS name.")
				exit(1)
			for x in qlts_index:
				temp_transitions.append(transitions[x])
				temp_snapshots.append(snapshots[x])
		parallel_member_number = len(temp_transitions)
		state_composition = (0,)*parallel_member_number
		print("Compose parallel components.")
		parallelism_trans2_qLTS(state_composition,current_state,temp_transitions,temp_snapshots)
	return

def parallelism_trans2_qLTS(state_composition,current_state,temp_transitions,temp_snapshots,meas_res={}):
	global state
	input_transitions = []
	output_transitions = []
	temp_action = []
	for i in range(len(state_composition)):
		state_index = state_composition[i]
		temp_transition = temp_transitions[i]
		next_transitions = [t for t in temp_transition if t[0] == state_index]
		for next_transition in next_transitions:
			current_action = next_transition[3]
			if next_transition[4] == "!" or next_transition[4] == ".!":
				for t in input_transitions:
					input_transition = t[0]
					matched_state_index = t[1]
					if match_action(input_transition[3],current_action):
						state += 1
						print("Comm: ",input_transition[3],current_action)
						new_meas_res = meas_res.copy()
						new_meas_res.update(next_transition[5])
						new_meas_res.update(input_transition[5])
						assertion = And(bool(next_transition[2]),bool(input_transition[2]))
						for m in new_meas_res:
							assertion = substitute(assertion,(Real(m),RealVal(meas_res[m])))
						transition.append((current_state,state,simplify(assertion),tau,'matched',new_meas_res.copy()))
						if i < matched_state_index:
							new_state_composition = state_composition[0:i]+(next_transition[1],)+state_composition[i+1:matched_state_index]+(input_transition[1],)+state_composition[matched_state_index+1:]
						else:
							new_state_composition = state_composition[0:matched_state_index]+(input_transition[1],)+state_composition[matched_state_index+1:i]+(next_transition[1],)+state_composition[i+1:]
						#temp_transitions[i].remove(next_transition)
						#if not temp_transitions[i]:
						#	temp_transitions.remove(temp_transitions[i])
						statement = gen_parallel_stmt(snapshots,new_state_composition)
						mat = np.eye(2**len(regq))
						current_superoperator = snapshot[current_state]['combined superoperator']
						new_snapshot = { 'term': statement, 'superoperator': mat, 
										 #'operation': mat, 
										 'combined superoperator': current_superoperator }
						snapshot.append(new_snapshot)
						parallelism_trans2_qLTS(new_state_composition,state,temp_transitions,temp_snapshots,new_meas_res)
						return
				output_transitions.append((next_transition,i))
				temp_action.append((next_transition,i))
			elif next_transition[4] == "?"  or next_transition[4] == ".?":
				for t in output_transitions:
					output_transition = t[0]
					matched_state_index = t[1]
					if match_action(current_action,output_transition[3]):
						state += 1
						print("Comm: ",current_action,output_transition[3])
						new_meas_res = meas_res.copy()
						new_meas_res.update(next_transition[5])
						new_meas_res.update(output_transition[5])
						assertion = And(bool(next_transition[2]),bool(output_transition[2]))
						for m in meas_res:
							assertion = substitute(assertion,(Real(m),RealVal(meas_res[m])))
						transition.append((current_state,state,simplify(assertion),tau,'matched',new_meas_res.copy()))
						if i < matched_state_index:
							new_state_composition = state_composition[0:i]+(next_transition[1],)+state_composition[i+1:matched_state_index]+(output_transition[1],)+state_composition[matched_state_index+1:]
						else:
							new_state_composition = state_composition[0:matched_state_index]+(output_transition[1],)+state_composition[matched_state_index+1:i]+(next_transition[1],)+state_composition[i+1:]
						#temp_transitions[i].remove(next_transition)
						#if not temp_transitions[i]:
						#	temp_transitions.remove(temp_transitions[i])
						statement = gen_parallel_stmt(snapshots,new_state_composition)
						mat = np.eye(2**len(regq))
						current_superoperator = snapshot[current_state]['combined superoperator']
						new_snapshot = { 'term': statement, 'superoperator': mat, 
										 #'operation': mat, 
										 'combined superoperator': current_superoperator }
						snapshot.append(new_snapshot)
						parallelism_trans2_qLTS(new_state_composition,state,temp_transitions,temp_snapshots,new_meas_res)
						return
				input_transitions.append((next_transition,i))
				temp_action.append((next_transition,i))
			else:
				temp_action.append((next_transition,i))
	#pprint.pprint(temp_action)
	have_next_step = False
	for n in temp_action:
		next_action = n[0]
		if next_action[4] == "kraus" or next_action[4] == "silent":
			have_next_step = True
			state += 1
			print(next_action)
			meas_res.update(next_action[5])
			assertion = And(next_action[2],True)
			for m in meas_res:
				assertion = substitute(assertion,(Real(m),RealVal(meas_res[m])))
			transition.append((current_state,state,simplify(assertion),next_action[3],next_action[4],meas_res.copy()))
			new_state_composition = state_composition[0:n[1]]+(next_action[1],)+state_composition[n[1]+1:]
			statement = gen_parallel_stmt(snapshots,new_state_composition)
			sn = snapshots[n[1]][next_action[1]]
			mat = sn['superoperator']
			res = np.kron(mat,mat.conjugate())
			#pre = sn['operation']
			#res = np.kron(pre,pre.conjugate())
			res = np.around(res,decimals=3)
			current_superoperator = snapshot[current_state]['combined superoperator']
			new_superoperator = np.dot(res,current_superoperator)
			new_snapshot = { 'term': statement, 'superoperator': mat, 
							 #'operation': pre, 
							 'combined superoperator': new_superoperator }
			snapshot.append(new_snapshot)
			#temp_action.remove(n)
			#if not temp_transitions[i]:
			#	temp_transitions.remove(temp_transitions[i])
			parallelism_trans2_qLTS(new_state_composition,state,temp_transitions,temp_snapshots,meas_res)
	if (not have_next_step) and temp_action:
		#TODO
		#遍历所有组合
		next_action = temp_action[0][0]
		state += 1
		print(next_action)
		meas_res.update(next_action[5])
		assertion = And(next_action[2],True)
		for m in meas_res:
			assertion = substitute(assertion,(Real(m),RealVal(meas_res[m])))
		transition.append((current_state,state,simplify(assertion),next_action[3],next_action[4],meas_res.copy()))
		new_state_composition = state_composition[0:temp_action[0][1]]+(next_action[1],)+state_composition[temp_action[0][1]+1:]
		statement = gen_parallel_stmt(snapshots,new_state_composition)
		sn = snapshots[n[1]][next_action[1]]
		mat = sn['superoperator']
		res = np.kron(mat,mat.conjugate())
		#pre = sn['operation']
		#res = np.kron(pre,pre.conjugate())
		res = np.around(res,decimals=3)
		current_superoperator = snapshot[current_state]['combined superoperator']
		new_superoperator = np.dot(res,current_superoperator)
		new_snapshot = { 'term': statement, 'superoperator': mat, 
						 #'operation': pre, 
						 'combined superoperator': new_superoperator }
		snapshot.append(new_snapshot)
		#temp_action.remove(temp_action[0])
		#if not temp_transitions[i]:
		#	temp_transitions.remove(temp_transitions[i])
		parallelism_trans2_qLTS(new_state_composition,state,temp_transitions,temp_snapshots,meas_res)
	return

def match_action(input_action,output_action):
	input_action = input_action.strip()
	output_action = output_action.strip()
	begin = 0
	end = 0
	channel_begin = begin
	channel_end = end
	variable_begin = begin
	variable_end = end
	input_channel = "ch_in"
	output_channel = "chi_out"
	input_variable = "var_in"
	output_variable = "var_out"
	for i in range(len(input_action)):
		if input_action[i] == '?':
			channel_end = i
			variable_begin = i+1
			variable_end = len(input_action)
			if (channel_end > channel_begin) and (variable_end > variable_begin):
				input_channel = input_action[channel_begin:channel_end]
				input_variable = input_action[variable_begin:variable_end]
			else:
				print("Error: Syntax error in Input action.")
	for i in range(len(output_action)):
		if output_action[i] == '!':
			channel_end = i
			variable_begin = i+1
			variable_end = len(output_action)
			if (channel_end > channel_begin) and (variable_end > variable_begin):
				output_channel = output_action[channel_begin:channel_end]
				output_variable = output_action[variable_begin:variable_end]
			else:
				print("Error: Syntax error in Output action.")
	return (input_channel==output_channel) and (input_variable==output_variable)

def gen_parallel_stmt(snapshots,state_composition):
	s = state_composition[0]
	sn = snapshots[0][s]
	statement = sn['term']
	for i in range(1,len(state_composition)):
		s = state_composition[i]
		sn = snapshots[i][s]
		statement = statement+"||"+sn['term']
	return statement