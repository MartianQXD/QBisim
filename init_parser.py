import ply.yacc as yacc
from q_ast_concrete import tokens

#定义顶层规则
start = 'init'
#定义优先级
precedence = (
	('left','EQUAL'),
	('left','PLUS','MINUS'),
	('left','TIMES','DIVIDE'),
	('left','CRegister','QRegister','Register'),
	('left','Next'),
)
#定义AST节点
class Node:
	def __init__(self,type,leaf=None,children=None):
		self.type = type
		self.leaf = leaf
		if children:
			self.children = children
		else:
			self.children = []
#构造AST规则
def p_info_term(p):
	'init : NUMBER_SIGN clause NUMBER_SIGN'
	p[0] = Node('Init',p[1],[p[2]])
def p_several_clause(p):
	'clause : clause Next clause'
	p[0] = Node('Next Statements',p[2],[p[1],p[3]])
def p_clause_register(p):
	'''clause : cregister 
			  | qregister'''
	p[0] = Node('SINGLE',p[1].leaf,[p[1]])
def p_clause_assignment(p):
	'''clause : cregister EQUAL assignment
			  | qregister EQUAL expression'''
	p[0] = Node('EQUAL',p[2],[p[1],p[3]])
def p_expression_binaryopexpr(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression'''
	p[0] = Node('BinaryOpExpr',p[2],[p[1],p[3]])
def p_expression_negative(p):
	'expression : MINUS expression'
	p[0] = Node('Negative',p[1],[p[2]])
def p_expression_coeffexpr(p):
	'expression : number TIMES register'
	p[0] = Node('Coeff',p[2],[p[1],p[3]])
def p_expression_nocoeffexpr(p):
	'expression : register'
	p[0] = Node('NoCoeff',p[1].leaf,[p[1]])
def p_assignment(p):
	'assignment : Assignment'
	p[0] = Node('Assignment',p[1])
def p_register(p):
	'register : Register'
	p[0] = Node('Register',p[1])
def p_cregister(p):
	'cregister : CRegister'
	p[0] = Node('CRegister',p[1])
def p_qregister(p):
	'qregister : QRegister'
	p[0] = Node('QRegister',p[1])
def p_number(p):
	'number : NUMBER'
	p[0] = Node('Number',p[1])
def p_error(p):
	print("Syntax error at '%s'" % p.value)

init_parser = yacc.yacc(debug=True)