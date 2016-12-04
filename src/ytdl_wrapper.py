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
    def debug(self, msg):
        print("YDL DEBUG: {}".format(msg))

    def warning(self, msg):
        print("YDL WARNING: {}".format(msg))

    def error(self, msg):
        print("YDL ERROR: {}".format(msg))


def my_hook(hook_dict):
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

# *extracts* formats info:
def extract_vid_info(url):
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

    try:
        info_dict = extract_vid_info(url)
    except youtube_dl.utils.DownloadError:
        exit("Website not supported")

    pprint(info_dict)

def download_vid(url, vid_format, where):
    dow_ydl_opts = {
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
        "format": vid_format,
        "outtmpl": where
    }

    dow_ydl = youtube_dl.YoutubeDL(dow_ydl_opts)

    dow_ydl.download([url])


# info_dict = extract_vid_info("https://www.youtube.com/watch?v=ylzkOPBrdx0")

def is_audio_only(formats_item):
    """
    Returns True if the given media format (a dict) is audio-only (no video)
    """
    # Some websites provide little information; by default evaluate to a/v
    if not "acodec" in formats_item or not "vcodec" in formats_item:
        return False
    elif formats_item["acodec"] != "none" and formats_item["vcodec"] == "none":
        return True
    else:
        return False

def is_video_only(formats_item):
    """
    Returns True if the given media format (a dict) is video-only (no audio)
    """
    # Some websites provide little information; by default evaluate to a/v
    if not "acodec" in formats_item or not "vcodec" in formats_item:
        return False
    elif formats_item["acodec"] == "none" and formats_item["vcodec"] != "none":
        return True
    else:
        return False

def is_both_a_v(formats_item):
    """
    Returns True if the given media format (a dict) includes both audio
    and video; this is also True if we can't extract enough information
    to decide -- it is a sensible default
    """
    # Some websites provide little information; by default evaluate to a/v
    if not "acodec" in formats_item or not "vcodec" in formats_item:
        return True
    elif formats_item["acodec"] != "none" and formats_item["vcodec"] != "none":
        return True
    else:
        return False


if __name__ == "__main__":

    if len(argv) == 3 and argv[1] == "pprint":
        pprint_info_dict(argv[2])
    else:
        cmdline_download()

