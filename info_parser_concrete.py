# -*- coding: utf-8 -*-
import ply.yacc as yacc
from q_ast_concrete import tokens

#定义顶层规则
start = 'info'
#定义优先级
precedence = (
	('left','Next'),
	('left','LBRACKET','RBRACKET','EQUAL'),
	('left','COMMA'),
	('left','PLUS','MINUS'),
	('left','TIMES'),
	('left','Kraus'),
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
def p_term_equal(p):
	'term : name EQUAL LBRACKET set RBRACKET'
	p[0] = Node('EQUAL',p[2],[p[1],p[4]])
def p_term_meas_equal(p):
	'term : measurement EQUAL LBRACKET set RBRACKET'
	p[0] = Node('MEQUAL',p[2],[p[1],p[4]])
def p_set_expression(p):
	'set : expression'
	p[0] = Node('SINGLE','EXPR',[p[1]])
def p_set_comma(p):
	'set : expression COMMA set'
	p[0] = Node('COMMA',p[2],[p[1],p[3]])
def p_expression_binaryopexpr(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression'''
	p[0] = Node('BinaryOpExpr',p[2],[p[1],p[3]])
def p_expression_negative(p):
	'expression : MINUS expression'
	p[0] = Node('Negative',p[1],[p[2]])
def p_expression_coeffexpr(p):
	'expression : number TIMES operator'
	p[0] = Node('Coeff',p[2],[p[1],p[3]])
def p_expression_nocoeffexpr(p):
	'expression : operator'
	p[0] = Node('NoCoeff','EXPR',[p[1]])
def p_register(p):
	'operator : Kraus'
	p[0] = Node('Kraus',p[1])
def p_number(p):
	'number : NUMBER'
	p[0] = Node('Number',p[1])
def p_name(p):
	'name : Name'
	p[0] = Node('Name',p[1])
def p_measurement(p):
	'measurement : Measurement'
	p[0] = Node('Measurement',p[1])
def p_error(p):
	print("Syntax error at '%s'" % p.value)

info_parser = yacc.yacc(debug=True)