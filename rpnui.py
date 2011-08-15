import gtk
import gtk.gdk
import rpn
import math

def do_update():
	# Update tree view from RPN stack
	sm.clear()
	stacktop = rpn.stack[-4:]
	for i in range(4 - len(stacktop)):
		sm.append(('', ''))
	for i in range(len(stacktop)):
		if type(stacktop[i]) is float:
			sm.append((len(stacktop) - i, eng_formatter(stacktop[i])))
		else:
			sm.append((len(stacktop) - i, repr(stacktop[i])))
	entry.set_text("")

def do_activate(entry):
	# Send text to RPN scanner
	s = entry.get_text()
	if not s: s = "dup"
	rpn.dostr(s)
	do_update()

def eng_formatter(f, sigfigs=4):
	# Format floats in engineering notation
	mult = {-15: 'f', -12: 'p', -9: 'n', -6: 'u', -3: 'm', 
		0: '', 
		3: 'k', 6: 'M', 9: 'G', 12: 'T'}

	if f < 0:
		sign = '-'
		f = -f
	else:
		sign = ''

	exp = 0
	if f != 0:
		while f < 1:
			exp -= 3
			f *= 1000
		while f >= 1000:
			exp += 3
			f /= 1000

	p = int(math.log10(f) if f > 0 else 0) + 1
	ff = f * (10 ** (sigfigs - p))
	s = ''
	for i in range(sigfigs):
		s = str(int(ff) % 10) + s
		ff /= 10
		p += 1
		if p == sigfigs:
			s = '.' + s

	return sign + s + mult.get(exp, "e%02d" % exp)

def do_keypress(entry, event):
	keyname = gtk.gdk.keyval_name(event.keyval) 
	if not entry.get_text():
		if keyname == "BackSpace":
			entry.set_text("drop")
			do_activate(entry)
			return True

	if keyname == "Escape":
		entry.set_text('')
		return True
		
	if (keyname == "d") and (event.state & gtk.gdk.CONTROL_MASK):
		#w.hide()
		w.iconify()
		#gtk.main_quit()

	keyop = {
		"plus": '+', "KP_Add": '+',
		"minus": '-', "KP_Subtract": '-',
		"asterisk": '*', "KP_Multiply": '*',
		"slash": '/', "KP_Divide": '/',
		"asciicircum": ' ^',
		"space": ' ',
		}
	if keyop.has_key(keyname):
		text = entry.get_text() + " " + keyop[keyname]
		entry.set_text(text)
		do_activate(entry)
		return True
	
	return False

if __name__ == "__main__":
	w = gtk.Window()
	w.connect("delete-event", lambda w, e: w.iconify() or True)
	w.connect("destroy", gtk.main_quit)
	w.set_default_size(200, 100)
	w.set_title("VaporCalc")
	w.set_decorated(False)
	w.set_border_width(1)
	w.set_keep_above(1)
	#w.set_skip_taskbar_hint(True)
	w.set_skip_pager_hint(True)
	w.set_opacity(0.9)
	w.set_resizable(False)

	vbox = gtk.VBox()
	w.add(vbox)

	sm = gtk.ListStore(str, str)
	for i in range(4):
		sm.append(('   ', None))
	sv = gtk.TreeView(sm)
	sv.set_headers_visible(False)
	sv.set_rules_hint(True)
	sv.append_column(gtk.TreeViewColumn(None, gtk.CellRendererText(), text=0))
	cel = gtk.CellRendererText()
	cel.set_alignment(1, 0.5)
	sv.append_column(gtk.TreeViewColumn(None, cel, text=1))
	sv.set_can_focus(False)
	vbox.pack_start(sv, True, True)

	entry = gtk.Entry()
	entry.connect("activate", do_activate)
	entry.connect("key-press-event", do_keypress)
	vbox.pack_start(entry, False, False)

	w.show_all()
	gtk.main()
