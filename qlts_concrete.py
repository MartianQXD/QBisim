from q_ast_concrete import lexer
from parser_concrete import parser
from info_parser_concrete import info_parser
from init_parser import init_parser
from graphviz import Digraph
from io import StringIO
from z3 import *
import pprint
import numpy as np
import numpy.matlib
import pandas as pd
import gc
import math

# Restore the name of operators by dict(Hashmap).
# Construct the matrix according to the maps and restore them.
op = {}
meas = {}
# qLTS
qLTS = []
transitions = []
snapshots = []
# Restore the states and transitions of qLTSs by list.
initial_state = {}
transition = []
snapshot = []
# Register
regx = []
regq = []
# Just the initial state of the register
regx_val = {}
regq_val = []
mat_size = 0
# S
state = 0
# t
statement = ""
# Reserved words
tt = True
ff = False
tau = "tau"
# Parameters for BB84
n = 1
# Accuracy
accuracy = 6
accuracy2 = 2

def qlts(inputfile, outputfile):
    f = open(inputfile, 'r')
    data = f.read()
    global state
    global statement
    lexer.input(data)
    for tok in lexer:
        tp = tok.type
        value = tok.value
        line = tok.lineno
        pos = tok.lexpos
        # print(tok.type, tok.value, tok.lineno, tok.lexpos)
    init = data[0:lexer.init_end]
    prog = data[lexer.init_end+1:lexer.info_start-2]
    operator = data[lexer.info_start-1:lexer.info_end]
    # print(str(lexer.init_end))
    # print(str(lexer.info_start))
    # print(str(lexer.info_end))
    # print("\nProgram: "+prog)
    # print("\nVariable Initialization: "+init)
    # print("\n======================Variable Initialization.======================")
    init_result = init_parser.parse(init)
    # tree_print(init_result)
    init_reg(init_result)
    # print("\nRegister: ",regx,regx_val,regq,regq_val)
    global mat_size
    mat_size = 2**len(regq)
    # print("\nOperator Infomation: "+operator)
    # print("\n======================Operator Infomation.======================")
    info_result = info_parser.parse(operator)
    # tree_print(info_result)
    extract_info(info_result)
    # print("\n======================Start Constructing Graph.======================")
    # 创建parser
    result = parser.parse(prog)
    # tree_print(result)
    meas_res = {}
    ast_trans2_qLTS(result, state, statement, regx_val)
    # print("\n======================        Finished.        ======================")
    # pprint.pprint(qLTS)
    # pprint.pprint(transitions)
    # pprint.pprint(regx)
    # pprint.pprint(regq)
    # pprint.pprint(op)
    # pprint.pprint(snapshot)
    # 画图
    # qLTS_index = len(qLTS)-1
    # dot = Digraph(comment="The qLTS "+qLTS[qLTS_index][0])
    # dot.attr('node', fontsize='35')
    # dot.attr('edge', fontsize='40')
    # t = transitions[qLTS_index]
    # for transition in t:
    #     if len(transition) > 2:
    #         dot.edge(str(transition[0]), str(
    #             transition[1]), str(transition[2]))
    #     else:
    #         dot.edge(str(transition[0]), str(transition[1]))
    # print(dot.source)
    # s = snapshots[qLTS_index]
    # for i in range(len(s)):
    # 	print("State "+str(i))
    # 	pprint.pprint(s[i])
    # 	i = i+1
    # 保存结果
    # dot.render(outputfile, view=False)


def tree_print(tree):
    print("ID", id(tree), ":")
    print(tree.type, " ", tree.leaf, end=' ')
    print("Next:", end=' ')
    if tree.children:
        for child in tree.children:
            print(id(child), end=' ')
        for child in tree.children:
            print("")
            tree_print(child)


def parse_bexpr(tree, evaluation):
    if tree.type == 'BinaryOpExpr':
        left = parse_bexpr(tree.children[0], evaluation)
        if left == None:
            return None
        right = parse_bexpr(tree.children[1], evaluation)
        if right == None:
            return None
        # print(left,right)
        if tree.leaf == '=':
            assertion = (left == right)
        elif tree.leaf == '+':
            assertion = (left+right)
        elif tree.leaf == '-':
            assertion = (left-right)
        elif tree.leaf == '*':
            assertion = (left*right)
        elif tree.leaf == 'and':
            assertion = (left and right)
        elif tree.leaf == 'or':
            assertion = (left or right)
        elif tree.leaf == '>=':
            assertion = (left >= right)
        elif tree.leaf == '<=':
            assertion = (left <= right)
        elif tree.leaf == '>':
            assertion = (left > right)
        elif tree.leaf == '<':
            assertion = (left < right)
        # print(assertion)
        return assertion
    elif tree.type == 'UnaryOpExpr':
        if tree.leaf == 'not':
            assertion = not (parse_bexpr(tree.children[0], evaluation))
        return assertion
    elif tree.type == 'Expression':
        if tree.children:
            assertion = parse_bexpr(tree.children[0], evaluation)
            return assertion
        else:
            print("Error: No terms in ().")
            return None
    elif tree.type == 'Sub':
        assertion = sub_function(tree, evaluation)
        return assertion
    elif tree.type == 'CMP':
        assertion = cmp_function(tree, evaluation)
        return assertion
    elif tree.type == 'XOR':
        assertion = xor_function(tree, evaluation)
        return assertion
    else:
        if evaluation.__contains__(tree.leaf):
            return evaluation[tree.leaf]
        elif type(tree.leaf) is int:
            return tree.leaf
        else:
            return None


