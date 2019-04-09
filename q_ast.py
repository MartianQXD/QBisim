import ply.lex as lex

#token列表，qCCS的terms
tokens = [
#	For main qCCS semantics
	'NULL',
	'Process',
	'Prefix',
	'Choice',
	'Parallel',
	'Forbidden',
	'Relabel',
	'IF',
	'THEN',
	'Silent',
	'CInput',
	'COutput',
	'QInput',
	'QOutput',
	'Superoperator',
	'Measurement',
    'Define',
    'Name',
    'LPAREN',
    'RPAREN',
#    'ID',
#	For boolean expression
	'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQUAL',
    'NOT',
    'AND',
    'OR',
    'GT',
    'LT',
    'GE',
    'LE',
#	For Kraus operator
    'LBRACE',
    'RBRACE',
    'Mapping',
    'Kraus',
    'Register',
    'Next',
#   For initialization
	'NUMBER_SIGN', 
	'CRegister',
	'QRegister',
	'Assignment',
]

#通过正则表达式匹配terms,以函数形式定义时，会严格按照顺序匹配表达式
def t_NULL(t):
	r'nil'
	return t

def t_Superoperator(t):
	r'\w*\[([a-z]([0-9]*)\,{0,1})*\]'
	return t

def t_Measurement(t):
	r'M([0-9]*)\[(q([0-9]*)\,)*q([0-9]*);(x([0-9]*)\,)*x([0-9]*)*\]'
	return t

def t_Define(t):
	r'def'
	return t

def t_Process(t):
	r'[A-Za-z]*([0-9]*)(\((x([0-9]*)\,)*(q([0-9]*)\,)*q([0-9]*)\))'
	return t

t_Next  = r'\;'

t_Prefix = r'\.'

t_Choice = r'\+'

t_Parallel = r'\|\|'

t_Forbidden = r'\\\{([A-Za-z]*([0-9]*)\,)*([A-Za-z]*([0-9]*))\}'

def t_Relabel(t):
	r'\[[a-z]\]'
	return t

def t_Silent(t):
	r'tau'
	return t

def t_QInput(t):
	r'\.\?'
	return t

def t_QOutput(t):
	r'\.\!'
	return t

def t_CInput(t):
	r'\?'
	return t

def t_COutput(t):
	r'\!'
	return t

t_LPAREN = r'\('

t_RPAREN = r'\)'

#定义额外规则，排他型
states = (
	('bexpr','exclusive'),
	('kraus','exclusive'),
	('rinit','exclusive')
)

#匹配到“#”时进入register initialization，再次遇到“#”时退出
def t_rinit(t):
	r'\#'
	t.type = "NUMBER_SIGN"
	t.lexer.init_start = t.lexer.lexpos
	t.lexer.level = 1
	print("Enter into register initialization.")
	t.lexer.begin('rinit')
	return t

def t_rinit_number_sign(t):     
    r'\#'
    t.type = "NUMBER_SIGN"
    if t.lexer.level == 0:
    	t.lexer.level = 1
    elif t.lexer.level == 1:
    	t.lexer.level = 0
    	t.lexer.lineno += t.value.count('\n')
    	# Record the end of the init part
    	t.lexer.init_end = t.lexer.lexpos
    	print("Return (from register initialization) to INITIAL.",t.lexer.init_end)
    	t.lexer.begin('INITIAL')
    return t

t_rinit_PLUS  = r'\+'
t_rinit_MINUS = r'-'
t_rinit_TIMES = r'\*'
t_rinit_DIVIDE = r'/'
t_rinit_EQUAL = r'\='
t_rinit_LPAREN = r'\('
t_rinit_RPAREN = r'\)'
t_rinit_Next = r'\;'

def t_rinit_Assignment(t):
	r'\{[0-9\.\,]*\}'
	return t

def t_rinit_Register(t):
	r'\[[0-1]*\]'
	return t

def t_rinit_CRegister(t):
	r'\{\w+[\w\d,]*\}'
	return t

