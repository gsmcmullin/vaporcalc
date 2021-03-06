# This file is part of the VaporCalc project.
#
# Copyright (C) 2012  Gareth McMullin <gareth@blacksphere.co.nz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ply.lex as lex
import sys
import math

lastarg = []
stack = []
anglemode = 'DEG'

angleconv = {
	'RAD': 1,
	'DEG': math.pi/180,
	'GRAD': math.pi/200,
}

def setangle(mode):
	global anglemode
	anglemode = mode

def angle2rad(a):
	return a * angleconv[anglemode];

def rad2angle(a):
	return a / angleconv[anglemode];

class Op(object):
	__slots__ = ('key', 'args', 'function');
	ops = {}

	def __init__(self, key, args, function):
		self.key = key
		self.args = args
		self.function = function
		Op.ops[key] = self

# Stack operations
Op('EXIT', 0, lambda: exit())
Op('DROP', 1, lambda a: None)
Op('DUP', 1, lambda a: (a, a))
Op('EXCH', 2, lambda a, b: (b, a))
Op('LASTARG', 0, lambda : lastarg)
def clearstack():
	global stack
	stack = []
Op('CLEAR', 0, clearstack)
# Programming operations
def rpneval(s):
	l = lexer.clone()
	l.input(str(s))
	for tok in l:
		pass
Op('EVAL', 1, rpneval)
def rpndef(code, name):
	Op(name.upper(), 0, lambda : rpneval(code))
Op('DEF', 2, rpndef)
def rpnundef(s):
	del Op.ops[s.upper()]
Op('UNDEF', 1, rpnundef)
# Arithmetic
Op('+', 2, lambda a, b: a + b)
Op('-', 2, lambda a, b: a - b)
Op('*', 2, lambda a, b: a * b)
Op('/', 2, lambda a, b: a / b)
Op('NEG', 1, lambda a: -a)
Op('INV', 1, lambda a: 1/a)
# Trigonometric
Op('PI', 0, lambda : math.pi)
Op('DEG', 0, lambda : setangle('DEG'))
Op('RAD', 0, lambda : setangle('RAD'))
Op('GRAD', 0, lambda : setangle('GRAD'))
Op('SIN', 1, lambda x: math.sin(angle2rad(x)))
Op('COS', 1, lambda x: math.cos(angle2rad(x)))
Op('TAN', 1, lambda x: math.tan(angle2rad(x)))
Op('ASIN', 1, lambda x: rad2angle(math.asin(x)))
Op('ACOS', 1, lambda x: rad2angle(math.acos(x)))
Op('ATAN', 1, lambda x: rad2angle(math.atan(x)))
# Exponential and Logarithm
Op('LN', 1, math.log)
Op('EXP', 1, math.exp)
Op('^', 2, math.pow)
Op('SQRT', 1, math.sqrt)
Op('SQR', 1, lambda a: a * a)

tokens = ('SPICENUM', 'NUMBER', 'STRING', 'OP')

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

# Scan a string
def t_STRING(t):
	r"'[^']+'"
	stack.append(t.value[1:-1])

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
		if len(stack) < f.args:
			raise Exception("%s needs %d args" % (f.key, f.args));
		arg = tuple(stack[-f.args:])
		del stack[-f.args:]
	else:
		arg = ()

	# Call operation
	try:
		result = f.function(*arg)
	except Exception as e:
		stack.extend(arg)
		raise e

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

def formatter(x):
	if type(x) is float:
		return _formatter(x)
	else:
		return repr(x)

def set_formatter(f):
	global _formatter
	_formatter = f

_formatter = repr

def dostr(s):
	lexer.input(s)
	for tok in lexer:
		pass

def stack_to_str(stack):
		return "[" + ", ".join(map(formatter, stack)) + "]"

if __name__ == "__main__":
	while True:
		print ("%s> " % anglemode),
		line = sys.stdin.readline()
		if not line: break

		try:
			dostr(line)
		except Exception as e:
			print e
		print stack_to_str(stack)

