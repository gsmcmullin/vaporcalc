import rpn
import math

def eng_formatter(f, sigfigs=4, spice=True):
	# Format floats in engineering notation
	mult = {-15: 'f', -12: 'p', -9: 'n', -6: u'\u03bc', -3: 'm', 
		0: '',
		3: 'k', 6: 'M', 9: 'G', 12: 'T'}
	if not spice:
			mult = {}

	if f < 0:
		sign = '-'
		f = -f
	else:
		sign = ''

	exp = 0
	if f != 0:
		f = round(f, sigfigs - int(math.log10(f)) - 1)
		while f < 1:
			exp -= 3
			f *= 1000
		while f >= 1000:
			exp += 3
			f /= 1000

	p = int(math.log10(f) if f > 0 else 0) + 1
	ff = round(f * (10 ** (sigfigs - p)))
	s = ''
	for i in range(sigfigs):
		s = str(int(ff) % 10) + s
		ff /= 10
		p += 1
		if p == sigfigs:
			s = '.' + s

	return sign + s + mult.get(exp, "e%02d" % exp)

rpn.Op('STD', 0, lambda : rpn.set_formatter(repr))
rpn.Op('FIX', 1, lambda figs: rpn.set_formatter(lambda x: ("%%.%df" % int(figs)) % x))
rpn.Op('ENG', 1, lambda figs: rpn.set_formatter(lambda x: eng_formatter(x, int(figs), False)))
rpn.Op('SPICE', 1, lambda figs: rpn.set_formatter(lambda x: eng_formatter(x, int(figs), True)))
