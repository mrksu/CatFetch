#!/usr/bin/env python3

from threading import Thread

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

from ytdl_wrapper import *
from basic_functions import _

class Downloadable(Gtk.ListBoxRow):
    """
    Class used to build individual rows in the main window's ListBox.
    Each item is based on extracted video info; contains a cover image,
    textual information, buttons for selecting video format, downloading, etc.
    """

    def __init__(self, main_window, this_item_dict):
        super(Gtk.ListBoxRow, self).__init__()

        self.main_window = main_window
        self.this_item_dict = this_item_dict
        self.url = this_item_dict["url"]
        self.info_dict = this_item_dict["ytdl_info_dict"]
        
        # Directory where videos are saved. For now the user's Downloads dir.
        # TODO: Make the directory cinfigurable
        self.default_download_dir = \
            GLib.get_user_special_dir(GLib.USER_DIRECTORY_DOWNLOAD)
        self.selected_download_dir = self.default_download_dir

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
        self.video_title_label = Gtk.Label()
        # Video title as a label
        # "size='large'" could also be added
        self.video_title_label.set_markup(
            "<span weight='bold'>{}</span>".format(self.info_dict["title"])
        )
        # ellipsize characters at the end
        self.video_title_label.props.ellipsize = 3
        # align text to the left
        self.video_title_label.props.xalign = 0
        
        self.info_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.info_widget.pack_start(self.video_title_label, 1, 0, 0)
        
        # This box contains various video info and is horizontally aligned
        self.video_details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # For some videos, time cannot be extracted
        if "duration" in self.info_dict:
            # Convert time from seconds to h:m:s
            dur_h, dur_m, dur_s = h_m_s_time(self.info_dict["duration"])

            self.video_duration_label = Gtk.Label(
                # {:02d} means numbers are 2 digits long and padded with 0s if nec.
                "{}:{:02d}:{:02d}".format(dur_h, dur_m, dur_s)
            )
        else:
            self.video_duration_label = Gtk.Label("--:--:--")
        
        # align text to the left
        self.video_duration_label.props.xalign = 0

        self.video_details_box.pack_start(self.video_duration_label, 0, 0, 0)
        
        # separator: a label containing just " | "
        self.video_details_box.pack_start(separator(), 0, 0, 0)
        
        # label displaying the website hosting the video
        if "extractor_key" in self.info_dict:
            video_hosting = self.info_dict["extractor_key"]
        # not sure if all websites provide the more readable extractor_key
        else:
            video_hosting = self.info_dict["extractor"]
        
        video_hosting_label = Gtk.Label(video_hosting)
        video_hosting_label.props.xalign = 0
        self.video_details_box.pack_start(video_hosting_label, 0, 0, 0)
        self.video_details_box.pack_start(separator(), 0, 0, 0)
        
        # label showing currently selected video format; empty by default:
        # will be filled in by the self.show_selected_format function
        self.selected_format_label = Gtk.Label("-")
        self.selected_format_label.props.xalign = 0
        # ellipsize characters at the end
        self.selected_format_label.props.ellipsize = 3
        self.video_details_box.pack_start(self.selected_format_label, 0, 0, 0)

        self.info_widget.pack_start(self.video_details_box, 0, 0, 0)
        
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
        self.mode_store.append(["av", _("Video and audio")])
        self.mode_store.append(["v", _("Video only")])
        self.mode_store.append(["a", _("Audio only")])

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
        
        # If there are only a/v formats available, disable the dropdown
        # TODO: Do this more pleasantly, also avoiding creation of stores
        if len(self.this_item_dict["available_audio_s"]) == 0 \
        and len(self.this_item_dict["available_video_s"]) == 0:
            self.mode_selection.props.sensitive = False
        else:
            pass

        # self.main_window.options_button = Gtk.Button("Formats")
        # self.main_window.options_button.connect("clicked", self.open_formats_dialog)
        # self.hbox.pack_end(self.options_button, 0, 0, 0)

        # a box containing the item's status info
        # TODO: turn into a dynamic thing containing e.g. download button
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.hbox.pack_end(self.status_box, 0, 0, 0)
        # self.status_label_text = self.this_item_dict["status"]
        # self.status_label = Gtk.Label(self.status_label_text)
        # self.status_box.add(self.status_label)

        # A Download button
        self.download_item_button = Gtk.Button.new_from_icon_name(
            "document-save-symbolic", Gtk.IconSize.BUTTON)
        self.download_item_button.connect("clicked", self.download_item)
        self.download_item_button.props.tooltip_text = \
            _("Download this video")
        self.status_box.pack_start(self.download_item_button, 1, 1, 0)

        # # Button combining download and format
        ### Need to figure out how to create a menu for this to work; TODO
        # download_icon = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON)
        # self.download_and_format_button = Gtk.MenuToolButton(download_icon, None)
        # self.download_and_format_button.set_menu(Gtk.Popover())
        # self.hbox.pack_end(self.download_and_format_button, 0, 0, 0)

        # a Gtk.Box Popover
        pop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        pop_box.props.margin = 10
        
        pop_mode_label = Gtk.Label(_("Mode:"))
        pop_mode_label.props.xalign = 0
        pop_format_label = Gtk.Label(_("Format:"))
        pop_format_label.props.xalign = 0
        pop_destination_label = Gtk.Label(_("Where to save:"))
        pop_destination_label.props.xalign = 0
        
        # Button used to open the filechooser (dir_chooser)
        self.destination_button = Gtk.Button()
        self.destination_button.connect("clicked", self.set_download_dir)
        # tooltip show the whole path
        self.destination_button.props.tooltip_text = self.selected_download_dir
        self.destination_label = Gtk.Label(self.selected_download_dir)
        # ellipsize in the middle
        self.destination_label.props.ellipsize = 2
        # Maximum width which is displayed fo the directory;
        # it should be roughly similar to how long mode and format description
        # are so 25 seems reasonable
        self.destination_label.props.max_width_chars = 25
        self.destination_button.add(self.destination_label)
        
        pop_box.pack_start(pop_mode_label, 0, 0, 0)
        pop_box.pack_start(self.mode_selection, 0, 0, 0)
        pop_box.pack_start(pop_format_label, 0, 0, 0)
        pop_box.pack_start(self.format_selection, 0, 0, 0)
        pop_box.pack_start(pop_destination_label, 0, 0, 0)
        pop_box.pack_start(self.destination_button, 0, 0, 0)
        
        # ...from a button
        pop_button = Gtk.MenuButton()
        # Possible icons: document-properties, applications-system
        pop_icon = Gtk.Image.new_from_icon_name(
            "document-properties-symbolic", Gtk.IconSize.BUTTON)
        pop_button.add(pop_icon)
        pop_button.props.tooltip_text = \
            _("Select video and audio format to download")

        popover = Gtk.Popover.new(pop_button)
        popover.add(pop_box)
        pop_button.set_popover(popover)
        self.hbox.pack_end(pop_button, 0, 0, 0)

        # this is needed or else the popover appears empty
        pop_box.show_all()


    def get_current_mode(self):
        """
        Returns currently selected 'mode' to be downloaded:
        one of 'av', 'v', 'a'.
        """

        mode = self.mode_selection.props.active_id
        return mode

    def mode_has_been_selected(self, combo):
        """
        Runs when user selects video 'mode' (a/v/both) from menu.
        Adjusts the specific formats menu according to 'mode'.
        """

        selected_mode = self.get_current_mode()

        if selected_mode == "av":
            store = self.a_v_format_store
        elif selected_mode == "v":
            store = self.video_format_store
        elif selected_mode == "a":
            store = self.audio_format_store
        else:
            exit("Error: Unknown mode {}".format(selected_mode))

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
        """
        Creates a ComboBox listing available formats, according
        to the currently selcted video 'mode'.
        """

        # TODO: Get rid of this 'initial' checking; can be done better
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
        """
        When the user selects a video format from list, write the format ID
        to this item's info dict so that it can be used for download.
        """

        selected_format = combo.props.active_id
        self.this_item_dict["download_format_id"] = selected_format
        # update the label displaying currently selected format
        self.show_selected_format(selected_format)

    def create_format_store(self, mode):
        """
        Returns a GTK 'ListStore' containing video formats for given 'mode',
        in the form of (str: format_id, str: format_name).
        """

        # TODO: Make format names more human-readable and useful

        if mode == "av":
            # this one contains downloads with video and audio
            format_store = Gtk.ListStore(str, str)

            for av_format in self.this_item_dict["available_a_v_s"]:
                format_id = av_format["format_id"]
                format_name = human_readable_format(
                    format_id, self.info_dict, short=True
                )
                format_store.append([format_id, format_name])

        elif mode == "v":
            # this one contains downloads with video only
            format_store = Gtk.ListStore(str, str)

            for video_format in self.this_item_dict["available_video_s"]:
                format_id = video_format["format_id"]
                format_name = human_readable_format(
                    format_id, self.info_dict, short=True
                )
                format_store.append([format_id, format_name])

        elif mode == "a":
            # this one contains downloads with audio only
            format_store = Gtk.ListStore(str, str)

            for audio_format in self.this_item_dict["available_audio_s"]:
                format_id = audio_format["format_id"]
                format_name = human_readable_format(
                    format_id, self.info_dict, short=True
                )
                format_store.append([format_id, format_name])

        else:
            return None

        return format_store

    def download_item(self, widget):
        """
        Starts downloading this video based on selected 'format ID'
        obtained from this item's info dict.
        """

        widget.props.sensitive = False

        url = self.url
        format_id = self.this_item_dict["download_format_id"]
        format_dict = get_format_by_id(format_id, self.info_dict)
        
        # Default dir or selected by the popover button
        downloads_dir = self.selected_download_dir
        
        title = self.info_dict["title"]
        extension = format_dict["ext"]

        # This is where we create the actual download path and filename
        where = "{}/{} (fmt {}).{}".format(
            downloads_dir, title, format_id, extension)

        # download_vid(url, format_id, where)
        thread = Thread(target=download_vid, args=(url, format_id, where,))
        # making this a daemon so that it stops when closing application window
        thread.daemon = True
        thread.start()
    
    def show_selected_format(self, format_id):
        hum_readable = human_readable_format(format_id, self.info_dict)
        self.selected_format_label.set_markup("<b>{}</b>".format(hum_readable))
    
    def set_download_dir(self, widget):
        """
        Runs the filechooser and updates the self.selected_download_dir variable
        """
        self.main_window.dir_chooser(self)
        destination_text = self.selected_download_dir
        self.destination_label.set_text(destination_text)
        self.destination_button.props.tooltip_text = destination_text



