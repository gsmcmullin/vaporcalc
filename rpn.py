import ply.lex as lex
import sys
import math

lastarg = []
stack = []

class Op(object):
	__slots__ = ('key', 'args', 'function');
	ops = {}

	def __init__(self, key, args, function):
		self.key = key
		self.args = args
		self.function = function
		Op.ops[key] = self

# Stack operations
Op('DROP', 1, lambda a: None)
Op('DUP', 1, lambda a: (a, a))
Op('EXCH', 2, lambda a, b: (b, a))
Op('LASTARG', 0, lambda : lastarg)
def clearstack():
	global stack
	stack = []
Op('CLEAR', 0, clearstack)
# Arithmetic
Op('+', 2, lambda a, b: a + b)
Op('-', 2, lambda a, b: a - b)
Op('*', 2, lambda a, b: a * b)
Op('/', 2, lambda a, b: a / b)
Op('NEG', 1, lambda a: -a)
Op('INV', 1, lambda a: 1/a)
# Trigonometric
Op('PI', 0, lambda : math.pi)
Op('SIN', 1, math.sin)
Op('COS', 1, math.cos)
Op('TAN', 1, math.tan)
Op('ASIN', 1, math.asin)
Op('ACOS', 1, math.acos)
Op('ATAN', 1, math.atan)
# Exponential and Logarithm
Op('LN', 1, math.log)
Op('EXP', 1, math.exp)
Op('^', 2, math.pow)
Op('SQRT', 1, math.sqrt)
Op('SQR', 1, lambda a: a * a)

tokens = ('SPICENUM', 'NUMBER', 'OP')

t_ignore = '\t \n\r'

# Scan a number in SPICE notation.  1k2 == 1200
def t_SPICENUM(t):
	r'[-+]?((\d+[TtGgMKkmUuNnPpFf]\d*)|((\d+(\.\d*)?|\.\d+)[TtGgMKkmUuNnPpFf]))'
	mult = {'T':1e12, 't':1e12,
		'G':1e9, 'g':1e9,
		'M':1e6, 
		'K':1e3, 'k':1e3, 
		'm':1e-3, 
		'U':1e-6, 'u': 1e-6,
		'N':1e-9, 'n': 1e-9,
		'P':1e-12, 'p': 1e-12,
		'F':1e-15, 'f': 1e-15,
	}
	if '.' in t.value:
		num = float(t.value[:-1])
		num *= mult[t.value[-1]]
	else:
		m = t.value.strip("0123456789")[0]
		i = t.value.find(m)
		t.value = t.value[:i] + '.' + t.value[i+1:]
		num = float(t.value)
		num *= mult[m]

	stack.append(num)

# Scan a number if floating point notation. 1.2e3
def t_NUMBER(t):
	r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
	stack.append(float(t.value))

# Scan a operator.
def t_OP(t):
	r'[^\t \n\r]+'

	global lastarg
	t.value = t.value.upper()

	f = Op.ops.get(t.value, None)
	if not f:
		# No op by this name, just push name to stack.
		stack.append(t.value)
		return

	# Get args from the stack
	if f.args:
		arg = tuple(stack[-f.args:])
		del stack[-f.args:]
	else:
		arg = ()

	# Call operation
	try:
		result = f.function(*arg)
	except:
		print "Error in operation"
		stack.extend(arg)
		return

	lastarg = arg

	# Push results to the stack
	if result is None: return
	if type(result) is tuple:
		stack.extend(result)
	else:
		stack.append(result)

# Error handling rule
def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

lexer = lex.lex()

def dostr(s):
	lexer.input(s)
	for tok in lexer:
		pass

if __name__ == "__main__":
	while True:
		line = sys.stdin.readline()
		if not line: break

		lexer.input(line)
		for tok in lexer:
			print tok
		print "STACK = %r" % stack

