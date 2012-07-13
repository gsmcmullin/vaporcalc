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

import gtk
import gtk.gdk
import glib
import rpn
import formatters
import kb
import os
import os.path
import sys

def do_update():
	# Update tree view from RPN stack
	sm.clear()
	stacktop = rpn.stack[-4:]
	for i in range(4 - len(stacktop)):
		sm.append(('   ', ''))
	for i in range(len(stacktop)):
		#if type(stacktop[i]) is float:
			sm.append((len(stacktop) - i, rpn.formatter(stacktop[i])))
		#else:
		#	sm.append((len(stacktop) - i, repr(stacktop[i])))

def do_keypress(entry, event):
	keyname = gtk.gdk.keyval_name(event.keyval)

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
	op_model = gtk.ListStore(str)
	opnames = rpn.Op.ops.keys()
	opnames.sort()
	for k in opnames:
		op_model[op_model.append()] = (k,)
	op_compl = gtk.EntryCompletion()
	op_compl.set_model(op_model)
	op_compl.set_text_column(0)
	op_compl.set_popup_completion(True)
	editable.set_completion(op_compl)
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
	# Modifier keys to ignore.
	mods = ["Control_L", "Control_R",
		"Shift_L", "Shift_R",
		"Alt_L", "Alt_R",
		"Meta_L", "Meta_R",
		"Up", "Down", "Left", "Right",
	]
	if keyname in mods:
		return True

	if (keyname == "Caps_Lock") or (keyname == "VoidSymbol"):
		global w
		kbwin = w.get_data("kbwin")
		if kbwin.get_visible():
			kbwin.hide()
		else:
			kbwin.show_all()
		return True

	if (keyname == "BackSpace") or (keyname == "Delete"):
		rpn.dostr("drop")
		do_update()
		return True

	if (keyname == "Escape"):
		rpn.dostr("clear")
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

def load_modules():
	moddir = os.path.expanduser("~/.vaprocalc")
	if not os.path.exists(moddir):
		os.mkdir(moddir)
	sys.path.append(moddir)
	mods = os.listdir(moddir)
	for mod in mods:
		if mod.endswith(".py"):
			__import__(mod[:-3])
	for mod in mods:
		if mod.endswith(".rpn"):
			rpn.dostr(open(os.path.join(moddir,mod)).read())

if __name__ == "__main__":
	load_modules()
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
	sv = gtk.TreeView(sm)
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

	w.set_data("kbwin", kb.KeyboardWindow())

	w.show_all()
	do_update()

	gtk.main()

