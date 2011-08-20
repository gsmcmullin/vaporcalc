import gtk
import gtk.gdk
import glib
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

def eng_formatter(f, sigfigs=4):
	# Format floats in engineering notation
	mult = {-15: 'f', -12: 'p', -9: 'n', -6: u'\u03bc', -3: 'm', 
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
	ff = round(f * (10 ** (sigfigs - p)))
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
#	if not entry.get_text():
#		entry.set_property("editing-canceled", True)
#		entry.editing_done()
#		entry.remove_widget()
#		return True

#	if keyname == "Escape":
#		return False
		
	if (keyname == "d") and (event.state & gtk.gdk.CONTROL_MASK):
		entry.stop_editing(True)
		#w.hide()
		w.iconify()
		return True

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
		entry.set_property("editing-canceled", False)
		entry.editing_done()
		entry.remove_widget()
		return True
	
	return False

def button_press(ww, e):
	w.window.begin_move_drag(int(e.button), int(e.x_root), int(e.y_root), int(e.time))
	return True

editing = False

def do_changed(editable):
	if not editable.get_text():
		editable.set_property("editing-canceled", True)
		editable.editing_done()
		editable.remove_widget()

def editing_started(cel, editable, path):
	global editing
	editable.connect("editing-done", editing_done)
	editable.connect("key-press-event", do_keypress)
	editable.connect("changed", do_changed)
	editing = True

def editing_done(editable):
	global editing
	if not editable.get_property("editing-canceled"):
		s = editable.get_text()
		rpn.dostr(s)
	do_update()
	sv.get_selection().unselect_all()
	editing = False

def key_press(ww, e):
	if editing: return

	keyname = gtk.gdk.keyval_name(e.keyval) 
	print keyname
	# Modifier keys to ignore.
	mods = ["Control_L", "Control_R", 
		"Shift_L", "Shift_R", 
		"Escape", 
		"Alt_L", "Alt_R",
		"Meta_L", "Meta_R",
		"Up", "Down", "Left", "Right",
	]
	if keyname in mods:
		return True

	if (keyname == "BackSpace") or (keyname == "Delete"):
		rpn.dostr("drop")
		do_update()
		return True

	if (keyname == "Return") or (keyname == "KP_Enter"):
		rpn.dostr("dup")
		do_update()
		return True

	if (keyname == "d") and (e.state & gtk.gdk.CONTROL_MASK):
		#w.hide()
		w.iconify()
		return True

	sm = ww.get_model()
	it = sm.get_iter_first()
	sm.remove(it)
	path = sm.get_string_from_iter(sm.append())
	ww.set_cursor(path, ww.get_column(1), True)
	gtk.main_do_event(e.copy())
	return True

if __name__ == "__main__":
	w = gtk.Window()
	w.connect("delete-event", lambda w, e: w.iconify() or True)
	w.connect("destroy", gtk.main_quit)
	w.set_default_size(200, 100)
	w.set_title("VaporCalc")
	w.set_icon_from_file("vapor-small.png")
	w.set_decorated(False)
	w.set_border_width(2)
	w.set_keep_above(1)
	w.stick()
	#w.set_skip_taskbar_hint(True)
	w.set_skip_pager_hint(True)
	w.set_opacity(0.9)
	w.set_resizable(False)
	# Put a background on the window
	bgcolour = gtk.gdk.color_parse("black")
	w.modify_bg(gtk.STATE_NORMAL, bgcolour)

	vbox = gtk.VBox()
	w.add(vbox)

	sm = gtk.ListStore(str, str)
	for i in range(4):
		it = sm.append(('   ', None))
	sv = gtk.TreeView(sm)
	sv.set_cursor(sm.get_string_from_iter(it))
	sv.set_size_request(150, -1)
	sv.connect("button-press-event", button_press)
	sv.connect("key-press-event", key_press)
	sv.set_headers_visible(False)
	sv.set_rules_hint(True)
	sv.append_column(gtk.TreeViewColumn(None, gtk.CellRendererText(), text=0))
	cel = gtk.CellRendererText()
	cel.set_alignment(1, 0.5)
	cel.set_property("editable", True)
	cel.connect("editing-started", editing_started)
	sv.append_column(gtk.TreeViewColumn(None, cel, text=1))
	sv.set_can_focus(True)
	vbox.pack_start(sv, True, True)

	w.show_all()
	#sv.grab_focus()
	sv.get_selection().unselect_all()

	gtk.main()