def get_process_name(process):
    process = process.strip()
    name_end = len(process)
    begin = 0
    end = 0
    for i in range(len(process)):
        if process[i] == '(':
            begin = i
            name_end = begin
        if process[i] == ')':
            end = i
    return process[0:name_end]


def check_unitary(mat):
    l = len(mat)
    # print(mat)
    # pprint.pprint(np.dot(mat,mat.conjugate().transpose()))
    matH = mat.conjugate().transpose()
    res = np.dot(mat, matH)
    if (res == np.eye(l)).all():
        # pprint.pprint(res)
        return
    else:
        print("Error: Matrix is not unitary.")
        exit(1)

# Do not reorder the qubits, tensor I on both sides only.


def matrix_presentation(superoperator):
    for i in range(len(superoperator)):
        if superoperator[i] == '[':
            break
    name = superoperator[0:i]
    mat = op[name]
    text = superoperator[i+1:len(superoperator)-1]
    reg = pd.read_csv(StringIO(text)).columns.tolist()
    #print(str(reg)+" transformed by matrix: ")
    res = temp_method_for_building_superoperator(mat, reg)
    return res

# Do not reorder the qubits, tensor I on both sides only.


def temp_method_for_building_superoperator(mat, reg):
    # print(mat,reg)
    r = []
    res = []
    l = len(reg)
    lq = len(regq) - len(reg)
    for m in mat:
        if lq == 0:
            res = np.around(m, decimals=accuracy)
            r.append(res)
        elif lq > 0:
            lq_left = 0
            lq_right = 0
            for q in regq:
                if q == reg[0]:
                    lq_left = regq.index(q)
                    lq_right = lq-lq_left
                    break
            if lq_left > 0:
                m = np.kron(np.eye(2**lq_left), m)
            if lq_right > 0:
                m = np.kron(m, np.eye(2**lq_right))
            res = np.around(m, decimals=accuracy)
            r.append(res)
        elif lq < 0:
            print("Error: Too many qubit used much more than the register.")
            exit(1)
    return r

# Normalize the result matrix of the measurement
# If its trace is 0, that just means the probability getting it is 0, return itself without doing anything


def normalize(s):
    global mat_size
    # print("---------")
    # print(s)
    # print("---------")
    new_s = np.zeros((mat_size, mat_size))
    trace(s)
    #print("Trace: ",trace)
    if trace == 0:
        print("Can not normalize the superoperator. Trace is 0.")
        new_s = s
    else:
        ss = (1/trace)
        new_s = s*ss
    return new_s


def trace(s):
    trace = 0.0
    for i in range(mat_size):
        trace = trace+abs(s[i, i])
    return round(trace, 3)