def t_rinit_QRegister(t):
	r'\[\w+[\w\d,]*\]'
	return t

def t_rinit_NUMBER(t):
    r'[0-9,.]+'
    t.lexer.num_count += 1
    return t

t_rinit_ignore = " \t\n"

def t_rinit_error(t):
    t.lexer.skip(1)

#匹配到if时进入bexpr，then且没有更多嵌套时退出
def t_bexpr(t):
	r'if'
	t.type = "IF"
	t.lexer.code_start = t.lexer.lexpos
	t.lexer.level = 1
	print("Enter into Bexpr.")
	t.lexer.begin('bexpr')
	return t

#嵌套if...then
def t_bexpr_if(t):
	r'if'
	t.type = "IF"
	t.lexer.level += 1
	return t

def t_bexpr_then(t):
	r'then'
	t.type = "THEN"
	t.lexer.level -= 1
	if t.lexer.level == 0:
		t.lexer.lineno += t.value.count('\n')
		print("Return (from Bexpr) to INITIAL.")
		t.lexer.begin('INITIAL')
	return t

t_bexpr_PLUS  = r'\+'
t_bexpr_MINUS = r'-'
t_bexpr_TIMES = r'\*'
t_bexpr_DIVIDE = r'/'
t_bexpr_GE = r'\>\='
t_bexpr_LE = r'\<\='
t_bexpr_GT = r'\>'
t_bexpr_LT = r'\<'
t_bexpr_EQUAL = r'\='
t_bexpr_LPAREN = r'\('
t_bexpr_RPAREN = r'\)'

def t_bexpr_NOT(t):
	r'not'
	return t

def t_bexpr_AND(t):
	r'and'
	return t

def t_bexpr_OR(t):
	r'or'
	return t

def t_bexpr_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    t.lexer.num_count += 1
    return t

def t_bexpr_Name(t):
	r'\w+'
	return t

t_bexpr_ignore = " \t\n"

def t_bexpr_error(t):
	t.lexer.skip(1)

#匹配到{时，进入kraus operator信息录入
def t_kraus(t):
    r'\{'
    t.type = "LBRACE"
    t.lexer.code_start = t.lexer.lexpos
    #加入一个对这部分信息开始位置的记录，同时也作为程序部分的结束
    t.lexer.info_start = t.lexer.lexpos
    t.lexer.level = 1
    print("Enter into Kraus.")
    t.lexer.begin('kraus')
    return t

def t_kraus_lbrace(t):     
    r'\{'
    t.type = "LBRACE"
    t.lexer.level +=1
    return t

def t_kraus_rbrace(t):
    r'\}'
    t.type = "RBRACE"
    t.lexer.level -=1
    if t.lexer.level == 0:
         t.lexer.lineno += t.value.count('\n')
         #加入一个对这部分信息开始位置的记录，作为程序部分的结束
         t.lexer.info_end = t.lexer.lexpos
         print("Return (from Kraus) to INITIAL.")
         t.lexer.begin('INITIAL')
    return t

def t_kraus_Mapping(t):
    r'\-\>'
    return t

def t_kraus_Register(t):
	r'\[[0-1]+\]'
	return t

t_kraus_PLUS  = r'\+'
t_kraus_MINUS = r'-'
t_kraus_TIMES = r'\*'
t_kraus_Next  = r'\;'

def t_kraus_NUMBER(t):
    r'[0-9,.]+'
    t.value = complex(t.value)
    t.lexer.num_count += 1
    return t

def t_kraus_Name(t):
	r'\w+'
	return t

t_kraus_ignore = " \t\n"

def t_kraus_error(t):
    t.lexer.skip(1)

#对象名称
def t_Name(t):
	r'\w+'
	return t

#跟踪行数
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#跳过对齐用的空格
t_ignore = ' \t'

def t_error(t):
    print("Illegal charater '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex(debug=True)
lexer.num_count = 0
lexer.info_start = 0
lexer.info_end = 0