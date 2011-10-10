import gtk

keys = [['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BS'],
        ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
        ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter'],
        ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
        ['Ctrl', 'Alt', '\t\t\t\t', 'Alt', 'Ctrl'],
        ]

expand = ['BS', 'Tab', '\\', 'Caps', 'Enter', 'Shift', 'Ctrl', 'Alt', '\t\t\t\t']
          
class KeyboardWindow(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		vbox = gtk.VBox(True)
		self.add(vbox)
		bgcolour = gtk.gdk.color_parse("black")
		self.modify_bg(gtk.STATE_NORMAL, bgcolour)
		self.set_border_width(2)

		for row in keys:
		    hbox = gtk.HBox(False)
		    vbox.pack_start(hbox, True, True)
		    for key in row:
			b = gtk.Button(key)
			if key not in expand: b.set_size_request(40, 40)
			hbox.pack_start(b, True if key in expand else False, True)

if __name__ == "__main__":
	w = KeyboardWindow()
	w.show_all()
	gtk.main()

        