def ast_trans2_qLTS(tree, current_state, statement, evaluation):
    global state
    # print(evaluation)
    if tree.type == 'NULL':
        #print("\n--- End of the sequencial process.")
        return (tree.leaf)
    # 新添加运算符Next，帮助Parallel的描述
    elif tree.type == 'Next':
        state = 0
        ast_trans2_qLTS(tree.children[0], state,
                        tree.children[0].stmt, evaluation)
        state = 0
        ast_trans2_qLTS(tree.children[1], state,
                        tree.children[1].stmt, evaluation)
        return
    elif tree.type == 'BinaryOpProc':
        if tree.leaf == '+':
            if tree.children:
                # print("Branching")
                ast_trans2_qLTS(
                    tree.children[0], current_state, tree.children[0].stmt, evaluation)
                ast_trans2_qLTS(
                    tree.children[1], current_state, tree.children[1].stmt, evaluation)
            else:
                print("Error: Has no terms for Choice term.")
                exit()
        elif tree.leaf == '||':
            collection = []
            collection.append(tree.children[0].stmt)
            parallelism(collection, state, tree.children[1], evaluation)
            return
        elif tree.leaf == '.':
            if tree.children:
                #print("\n--- Successfully find a state.")
                current_label = ast_trans2_qLTS(
                    tree.children[0], current_state, tree.children[1].stmt, evaluation)
                if tree.children[0].type == 'Measurement':
                    state = state+1
                    transition.append(
                        (current_state, state, tau, "measurement", evaluation))
                    add_slilent_SN(current_state, statement, 'silent')
                    current_state = state
                    # print("Branching")
                    text = tree.children[0].leaf
                    for i in range(len(text)):
                        if text[i] == '[':
                            break
                    for j in range(len(text)):
                        if text[j] == ';':
                            break
                    qbit = pd.read_csv(StringIO(text[i+1:j])).columns.tolist()
                    cbit = pd.read_csv(
                        StringIO(text[j+1:len(text)-1])).columns.tolist()
                    # Branch is dicide by the qubits measured (exactly 2^n).
                    # The order of the qubits won't be organized,
                    # only tesor I before or after the qubits instead,
                    # as what matrix_presentation() done.
                    name = text[0:i]
                    measurement = meas[name]
                    measurement = temp_method_for_building_superoperator(
                        measurement, qbit)
                    n = 0
                    for m in measurement:
                        current_superoperator = snapshot[current_state]['density operator']
                        new_superoperator = np.dot(
                            np.dot(m, current_superoperator), m)
                        new_superoperator = np.around(
                            new_superoperator, decimals=accuracy)
                        prob = round(trace(new_superoperator), accuracy2)
                        #print("Trace: ",trace)
                        if prob == 0:
                            flag_tr = 0
                            # print("Can not normalize the superoperator. Trace is 0.")
                        else:
                            state = state+1
                            new_evaluation = {}
                            new_evaluation.update(evaluation)
                            ss = (1/prob)
                            new_superoperator = new_superoperator*ss
                            dic = {cbit[0]: n}
                            new_evaluation.update(dic)
                            new_snapshot = {'term': tree.children[1].stmt,  # 'probability': prob,
                                            'kraus operator': m,
                                            'density operator': new_superoperator,
                                            'action name': name}
                            snapshot.append(new_snapshot)
                            transition.append((current_state, state,  # "p"+str(int(n))+"="+str(prob)
                                               prob, 'measurement'))
                            next_label = ast_trans2_qLTS(
                                tree.children[1], state, tree.children[1].stmt, new_evaluation)
                        n = n+1
                elif tree.children[0].type == 'Superoperator':
                    state += 1
                    transition.append(
                        (current_state, state, tau, current_label[1], evaluation))
                    add_slilent_SN(current_state, statement, 'silent')
                    current_state = state
                    text = tree.children[0].leaf
                    mat = matrix_presentation(text)
                    current_operator = snapshot[current_state]['density operator']
                    new_operator = np.zeros((mat_size, mat_size))
                    for m in mat:
                        new_operator = new_operator + \
                            np.dot(np.dot(m, current_operator),
                                   m.conjugate().transpose())
                        new_operator = np.around(new_operator, decimals=accuracy)
                    prob = round(trace(new_operator), accuracy2)
                    state += 1
                    new_snapshot = {'term': tree.children[1].stmt,  # 'probability': prob,
                                    'kraus operator': mat,
                                    'density operator': new_operator,
                                    'action name': text}
                    snapshot.append(new_snapshot)
                    transition.append((current_state, state,  # "p="+str(prob)
                                       prob, current_label[1], evaluation))
                    next_label = ast_trans2_qLTS(
                        tree.children[1], state, tree.children[1].stmt, evaluation)
                elif tree.children[0].type == 'Ran':
                    state = state+1
                    transition.append(
                        (current_state, state, tau, "measurement", evaluation))
                    add_slilent_SN(current_state, statement, 'silent')
                    current_state = state
                    process = tree.children[0].leaf
                    para = []
                    count = 0
                    for i in range(len(process)):
                        if process[i] == '[':
                            begin = i
                        if process[i] == ',':
                            end = i
                            name = process[begin+1:end]
                            para.append(name)
                            count = count+1
                            begin = end
                        if process[i] == ']':
                            end = i
                        if count > 3:
                            break
                    if end >= len(process)-1:
                        name = process[begin+1:end]
                        para.append(name)
                    result = ''
                    qubit = {}
                    for name in para:
                        if name in evaluation.keys():
                            qubit.update(
                                {name: number2qubit(evaluation[name])})
                    n = len(qubit[para[2]])
                    for i in range(n):
                        if qubit[para[0]][i] == qubit[para[1]][i]:
                            result = result+str(qubit[para[2]][i])
                    if len(result) == 0:
                        result = ''
                    matched_len = len(result)
                    not_matched_len = n-matched_len
                    # print("=========",qubit,result)
                    for i in range(2**not_matched_len):
                        new_evaluation = evaluation
                        if len(result) != 0:
                            dic = {para[3]: result}
                        else:
                            dic = {para[3]: i}
                        new_evaluation.update(dic)
                        mat = [np.eye(mat_size)]
                        current_operator = snapshot[current_state]['density operator']
                        state += 1
                        new_snapshot = {'term': tree.children[1].stmt,  # 'probability': 0.5,
                                        'kraus operator': mat,
                                        'density operator': current_operator,
                                        'action name': process}
                        snapshot.append(new_snapshot)
                        transition.append((current_state, state,  # "p="+str(1/(2**not_matched_len))
                                           1/(2**not_matched_len), current_label[1], new_evaluation))
                        next_label = ast_trans2_qLTS(
                            tree.children[1], state, tree.children[1].stmt, new_evaluation)
                elif tree.children[0].type == 'Pstr':
                    text = tree.children[0].leaf
                    for i in range(len(text)):
                        if text[i] == '[':
                            break
                    for j in range(len(text)):
                        if text[j] == ';':
                            break
                    qbit = pd.read_csv(StringIO(text[i+1:j])).columns.tolist()
                    cbit = pd.read_csv(
                        StringIO(text[j+1:len(text)-1])).columns.tolist()
                    n = 2**len(qbit)-1
                    dic = {cbit[0]: n}
                    evaluation.update(dic)
                    state += 1
                    transition.append(
                        (current_state, state, tau, current_label[1], evaluation))
                    add_slilent_SN(current_state, statement, 'silent')
                    next_label = ast_trans2_qLTS(
                        tree.children[1], state, tree.children[1].stmt, evaluation)
                else:
                    state += 1
                    transition.append(
                        (current_state, state, current_label[0], current_label[1], evaluation.copy()))
                    next_label = ast_trans2_qLTS(
                        tree.children[1], state, tree.children[1].stmt, evaluation)
                return (next_label, current_label[1])
            else:
                print("Error: Has no terms for Prefix term.")
                exit()
        elif tree.leaf == 'def':
            global regx_val
            if tree.children:
                #print("\n--- Successfully find a qLTS.")
                qLTS.append(
                    (get_process_name(tree.children[0].leaf), tree.children[1]))
                # Here is different from the non-concrete one,
                # the initial mat is outer product of initial regq
                i = [np.eye(mat_size)]
                qubit = regq_val
                mat = np.dot(qubit, qubit.conjugate().transpose())
                mat = np.around(mat, decimals=accuracy)
                initial_state = {'term': tree.children[1].stmt,  # 'probability': 1,
                                 'kraus operator': i,
                                 'density operator': mat,
                                 'action name': 'def'}
                transition.clear()
                snapshot.clear()
                snapshot.append(initial_state)
                state = 0
                # pprint.pprint(snapshot)
                ast_trans2_qLTS(
                    tree.children[1], current_state, tree.children[1].stmt, regx_val.copy())
                # pprint.pprint(transition)
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
            bexpr = parse_bexpr(tree.children[0], evaluation)
            if tree.children[0].children[0].type == 'CMP' and tree.children[0].children[1].type == 'CMP':
                evaluation.update(cmp_function2(
                    tree.children[0].children[0], evaluation))
                evaluation.update(cmp_function2(
                    tree.children[0].children[1], evaluation))
            #print("Boolean expression: ",bexpr)
            if (bexpr == None) or (bexpr == False):
                return
            else:
                ast_trans2_qLTS(
                    tree.children[1], current_state, tree.children[1].stmt, evaluation)
            return
        else:
            print("Error: Has no terms for IfThen term.")
            exit()
    elif tree.type == 'Term':
        if tree.children:
            ast_trans2_qLTS(tree.children[0], state,
                            tree.children[0].stmt, evaluation)
            return
        else:
            print("Error: No terms in ().")
            exit()
    elif tree.type == 'Silent':
        add_slilent_SN(state, statement, 'silent')
        # print("Silent")
        return (tau, "silent")
    elif tree.type == 'BinaryOpAct':
        new_stmt = tree.stmt
        if tree.leaf == '!':
            if tree.children[1].type == 'CMP':
                result = cmp_function(tree.children[1], evaluation)
                new_stmt = tree.children[0].stmt+tree.leaf+result
            elif tree.children[1].type == 'Sub':
                result = sub_function(tree.children[1], evaluation)
                new_stmt = tree.children[0].stmt+tree.leaf+result
            elif tree.children[1].type == 'Rem':
                result = rem_function(tree.children[1], evaluation)
                new_stmt = tree.children[0].stmt+tree.leaf+result
            elif tree.children[1].type == 'XOR':
                result = xor_function(tree.children[1], evaluation)
                new_stmt = tree.children[0].stmt+tree.leaf+result
            else:
                result = ''
                if tree.children[1].leaf in evaluation.keys():
                    result = str(evaluation[tree.children[1].leaf])
                else:
                    result = tree.children[1].leaf
                new_stmt = tree.children[0].stmt+tree.leaf+result
        add_slilent_SN(state, statement, tree.leaf)
        return (new_stmt, tree.leaf.lower())
    elif tree.type == 'Superoperator':
        #print("\n--- Catch a superoperator (quantum operation): "+tree.leaf)
        return (tree.leaf, "operation")
    elif tree.type == 'Measurement':
        #print("\n--- Catch a measurement: "+tree.leaf)
        return (tree.leaf, "measurement")
    elif tree.type == 'Pstr':
        # print("Pstr")
        return (tree.leaf, "silent")
    elif tree.type == 'Ran':
        # print("Pstr")
        return (tree.leaf, "silent")
    elif tree.type == 'Forbidden':
        ast_trans2_qLTS(tree.children[0], state,
                        tree.children[0].stmt, evaluation)
        return
    elif tree.type == 'Name':
        return
    elif tree.type == 'BinaryOpExpr':
        # TODO
        return
    elif tree.type == 'NUMBER':
        return


