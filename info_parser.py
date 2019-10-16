import ply.yacc as yacc
from q_ast import tokens

#定义顶层规则
start = 'info'
#定义优先级
precedence = (
	('left','Mapping'),
	('left','PLUS','MINUS'),
	('left','TIMES'),
	('left','Register'),
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
	'info : LBRACE term RBRACE'
	p[0] = Node('Info',p[1],[p[2]])
def p_term_next(p):
	'term : term Next term'
	p[0] = Node('Next Statements',p[2],[p[1],p[3]])
def p_term_mapping(p):
	'term : name register Mapping expression'
	p[0] = Node('Mapping',p[3],[p[1],p[2],p[4]])
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
	p[0] = Node('NoCoeff','EXPR',[p[1]])
def p_register(p):
	'register : Register'
	p[0] = Node('Register',p[1])
def p_number(p):
	'number : NUMBER'
	p[0] = Node('Number',p[1])
def p_name(p):
	'name : Name'
	p[0] = Node('Name',p[1])
def p_error(p):
	print("Syntax error at '%s'" % p.value)

info_parser = yacc.yacc(debug=True)