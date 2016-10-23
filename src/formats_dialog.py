#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class FormatsDialog(Gtk.Dialog):
    
    def __init__(self, parent, listbox_row):
        Gtk.Dialog.__init__(self, "Formats Dialog", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        # self.set_default_size(200, 200)

        label = Gtk.Label("This is a placeholder label")

        # gives us a box representing the inside of the dialog
        self.box = self.get_content_area()
        self.box.add(label)


        # vertical box for a/v/both mode and format selection
        self.av_selection_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.box.pack_end(self.av_selection_box, 0, 0, 5)

        # a ComboBox for mode selection (a/v/both)
        self.mode_selection = listbox_row.mode_selection
        # this means the first item (Video and audio) will be pre-selected
        self.mode_selection.props.active = 0
        self.av_selection_box.pack_start(self.mode_selection, 0, 0, 0)

        self.format_selection = listbox_row.format_selection
        self.av_selection_box.pack_end(self.format_selection, 0, 0, 0)

        self.connect("delete-event", Gtk.main_quit)

        self.show_all()