def get_kraus(expr):
    kraus = []
    if expr.type == 'SINGLE':
        kraus.append(expr2mat(expr.children[0]))
    elif expr.type == 'COMMA':
        kraus.append(expr2mat(expr.children[0]))
        kraus.extend(get_kraus(expr.children[1]))
    return kraus


def get_outer_product(expr):
    if expr.type == 'Kraus':
        process = expr.leaf.strip()
        left_begin = 0
        left_end = 0
        right_begin = 0
        right_end = 0
        left = ""
        right = ""
        for i in range(len(process)):
            if process[i] == '|':
                left_begin = i
                right_end = i
            if process[i] == '>':
                left_end = i
                left = process[left_begin+1:left_end].strip()
            if process[i] == '<':
                right_begin = i
        right = process[right_begin+1:right_end].strip()
        if len(left) != len(right):
            print("Error Kraus operator (length not equal).")
            exit(1)
        dem = 2**len(left)
        n = qubit2number(left)
        m = qubit2number(right)
        vec = np.zeros((dem, 1))
        vec_d = np.zeros((1, dem))
        vec[n, 0] = 1
        vec_d[0, m] = 1
        result = np.dot(vec, vec_d)
        return result
    else:
        print("Error Kraus operator.")
        exit(1)


def get_qubit(reg):
    return reg[1:len(reg)-1]


def qubit2number(qubit):
    n = 0
    i = len(qubit)-1
    for q in qubit:
        n += int(q)*(2**i)
        i = i-1
    return n


def number2qubit(number):
    fmt = '{:0'+str(n)+'b}'
    return fmt.format(int(number))


