#!/usr/bin/env python3

def _(string):
    """ Placeholder function later to be replaced by gettext """
    return string

def h_m_s_time(seconds):
    """ Convert time from seconds to h:m:s """

    # Some sites seem to provide duration as a float...?
    duration_total_s = int(seconds)
    duration_m, duration_s = divmod(duration_total_s, 60)
    duration_h, duration_m = divmod(duration_m, 60)

    return (duration_h, duration_m, duration_s)

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