def h_m_s_time(seconds):
    """ Convert time from seconds to h:m:s """

    # Some sites seem to provide duration as a float...?
    duration_total_s = int(seconds)
    duration_m, duration_s = divmod(duration_total_s, 60)
    duration_h, duration_m = divmod(duration_m, 60)
    
    return (duration_h, duration_m, duration_s)

def separator():
    label = Gtk.Label(" | ")
    label.props.xalign = 0
    return label

def get_format_by_id(format_id, ytdl_info_dict):
    """
    Searches given ytdl_info_dict and returns the (first) format dict that
    has the given format_id
    """
    for format_dict in ytdl_info_dict["formats"]:
        if format_dict["format_id"] == format_id:
            return format_dict
        else:
            pass
    
    # if no correct format dict is found:
    return None

def human_readable_format(format_id, ytdl_info_dict, short=False):
    """
    Returns a string containing detailed, human-readable description
    of the provided Format ID based on the provided ytdl_info_dict.
    Accepts short=True as an optional argument, mainly for the popover menu.
    """
    format_dict = get_format_by_id(format_id, ytdl_info_dict)
    
    ext = format_dict["ext"] if "ext" in format_dict else "?"

    if "filesize" in format_dict and format_dict["filesize"] == "none":
        # let's convert size to MiB
        filesize = format_dict["filesize"] / 1048576
    else:
        filesize = "?"
    
    if "vcodec" in format_dict and format_dict["vcodec"] != "none":
        video = True
        vcodec = format_dict["vcodec"]
        
        if "resolution" in format_dict:
            resolution = format_dict["resolution"]
        elif "width" in format_dict and "height" in format_dict:
            width = format_dict["width"]
            height = format_dict["height"]
            resolution = "{}x{}".format(width, height)
        else:
            resolution = "?"
        
    else:
        video = False
    
    if "acodec" in format_dict and format_dict["acodec"] != "none":
        audio = True
        acodec = format_dict["acodec"]
        abr = format_dict["abr"] if "abr" in format_dict else "?"
    else:
        audio = False
    
    if video and audio:
        if short:
            h_r_format = "{}, {}, {}".format(resolution, vcodec, acodec)
        else:
            h_r_format = "{} {}, {}, *.{}".format(
                resolution, vcodec, acodec, ext
            )
    elif video:
        if short:
            h_r_format = "{}, {}, *.{}".format(resolution, vcodec, ext)
        else:
            h_r_format = "{} {}, *.{}".format(
                resolution, vcodec, ext
            )
    elif audio:
        if short:
            h_r_format = "{} kb/s, {}, *.{}".format(abr, acodec, ext)
        else:
            h_r_format = "{} kb/s {}, *.{}".format(
                abr, acodec, ext
            )
    # Some websites provide very little information
    else:
        fallback_name = format_dict["format"] if "format" in format_dict \
            else format_dict["format_id"]
        
        h_r_format = "{}, {} MiB, *.{}".format(
            fallback_name, filesize, ext
        )
    
    return h_r_format