def expr2mat(expr):
    if expr.type == 'NoCoeff':
        mat = get_outer_product(expr.children[0])
        return mat
    elif expr.type == 'Coeff':
        mat = get_outer_product(expr.children[1])
        c = complex(expr.children[0].leaf)
        mat = c*mat
        return mat
    elif expr.type == 'Negative':
        mat = expr2mat(expr.children[0])*(-1)
        return mat
    elif expr.type == 'BinaryOpExpr':
        if expr.leaf == '+':
            mat = expr2mat(expr.children[0])+expr2mat(expr.children[1])
            return mat
        elif expr.leaf == '-':
            mat = expr2mat(expr.children[0])-expr2mat(expr.children[1])
            return mat


def expr2vector(expr):
    if expr.type == 'NoCoeff':
        q = get_qubit(expr.children[0].leaf)
        n = qubit2number(q)
        vec = np.zeros([2**len(q)], dtype=complex)
        vec[n] = 1
        return vec
    elif expr.type == 'Coeff':
        q = get_qubit(expr.children[1].leaf)
        n = qubit2number(q)
        vec = np.zeros([2**len(q)], dtype=complex)
        vec[n] = complex(expr.children[0].leaf)
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
        # print("Infomation.")
        if tree.children:
            extract_info(tree.children[0])
        return
    elif tree.type == 'Next Statements':
        #print("Several statements.")
        if tree.children:
            extract_info(tree.children[0])
            extract_info(tree.children[1])
        return
    elif tree.type == 'EQUAL':
        #print("Find a map.")
        if tree.children:
            kraus = get_kraus(tree.children[1])
            if tree.children[0].leaf not in op.keys():
                kraus_list = kraus
                op[tree.children[0].leaf] = kraus_list
            else:
                kraus_list = op[tree.children[0].leaf]
                kraus_list = kraus_list.extend(kraus)
                op[tree.children[0].leaf] = kraus_list
        else:
            print("Need parameters.")
        return
    elif tree.type == 'MEQUAL':
        #print("Find a map.")
        if tree.children:
            kraus = get_kraus(tree.children[1])
            if tree.children[0].leaf not in meas.keys():
                kraus_list = kraus
                meas[tree.children[0].leaf] = kraus_list
            else:
                kraus_list = meas[tree.children[0].leaf]
                kraus_list = kraus_list.extend(kraus)
                meas[tree.children[0].leaf] = kraus_list
        else:
            print("Need parameters.")
        return
    else:
        print("Something went wrong...")
        return


def constr_reg(process):
    process = process.strip()
    word_begin = 0
    word_end = len(process)-1
    val_begin = -1
    val_end = -1
    for i in range(len(process)):
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
                    print(
                        "Error: the register element should be x (classical bit) or q (quantum bit).")
                word_begin = len(process)
            else:
                print("Error: Syntax error in Process ID.")
    if word_begin < len(process):
        if process[word_begin] == 'x':
            bit_name = process[word_begin:len(process)-1].strip()
            if not (regx.__contains__(bit_name)):
                regx.append(bit_name)
        elif process[word_begin] == 'q':
            qbit_name = process[word_begin:len(process)-1].strip()
            if not (regq.__contains__(qbit_name)):
                regq.append(qbit_name)
        else:
            print(
                "Error: the register element should be x (classical bit) or q (quantum bit).")
    return process


def constr_eval(tree):
    evaluation = []
    if tree.type == 'Assignment':
        process = tree.leaf[1:len(tree.leaf)-1].strip()
        word_begin = 0
        word_end = len(process)
        regx_index = 0
        for i in range(len(process)):
            if process[i] == ',':
                new_val = int(process[word_begin:i])
                evaluation.append(new_val)
                regx_val.update({regx[regx_index]: new_val})
                regx_index = regx_index+1
                word_begin = i+1
        new_val = int(process[word_begin:word_end])
        if new_val is not None:
            evaluation.append(new_val)
            regx_val.update({regx[regx_index]: new_val})
    return evaluation


def constr_vector(tree):
    global regq_val
    mat = expr2vector(tree)
    matH = mat.reshape(len(mat), 1)
    if regq_val:
        regq_val += matH
    else:
        regq_val = matH
    return matH


def init_reg(tree):
    if tree.type == 'Init':
        # print("Initialization.")
        if tree.children:
            init_reg(tree.children[0])
        return
    elif tree.type == 'Next Statements':
        #print("Several statements.")
        if tree.children:
            init_reg(tree.children[0])
            init_reg(tree.children[1])
        return
    elif tree.type == 'EQUAL':
        #print("Find an initialization of classical/quantum variables.")
        if tree.children:
            # Build qubits register and give them value
            result = constr_reg(tree.children[0].leaf)
            if tree.children[0].type == 'CRegister':
                evaluation = constr_eval(tree.children[1])
            elif tree.children[0].type == 'QRegister':
                evaluation = constr_vector(tree.children[1])
            # print("Construct register: ",result)
        return
    elif tree.type == 'SINGLE':
        #print("Find the register.")
        # Build qubits register only
        result = constr_reg(tree.children[0].leaf)
        #print("Construct register: ",result)
        return
    return


def parallelism(collection, current_state, tree, evaluation):
    if tree.leaf == "||":
        collection.append(tree.children[0].stmt)
        return parallelism(collection, current_state, tree.children[1], evaluation)
    else:
        collection.append(tree.stmt)
        temp_components = []
        for process_name in collection:
            qlts_index = [x for x in range(
                len(qLTS)) if qLTS[x][0] == process_name]
            if len(qlts_index) > 1:
                print("Error: Reduplicate qLTS name.")
                exit(1)
            for x in qlts_index:
                temp_components.append(qLTS[x][1])
        # print("Compose parallel components.")
        parallelism_trans2_qLTS(temp_components, current_state, evaluation)
    return


