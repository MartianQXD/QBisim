import ply.yacc as yacc
from q_ast_concrete import tokens

#定义顶层规则
start = 'clause'
#定义优先级
precedence = (
	('right','NOT'),
	('left','OR'),
	('left','AND'),
	('left','EQUAL'),
	('left','GE','LE','GT','LT'),
	('left','PLUS','MINUS'),
	('left','TIMES','DIVIDE'),
	('left','Choice'),
	('left','IF','THEN'),
	('right','Parallel'),
	('left','Prefix'),
	('left','Define'),
	('left','Next'),
)
#定义AST节点
class Node:
	def __init__(self,type,stmt,leaf=None,children=None):
		self.type = type
		self.leaf = leaf
		self.stmt = stmt
		if children:
			self.children = children
		else:
			self.children = []
#构造AST规则
def p_several_clause(p):
	'clause : clause Next clause'
	p[0] = Node('Next','',p[2],[p[1],p[3]])
def p_clause_term_define(p):
	'clause : term Define term'
	p[0] = Node('BinaryOpProc',str(p[1].stmt)+str(p[2])+str(p[3].stmt),p[2],[p[1],p[3]])
def p_term_nil(p):
	'term : NULL'
	#p[0] = ('null-term',p[1])
	p[0] = Node('NULL',str(p[1]),p[1])
def p_term_process(p):
	'term : Process'
	#p[0] = ('process-term',p[1])
	p[0] = Node('Process',str(p[1]),p[1])
def p_term_name(p):
	'term : Name'
	#p[0] = ('process-term',p[1])
	p[0] = Node('Name',str(p[1]),p[1])
def p_term_parallel(p):
	'term : term Forbidden'
	p[0] = Node('Forbidden',str(p[1].stmt)+str(p[2]),p[2],[p[1]])
def p_term_binaryopproc(p):
	'''term : action Prefix term
			| term Choice term
			| term Parallel term'''
	#p[0] = ('binary-op-term',p[2],p[1],p[3])
	p[0] = Node('BinaryOpProc',str(p[1].stmt)+str(p[2])+str(p[3].stmt),p[2],[p[1],p[3]])
def p_term_relabel(p):
	'term : term Relabel'
	#p[0] = ('relabel',p[2],p[1])
	p[0] = Node('Relabel',str(p[1].stmt)+str(p[2]),p[2],[p[1]])
def p_term_ifthenelse(p):
	'term : IF expression THEN term'
	#p[0] = ('IfThenElse',p[1],p[2],p[4])
	p[0] = Node('IfThenElse',str(p[1])+" "+str(p[2].stmt)+" "+str(p[3])+" "+str(p[4].stmt),p[1],[p[2],p[4]])
def p_term_term(p):
	'term : LPAREN term RPAREN'
	#p[0] = ('Term','()',p[2])
	p[0] = Node('Term',"("+str(p[2].stmt)+")",'()',[p[2]])
def p_action_silent(p):
	'action : Silent'
	#p[0] = ('Silent',p[1])
	p[0] = Node('Silent',str(p[1]),p[1])
def p_action_binaryopact(p):
	'''action : name CInput name
			  | name COutput name
			  | name QInput name
			  | name QOutput name'''
	#p[0] = ('binary-op-act',p[2],p[1],p[3])
	p[0] = Node('BinaryOpAct',str(p[1].stmt)+str(p[2])+str(p[3].stmt),p[2],[p[1],p[3]])
def p_action_superoperator(p):
	'action : Superoperator'
	#p[0] = ('Superoperator',p[1])
	p[0] = Node('Superoperator',str(p[1]),p[1])
def p_action_measurement(p):
	'action : Measurement'
	#p[0] = ('Measurement',p[1])
	p[0] = Node('Measurement',str(p[1]),p[1])
def p_action_pstr(p):
	'action : Pstr'
	p[0] = Node('Pstr',str(p[1]),p[1])
def p_action_ran(p):
	'action : Ran'
	p[0] = Node('Ran',str(p[1]),p[1])
def p_name(p):
	'name : Name'
	#p[0] = ('Name',p[1])
	p[0] = Node('Name',str(p[1]),p[1])
def p_name_cmp(p):
	'name : CMP'
	p[0] = Node('CMP',str(p[1]),p[1])
def p_name_sub(p):
	'name : Sub'
	p[0] = Node('Sub',str(p[1]),p[1])
def p_name_Rem(p):
	'name : Rem'
	p[0] = Node('Rem',str(p[1]),p[1])
def p_expression_unaryopexpr(p):
	'''expression : NOT expression'''
	#p[0] = ('unary-op-expr',p[1],p[2])
	p[0] = Node('UnaryOpExpr',str(p[1])+str(p[2].stmt),p[1],[p[2]])
def p_expression_binaryopexpr(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression TIMES expression
				  | expression DIVIDE expression
				  | expression EQUAL expression
				  | expression AND expression
				  | expression OR expression
				  | expression GE expression
				  | expression LE expression
				  | expression GT expression
				  | expression LT expression'''
	#p[0] = ('binary-op-expr',p[2],p[1],p[3])
	p[0] = Node('BinaryOpExpr',str(p[1].stmt)+str(p[2])+str(p[3].stmt),p[2],[p[1],p[3]])
def p_expression_expression(p):
	'expression : LPAREN expression RPAREN'
	#p[0] = ('Expression','()',p[2])
	p[0] = Node('Expression',"("+str(p[2].stmt)+")",'()',[p[2]])
def p_expression_num(p):
	'expression : NUMBER'
	#p[0] = ('NUMBER',p[1])
	p[0] = Node('Number',str(p[1]),p[1])
def p_expression_name(p):
	'expression : Name'
	#p[0] = ('Name',p[1])
	p[0] = Node('Name',str(p[1]),p[1])
def p_expression_substr(p):
	'expression : Sub'
	p[0] = Node('Sub',str(p[1]),p[1])
def p_expression_cmp(p):
	'expression : CMP'
	p[0] = Node('CMP',str(p[1]),p[1])
def p_error(p):
	print("Syntax error at '%s'" % p.value)

parser = yacc.yacc(debug=True)