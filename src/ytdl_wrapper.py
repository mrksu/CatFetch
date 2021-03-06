#!/usr/bin/env python3
from sys import argv
from pprint import pprint
import youtube_dl

# ydl_opts = {}
# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#     ydl.download(["https://www.youtube.com/watch?v=ylzkOPBrdx0"])

## *prints* formats info:
# ydl_opts = {"listformats": True}
# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#     ydl.download(["https://www.youtube.com/watch?v=ylzkOPBrdx0"])


class MyLogger(object):
    """
    Used by YoutubeDL to pass various information into. There are three types
    of messages: debug (most common, just tells what YoutubeDL is doing ATM),
    warning and error. For now, we just print them to the stdout.
    """
    # TODO: Find a more meaningful way to handle log messages
    def debug(self, msg):
        print("YDL DEBUG: {}".format(msg))

    def warning(self, msg):
        print("YDL WARNING: {}".format(msg))

    def error(self, msg):
        print("YDL ERROR: {}".format(msg))


def my_hook(hook_dict):
    """
    Actions to be launched on various YoutubeDL events can be specified here
    """
    # TODO: Find a more meaningful use for the events
    if hook_dict['status'] == 'finished':
        print('my_hook: finished')
        print("filename: {}".format(hook_dict["filename"]))
    if hook_dict['status'] == 'downloading':
        print("my_hook: downloading")
        # print("downloaded_bytes: {}".format(hook_dict["downloaded_bytes"]))
        # print("total_bytes: {}".format(hook_dict["total_bytes"]))
        # print("elapsed: {}".format(hook_dict["elapsed"]))
        # print("eta: {}".format(hook_dict["eta"]))
        # print("speed: {}".format(hook_dict["speed"]))
    if hook_dict['status'] == "error":
        print("my_hook: error")


# ydl_opts = {
#     'format': 'bestaudio/best',
#     'postprocessors': [{
#         'key': 'FFmpegExtractAudio',
#         'preferredcodec': 'mp3',
#         'preferredquality': '192',
#     }],
#     'logger': MyLogger(),
#     'progress_hooks': [my_hook],
# }

# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#     ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc'])


def extract_vid_info(url):
    """
    Lets YoutubeDL check out the given address and returns an 'info dict'
    containing all data we can get about the video
    """
    info_ydl_opts = {
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
        # this is so that we get information about the best possible format
        # on the first call and only go through the dictionary to find
        # lower quality formats
        "format": "best"
    }

    info_ydl = youtube_dl.YoutubeDL(info_ydl_opts)
    # this creates a huge dict containing detailed video info
    info_dict = info_ydl.extract_info(url, download=False)

    # this prints format info to stdout, the way youtube-dl does. not really useful.
    # ydl.list_formats(info_dict)

    return info_dict

def pprint_info_dict(url):
    """
    Pretty-prints extracted information about the given (video) address
    to the terminal stdout
    """
    try:
        info_dict = extract_vid_info(url)
    except youtube_dl.utils.DownloadError:
        exit("Website not supported")

    pprint(info_dict)

def download_vid(url, vid_format, where):
    """
    Orders YoutubeDL to start downloading the video from an address ('url')
    and in a format specified by id ('vid_format') into location ('where')
    """
    dow_ydl_opts = {
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
        "format": vid_format,
        "outtmpl": where
    }

    dow_ydl = youtube_dl.YoutubeDL(dow_ydl_opts)

    dow_ydl.download([url])


# info_dict = extract_vid_info("https://www.youtube.com/watch?v=ylzkOPBrdx0")



if __name__ == "__main__":

    if len(argv) == 3 and argv[1] == "pprint":
        pprint_info_dict(argv[2])
    else:
        pass