def next_act(components, evaluation):
    acts = []
    for component in components:
        acts.append(get_act(component, evaluation))
    return acts


def get_act(component, evaluation):
    acts = []
    if component.leaf == '.':
        acts.append(component)
    elif component.leaf == '+':
        acts = get_act(component.children[0], evaluation)
        acts.extend(get_act(component.children[1], evaluation))
    elif component.type == 'NULL':
        acts.append(None)
    elif component.type == 'Term':
        acts = get_act(component.children[0], evaluation)
    elif component.type == 'IfThenElse':
        # print(component.children[0].stmt,evaluation)
        bexpr = parse_bexpr(component.children[0], evaluation)
        #print("Boolean expression: ",bexpr)
        if (bexpr != None) and (bexpr != False):
            acts = get_act(component.children[1], evaluation)
    else:
        print("Error: Syntax error.")
    return acts


def contains_act(acts, act):
    for a in acts:
        if contains_act_(a, act) == True:
            return True
    return False

# From elements from act list


def contains_act_(a, act):
    for aa in a:
        if aa is None:
            break
        if aa.children[0].leaf == act:
            return True
    return False


def have_matched(acts):
    input_act_pos = [t for t in range(
        len(acts)) if contains_act_(acts[t], '?') == True]
    output_act_pos = [t for t in range(
        len(acts)) if contains_act_(acts[t], '!') == True]
    for i in input_act_pos:
        for o in output_act_pos:
            if i == o:
                break
            for action1 in acts[i]:
                for action2 in acts[o]:
                    if match_action(action1.children[0], action2.children[0]):
                        return True
    input_act_pos = [t for t in range(
        len(acts)) if contains_act_(acts[t], '.?') == True]
    output_act_pos = [t for t in range(
        len(acts)) if contains_act_(acts[t], '.!') == True]
    for i in input_act_pos:
        for o in output_act_pos:
            if i == o:
                break
            for action1 in acts[i]:
                for action2 in acts[o]:
                    if match_action(action1.children[0], action2.children[0]):
                        return True
    return False


def update_components1(a, action, components):
    new_components = components.copy()
    new_components[a] = action.children[1]
    return new_components


def update_components2(i, o, action1, action2, components):
    new_components = components.copy()
    if match_action(action1.children[0], action2.children[0]):
        new_components[i] = action1.children[1]
        new_components[o] = action2.children[1]
    else:
        new_components = None
    return new_components


def update_variable(action1, action2, evaluation):
    if match_action(action1.children[0], action2.children[0]):
        input_action = action1.children[0]
        output_action = action2.children[0]
        # print(input_action.stmt,output_action.stmt)
        input_variable = input_action.children[1]
        output_value = output_action.children[1]
        result = ''
        if output_value.leaf in evaluation.keys():
            result = evaluation[output_value.leaf]
        else:
            if output_value.type == 'CMP':
                result = cmp_function(output_value, evaluation)
            elif output_value.type == 'Sub':
                result = sub_function(output_value, evaluation)
            elif output_value.type == 'Rem':
                result = rem_function(output_value, evaluation)
        evaluation.update({input_variable.leaf: result})
    else:
        print("The actions are not matched.")
    return evaluation


