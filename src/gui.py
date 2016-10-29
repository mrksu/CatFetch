#!/usr/bin/env python3

from pprint import pprint

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import youtube_dl
from ytdl_wrapper import *
from downloadables import Downloadable

class MainWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self, title="Video Downloader")

        # a list containing one dictionary per video entered by the user
        # structure:
        # [
        #  {
        #   "url": "https://...",
        #   "ytdl_info_dict": <dict>,
        #   "listbox_row": <ListBoxRow>,
        #   "status": "waiting" or "downloaded"
        #  }
        # ]
        self.items_list = []

        self.set_default_size(400, 400)
        self.set_border_width(10)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = "Video Downloader"
        self.set_titlebar(self.headerbar)


        # TODO: Add a button for removing all downloaded items from list


        # The Download button
        # possible icons: document-save, go-down, emblem-downloads
        self.download_button = Gtk.Button.new_from_icon_name(
            "document-save", Gtk.IconSize.BUTTON)
        self.download_button.connect("clicked", self.launch_download)
        self.download_button.props.sensitive = False
        self.download_button.props.tooltip_text = \
            "Download all waiting videos"
        self.headerbar.pack_end(self.download_button)

        # The Paste button
        self.paste_button = Gtk.Button("Paste")
        self.paste_button.connect("clicked", self.url_pasted)
        self.paste_button.props.tooltip_text = \
            "Paste video address from the clipboard"
        self.headerbar.pack_start(self.paste_button)

        self.outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, 
            spacing=10)
        self.add(self.outer_box)

        ### replaced by the 'Paste' button
        ## self.url_line_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ## self.outer_box.add(self.url_line_box)

        ## self.url_label = Gtk.Label("Video address:")
        ## self.url_line_box.pack_start(self.url_label, 0, 0, 0)

        ## self.url_entry = Gtk.Entry()
        ## self.url_entry.grab_focus()
        ## self.url_line_box.pack_start(self.url_entry, 1, 1, 0)

        ## self.url_evaluate_button = Gtk.Button()
        ## self.url_evaluate_label = Gtk.Label("Add")
        ## self.url_evaluate_button.add(self.url_evaluate_label)
        ## self.url_evaluate_button.connect("clicked", self.url_evaluate)
        ## self.url_line_box.pack_start(self.url_evaluate_button, 0, 0, 0)

        # a placeholder if there aren't any videos to show
        # TODO: find out why this doesn't work or find a different way
        listbox_placeholder = Gtk.Label(
            "Paste videos from the clipboard using the 'Paste' button")

        # a ListBox containing added videos to be downloaded
        self.downloadables_listbox = Gtk.ListBox()
        self.downloadables_listbox.set_placeholder(listbox_placeholder)
        self.outer_box.add(self.downloadables_listbox)


    def launch_download(self, widget):
        for item in self.items_list:
            download_vid(item["url"], item["download_format_id"])

    def url_pasted(self, widget):
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = self.clipboard.wait_for_text()

        if text != None:
            self.url_evaluate(text)
        else:
            print("No text in the clipboard!")

    def url_evaluate(self, text):
        # self.url_entry.set_progress_fraction(0.4)
        # self.url_entry.props.sensitive = False
        # url_entered = self.url_entry.props.text
        url_entered = text

        try:
            ytdl_info_dict = extract_vid_info(url_entered)
            # pprint(self.ytdl_info_dict)
        except youtube_dl.utils.DownloadError:
            # Show an error dialog
            self.invalid_url_dialog(url_entered)
            return

        available_a_v_s = filter(get_a_v_list, ytdl_info_dict["formats"])
        available_video_s = filter(get_video_list, ytdl_info_dict["formats"])
        available_audio_s = filter(get_audio_list, ytdl_info_dict["formats"])

        self.items_list.append({
            "url": url_entered,
            "ytdl_info_dict": ytdl_info_dict,
            "available_a_v_s": available_a_v_s,
            "available_video_s": available_video_s,
            "available_audio_s": available_audio_s,
            "status": "waiting"
        })

        listbox_row = Downloadable(self, self.items_list[-1])

        self.items_list[-1]["listbox_row"] = listbox_row

        self.downloadables_listbox.add(listbox_row)
        self.downloadables_listbox.show_all()

        ## video_title = ytdl_info_dict["title"]
        ## video_description = ytdl_info_dict["description"]
        ## video_duration = ytdl_info_dict["duration"]
        ## video_website = ytdl_info_dict["extractor_key"]
        ## video_thumbnail_url = ytdl_info_dict["thumbnail"]
        ## video_uploader = ytdl_info_dict["uploader"]

        ## self.url_entry.props.text = ""
        ## self.url_entry.props.sensitive = True

        self.download_button.props.sensitive = True

    def downloadables_refresh(self, items_list):
        self.outer_box.remove(self.downloadables_listbox)
        self.downloadables_listbox = Gtk.ListBox()

        for item in items_list:
            pprint(item["listbox_row"])
            self.downloadables_listbox.add(item.get("listbox_row"))

        self.outer_box.add(self.downloadables_listbox)
        self.downloadables_listbox.show_all()

    def invalid_url_dialog(self, url):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                 Gtk.ButtonsType.CANCEL, "Invalid address")
        dialog.format_secondary_text(
                 "The address you entered is not downloadable:\n\n"
                 "{}".format(url))
        dialog.run()
        dialog.destroy()



if __name__ == "__main__":
    main_win = MainWindow()
    main_win.connect("delete-event", Gtk.main_quit)
    main_win.show_all()
    Gtk.main()

