#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class Downloadable(Gtk.ListBoxRow):

    def __init__(self, main_window, this_item_dict):
        super(Gtk.ListBoxRow, self).__init__()

        self.main_window = main_window
        self.this_item_dict = this_item_dict
        self.url = this_item_dict["url"]
        self.info_dict = this_item_dict["ytdl_info_dict"]

        # Make rows non-selectable
        self.props.selectable = False

        # a horizontal box containing all else in this row
        # TODO: could use borders separating ListBox rows
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.hbox.props.margin = 5
        self.add(self.hbox)

        # a box for a cover picture; placeholder for now
        # TODO: cover picture
        self.cover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.hbox.pack_start(self.cover_box, 0, 0, 5)
        self.cover_placeholder = Gtk.Label("cover")
        self.cover_placeholder.props.xalign = 0.5
        self.cover_placeholder.props.yalign = 0.5
        self.cover_box.add(self.cover_placeholder)

        # middle part of the row; contains video info
        # TODO: nicer info
        self.video_title_label = Gtk.Label(self.info_dict["title"])
        # ellipsize characters at the end
        self.video_title_label.props.ellipsize = 3
        self.video_duration_label = Gtk.Label(self.info_dict["duration"])
        self.info_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.info_widget.pack_start(self.video_title_label, 1, 0, 0)
        self.info_widget.pack_start(self.video_duration_label, 0, 0, 0)
        self.hbox.pack_start(self.info_widget, 1, 1, 0)

        # and now a ComboBox for format selection
        # this one contains downloads with video and audio
        self.a_v_format_store = self.create_format_store("av")

        # this one contains downloads with video only
        self.video_format_store = self.create_format_store("v")

        # this one contains downloads with audio only
        self.audio_format_store = self.create_format_store("a")

        # a ComboBox containing available formats for current mode.
        # Creating the formats selection earlier because mode selection
        # requires it to exist
        self.format_selection = self.create_format_selection(initial=True)

        # self.hbox.pack_end(self.format_selection, 0, 0, 0)

        # # a failed popover test
        # self.app = Gtk.Application.new('org.mrksu.g_vid_dow', 0)

        # pop_button = Gtk.MenuButton()
        # pop_label = Gtk.Label("Pop")
        # pop_button.add(pop_label)

        # first_action = Gio.SimpleAction.new("first_action", None)
        # first_action.connect('activate', print)
        # self.app.add_action(first_action)

        # gmenu_model = Gio.Menu()
        # menu_section = Gio.Menu()
        # menu_section.append("First", "first_action")
        # menu_section.append("Second", None)
        # gmenu_model.append_section("Section", menu_section)
        # gmenu_model.append("Third", None)

        # popover = Gtk.Popover.new_from_model(pop_button, gmenu_model)
        # #popover.bind_model(gmenu_model, None)
        # pop_button.set_popover(popover)
        # self.hbox.pack_end(pop_button, 0, 0, 0)

        # # an attempt to have an options box appear after button click
        # format_opts_button = Gtk.Button()
        # format_opts_label = Gtk.Label("Opts")
        # format_opts_button.add(format_opts_label)
        # self.hbox.pack_end(format_opts_button, 0, 0, 0)

        # format_opts_button.connect("clicked", self.show_opts_box)


        # a ComboBox for mode selection (a/v/both)
        self.mode_store = Gtk.ListStore(str, str)
        self.mode_store.append(["av", "Video and audio"])
        self.mode_store.append(["v", "Video only"])
        self.mode_store.append(["a", "Audio only"])

        self.mode_selection = Gtk.ComboBox.new_with_model(self.mode_store)
        self.mode_selection.connect("changed", self.mode_has_been_selected)
        mode_renderer_text = Gtk.CellRendererText()
        self.mode_selection.pack_start(mode_renderer_text, True)
        self.mode_selection.add_attribute(mode_renderer_text, "text", 1)
        # this specifies which columns is used by get_active_id()
        self.mode_selection.props.id_column = 0
        # this means the first item (Video and audio) will be pre-selected
        self.mode_selection.props.active = 0
        # self.av_selection_box.pack_start(self.mode_selection, 0, 0, 0)

        # self.main_window.options_button = Gtk.Button("Formats")
        # self.main_window.options_button.connect("clicked", self.open_formats_dialog)
        # self.hbox.pack_end(self.options_button, 0, 0, 0)

        # a box containing the item's status info
        # TODO: turn into a dynamic thing containing e.g. download button
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.hbox.pack_end(self.status_box, 0, 0, 0)
        self.status_label_text = self.this_item_dict["status"]
        self.status_label = Gtk.Label(self.status_label_text)
        self.status_box.add(self.status_label)

        # a Gtk.Box Popover
        pop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pop_box.pack_start(self.mode_selection, 0, 0, 0)
        pop_box.pack_start(self.format_selection, 0, 0, 0)
        
        # ...from a button
        pop_button = Gtk.MenuButton()
        # Possible icons: document-properties, applications-system
        pop_icon = Gtk.Image.new_from_icon_name(
            "applications-system", Gtk.IconSize.BUTTON)
        pop_button.add(pop_icon)
        pop_button.props.tooltip_text = \
            "Select video and audio format to download"

        popover = Gtk.Popover.new(pop_button)
        popover.add(pop_box)
        pop_button.set_popover(popover)
        self.hbox.pack_end(pop_button, 0, 0, 0)

        # this is needed or else the popover appears empty
        pop_box.show_all()


    def get_current_mode(self):
        """returns one of 'av', 'v', 'a'"""
        mode = self.mode_selection.props.active_id
        return mode

    def mode_has_been_selected(self, combo):

        mode = self.get_current_mode()

        if mode == "av":
            store = self.a_v_format_store
        elif mode == "v":
            store = self.video_format_store
        elif mode == "a":
            store = self.audio_format_store
        else:
            exit("Error: Unknown mode {}".format(mode))

        self.format_selection.clear()
        self.format_selection.set_model(store)

        format_renderer_text = Gtk.CellRendererText()
        self.format_selection.pack_start(format_renderer_text, True)
        # that '1' at the end tells which list item should be displayed in the dropdown
        self.format_selection.add_attribute(format_renderer_text, "text", 1)
        # this specifies which columns is used by get_active_id()
        self.format_selection.props.id_column = 0

        # the last available item should be pre-selected; let's hope
        # it always means the highest quality
        last_item = len(store) - 1
        self.format_selection.props.active = last_item

    def create_format_selection(self, initial=False):
        if initial:
            mode = "av"
        else:
            mode = self.get_current_mode()

        if mode == "av":
            store = self.a_v_format_store
        elif mode == "v":
            store = self.video_format_store
        elif mode == "a":
            store = self.audio_format_store
        else:
            exit("Unknown media mode: {}".format(mode))

        format_selection = Gtk.ComboBox.new_with_model(store)
        format_selection.connect("changed", self.format_has_been_selected)
        format_renderer_text = Gtk.CellRendererText()
        format_selection.pack_start(format_renderer_text, True)
        # that '1' at the end tells which list item should be displayed in the dropdown
        format_selection.add_attribute(format_renderer_text, "text", 1)
        # this specifies which columns is used by get_active_id()
        format_selection.props.id_column = 0

        # the last available item should be pre-selected; let's hope
        # it always means the highest quality
        last_item = len(store) - 1
        format_selection.props.active = last_item

        return format_selection

    def format_has_been_selected(self, combo):
        self.this_item_dict["download_format_id"] = combo.props.active_id

    def create_format_store(self, mode):

        if mode == "av":
            # this one contains downloads with video and audio
            format_store = Gtk.ListStore(str, str)

            for av_format in self.this_item_dict["available_a_v_s"]:
                format_id = av_format["format_id"]
                format_name = av_format["format"]
                format_store.append([format_id, format_name])

        elif mode == "v":
            # this one contains downloads with video only
            format_store = Gtk.ListStore(str, str)

            for video_format in self.this_item_dict["available_video_s"]:
                format_id = video_format["format_id"]
                format_name = video_format["format"]
                format_store.append([format_id, format_name])

        elif mode == "a":
            # this one contains downloads with audio only
            format_store = Gtk.ListStore(str, str)

            for audio_format in self.this_item_dict["available_audio_s"]:
                format_id = audio_format["format_id"]
                format_name = audio_format["format"]
                format_store.append([format_id, format_name])

        else:
            return None

        return format_store