def parallelism_trans2_qLTS(temp_components, current_state, evaluation):
    # print(evaluation)
    global state
    # "acts" is the list of node sets whose type is must "Next", so its left is next action
    acts = next_act(temp_components, evaluation)
    act_pos = []
    if have_matched(acts):
        input_act_pos = [t for t in range(
            len(acts)) if contains_act_(acts[t], '?') == True]
        output_act_pos = [t for t in range(
            len(acts)) if contains_act_(acts[t], '!') == True]
        for i in input_act_pos:
            for o in output_act_pos:
                if i == o:
                    break
                for action1 in acts[i]:
                    for action2 in acts[o]:
                        new_temp_components = update_components2(
                            i, o, action1, action2, temp_components)
                        if new_temp_components != None:
                            state = state+1
                            new_evaluation = evaluation
                            new_evaluation = update_variable(
                                action1, action2, evaluation)
                            transition.append(
                                (current_state, state, tau, 'matched'))
                            add_slilent_SN(current_state, gen_parallel_stmt(
                                new_temp_components), 'matched')
                            parallelism_trans2_qLTS(
                                new_temp_components, state, new_evaluation)
        input_act_pos = [t for t in range(
            len(acts)) if contains_act_(acts[t], '.?') == True]
        output_act_pos = [t for t in range(
            len(acts)) if contains_act_(acts[t], '.!') == True]
        for i in input_act_pos:
            for o in output_act_pos:
                if i == o:
                    break
                for action1 in acts[i]:
                    for action2 in acts[o]:
                        new_temp_components = update_components2(
                            i, o, action1, action2, temp_components)
                        if new_temp_components != None:
                            state = state+1
                            transition.append(
                                (current_state, state, tau, 'matched'))
                            add_slilent_SN(current_state, gen_parallel_stmt(
                                new_temp_components), 'matched')
                            parallelism_trans2_qLTS(
                                new_temp_components, state, evaluation)
    else:
        for t in range(len(acts)):
            b = contains_act_(acts[t], '?') or contains_act_(acts[t], '!') or contains_act_(
                acts[t], '.?') or contains_act_(acts[t], '.!') or None in acts[t]
            if b == False:
                act_pos.append(t)
        if len(act_pos) == 0:
            act_pos = [t for t in range(len(acts)) if None not in acts[t]]
    # "action" is a node about next action
    # print(act_pos)
    if len(act_pos) > 0:
        a = act_pos[0]
        if len(acts[a]) > 0:
            action = acts[a][0]
            # print(action.stmt)
            if action.children[0].type == 'Silent':
                new_temp_components = update_components1(
                    a, action, temp_components)
                state = state+1
                transition.append((current_state, state, tau, 'silent'))
                add_slilent_SN(current_state, gen_parallel_stmt(
                    new_temp_components), 'silent')
                parallelism_trans2_qLTS(new_temp_components, state, evaluation)
            elif action.children[0].type == 'Superoperator':
                new_temp_components = update_components1(
                    a, action, temp_components)
                state = state+1
                transition.append((current_state, state, tau, 'operation'))
                add_slilent_SN(current_state, gen_parallel_stmt(
                    new_temp_components), 'silent')
                current_state = state
                state = state+1
                text = action.children[0].leaf
                mat = matrix_presentation(text)
                current_operator = snapshot[current_state]['density operator']
                new_operator = np.zeros((mat_size, mat_size))
                for m in mat:
                    new_operator = new_operator + \
                        np.dot(np.dot(m, current_operator),
                               m.conjugate().transpose())
                    new_operator = np.around(new_operator, decimals=accuracy)
                prob = round(trace(new_operator), accuracy2)
                new_snapshot = {'term': gen_parallel_stmt(new_temp_components),  # 'probability': prob,
                                'kraus operator': mat,
                                'density operator': new_operator,
                                'action': text}
                snapshot.append(new_snapshot)
                transition.append((current_state, state,  # "p="+str(prob)
                                   prob, 'operation'))
                parallelism_trans2_qLTS(new_temp_components, state, evaluation)
            elif action.children[0].type == 'Measurement':
                new_temp_components = update_components1(
                    a, action, temp_components)
                state = state+1
                transition.append((current_state, state, tau, 'measurement'))
                add_slilent_SN(current_state, gen_parallel_stmt(
                    new_temp_components), 'silent')
                current_state = state
                text = action.children[0].leaf
                for i in range(len(text)):
                    if text[i] == '[':
                        break
                for j in range(len(text)):
                    if text[j] == ';':
                        break
                qbit = pd.read_csv(StringIO(text[i+1:j])).columns.tolist()
                cbit = pd.read_csv(
                    StringIO(text[j+1:len(text)-1])).columns.tolist()
                # Branch is dicide by the qubits measured (exactly 2^n).
                # The order of the qubits won't be organized,
                # only tesor I before or after the qubits instead,
                # as what matrix_presentation() done.
                name = text[0:i]
                measurement = meas[name]
                measurement = temp_method_for_building_superoperator(
                    measurement, qbit)
                n = 0
                for m in measurement:
                    current_operator = snapshot[current_state]['density operator']
                    new_operator = np.dot(np.dot(m, current_operator), m)
                    new_operator = np.around(new_operator, decimals=accuracy)
                    prob = round(trace(new_operator), accuracy2)
                    if prob == 0:
                        flag_tr = 0
                        # print("Can not normalize the superoperator. Trace is 0.")
                    else:
                        state = state+1
                        new_evaluation = evaluation
                        ss = (1/prob)
                        new_operator = new_operator*ss
                        dic = {cbit[0]: n}
                        new_evaluation.update(dic)
                        new_snapshot = {'term': gen_parallel_stmt(new_temp_components),  # 'probability': prob,
                                        'kraus operator': m,
                                        'density operator': new_operator,
                                        'action name': name}
                        snapshot.append(new_snapshot)
                        transition.append((current_state, state,  # "p"+str(int(n))+"="+str(prob)
                                           prob, 'measurement'))
                        parallelism_trans2_qLTS(
                            new_temp_components, state, new_evaluation)
                    n = n+1
            elif action.children[0].type == 'Pstr':
                new_temp_components = update_components1(
                    a, action, temp_components)
                text = action.children[0].leaf
                for i in range(len(text)):
                    if text[i] == '[':
                        break
                for j in range(len(text)):
                    if text[j] == ';':
                        break
                qbit = pd.read_csv(StringIO(text[i+1:j])).columns.tolist()
                cbit = pd.read_csv(
                    StringIO(text[j+1:len(text)-1])).columns.tolist()
                n = 2**len(qbit)-1
                dic = {cbit[0]: n}
                evaluation.update(dic)
                state += 1
                transition.append(
                    (current_state, state, tau, 'silent', evaluation))
                add_slilent_SN(current_state, statement, 'silent')
                parallelism_trans2_qLTS(new_temp_components, state, evaluation)
            else:
                new_stmt = action.children[0].stmt
                if action.children[0].leaf == '!' or action.children[0].leaf == '.!':
                    func = action.children[0].children[1]
                    if func.type == 'CMP':
                        result = cmp_function(func, evaluation)
                        new_stmt = action.children[0].children[0].stmt + \
                            action.children[0].leaf+result
                    elif func.type == 'Sub':
                        result = sub_function(func, evaluation)
                        new_stmt = action.children[0].children[0].stmt + \
                            action.children[0].leaf+result
                    elif func.type == 'Rem':
                        result = rem_function(func, evaluation)
                        new_stmt = action.children[0].children[0].stmt + \
                            action.children[0].leaf+result
                    else:
                        result = ''
                        if func.leaf in evaluation.keys():
                            result = str(evaluation[func.leaf])
                        else:
                            result = func.leaf
                        new_stmt = action.children[0].children[0].stmt + \
                            action.children[0].leaf+result
                new_temp_components = update_components1(
                    a, action, temp_components)
                state = state+1
                transition.append(
                    (current_state, state, new_stmt, action.children[0].leaf.lower()))
                add_slilent_SN(current_state, gen_parallel_stmt(
                    new_temp_components), action.children[0].leaf)
                parallelism_trans2_qLTS(new_temp_components, state, evaluation)
    return


def match_action(action1, action2):
    input_action = action1.stmt.strip()
    output_action = action2.stmt.strip()
    # print(input_action,output_action)
    begin = 0
    end = 0
    channel_begin = begin
    channel_end = end
    input_channel = "ch_in"
    output_channel = "chi_out"
    for i in range(len(input_action)):
        if input_action[i] == '?':
            channel_end = i
            if channel_end > channel_begin:
                input_channel = input_action[channel_begin:channel_end]
            else:
                print("Error: Syntax error in Input action.")
    for i in range(len(output_action)):
        if output_action[i] == '!':
            channel_end = i
            if channel_end > channel_begin:
                output_channel = output_action[channel_begin:channel_end]
            else:
                print("Error: Syntax error in Output action.")
    return (input_channel == output_channel)


def gen_parallel_stmt(temp_components):
    statement = temp_components[0].stmt
    for i in range(1, len(temp_components)):
        statement = statement+"||"+temp_components[i].stmt
    return statement


def add_slilent_SN(current_state, statement, action="unknown"):
    mat = [np.eye(mat_size)]
    current_superoperator = snapshot[current_state]['density operator']
    new_snapshot = {'term': statement,  # 'probability': 1,
                    'kraus operator': mat,
                    'density operator': current_superoperator,
                    'action name': action}
    snapshot.append(new_snapshot)
    return


def get_parameters(process, number):
    # print(number,process)
    para = []
    begin = 0
    end = len(process)
    count = 0
    # Get Ka/Kb,Ba,Bb
    for i in range(len(process)):
        if process[i] == '(':
            begin = i
        if process[i] == ',':
            end = i
            name = process[begin+1:end]
            para.append(name)
            count = count+1
            begin = end
        if process[i] == ')':
            end = i
        if count > number-1:
            break
    if end >= len(process)-1:
        name = process[begin+1:end]
        para.append(name)
    return para


def cmp_function(tree, evaluation):
    process = tree.stmt.strip()
    # print(process)
    # print(evaluation)
    # Get Ka/Kb,Ba,Bb
    para = get_parameters(process, 3)
    # for p in para:
    #	print(p)
    # Compare Ba,Bb, if matched store Ka/Kb
    result = ''
    qubit = []
    for name in para:
        if name in evaluation.keys():
            if evaluation[name] != '':
                qubit.append(number2qubit(evaluation[name]))
    if len(qubit) == 3:
    	# Consider the case that the length of qubits is over 1
        for i in range(n):
            if qubit[1][i] == qubit[2][i]:
                result = result+str(qubit[0][i])
        if len(result) == 0:
            result = ''
    else:
        print("Warning: lack of parameters in cmp function.")
        return result
    return result


def cmp_function2(tree, evaluation):
    process = tree.stmt.strip()
    # print(process)
    # print(evaluation)
    # Get Ka/Kb,Ba,Bb
    para = get_parameters(process, 4)
    # for p in para:
    #	print(p)
    # Compare Ba,Bb, if matched store Ka/Kb
    result = ''
    qubit = []
    for name in para:
        if name in evaluation.keys():
            if evaluation[name] != '':
                qubit.append(number2qubit(evaluation[name]))
    if len(para) == 4:
        for i in range(len(qubit[0])):
            if qubit[1][i] == qubit[2][i]:
                result = result+str(qubit[0][i])
        if len(result) == 0:
            result = ''
        evaluation.update({para[3]: result})
    else:
        print("Warning: lack of parameters in cmp function.")
        return evaluation
    return evaluation


def sub_function(tree, evaluation):
    process = tree.stmt.strip()
    # print(process)
    # print(evaluation)
    # Get Ka/Kb,Ba,Bb
    para = get_parameters(process, 2)
    # for p in para:
    #	print(p)
    # Compare Ba,Bb, if matched store Ka/Kb
    result = ''
    if len(para) == 2:
        qubit = ''
        if para[0] in evaluation.keys():
            qubit = evaluation[para[0]]
        strlen = 0
        if para[1] in evaluation.keys():
            strlen = int(evaluation[para[1]])
        # print(qubit,strlen)
        for i in range(strlen):
            if i < len(qubit):
                result = result+str(qubit[i])
        if len(result) == 0:
            result = ''
    else:
        print("Warning: lack of parameters in sub function.")
        return result
    return result


def xor_function(tree, evaluation):
    return result


def rem_function(tree, evaluation):
    process = tree.stmt.strip()
    # print(process)
    # print(evaluation)
    # Get Ka/Kb,Ba,Bb
    para = get_parameters(process, 2)
    # for p in para:
    #	print(p)
    # Compare Ba,Bb, if matched store Ka/Kb
    result = ''
    if len(para) == 2:
        qubit = ''
        if para[0] in evaluation.keys():
            qubit = evaluation[para[0]]
        strlen = 0
        if para[1] in evaluation.keys():
            strlen = int(evaluation[para[1]])
        if strlen < len(qubit):
            result = qubit[strlen:]
        if len(result) == 0:
            result = ''
    else:
        print("Warning: lack of parameters in rem function.")
        return result
    # print(result)
    return result
