import xbmcgui
from datetime import datetime
import urllib.parse
import json
import xbmcaddon
import xbmcplugin
import sys
import xbmc
import xbmcvfs
import os
import hashlib
import requests

# =========================
# Timestamp hôm nay (UTC)
# =========================
def today_timestamp():
    from datetime import datetime, timezone
    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    return int(start.timestamp())

def format_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d-%m-%Y %H:%M")

# =========================
# Convert timestamp sang giờ VN
# =========================
def timestamp_to_vn_time(timestamp):
    return datetime.fromtimestamp(
        timestamp,
        timezone.utc
    ).astimezone().strftime("%d/%m/%Y %H:%M:%S")

def iso_to_timestamp(timestr):
    try:
        dt = datetime.fromisoformat(timestr.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except:
        return 0


def GetListItemFromData(data):
    # Lấy logo
    thumb = data["home_team"]["logo"]

    # Tạo ListItem
    if data['match_time']:
        time_str = f"[COLOR yellow]{format_time(data['match_time'])}[/COLOR]"
    else:
        time_str = ""
    title = f"[B]{data['title']} {time_str}[/B] - {data['competition']}"
    
    if data['live']:
        title=f"[B][COLOR red]● LIVE[/COLOR][/B] " + title
        
    li = xbmcgui.ListItem(label=title)
   
    #img_list = [data["home_team"]["logo"], data["away_team"]["logo"], data["logo_league"]]

    #thumb_path = get_merged_thumb(data["match_id"], img_list)

    li.setArt({
        "thumb": thumb,
        "icon": thumb,
    })

    li.setInfo("video", {
        "title": title,
        "plot": f"[B][COLOR yellow]{data['competition']}[/COLOR][/B]\n[B]{data['title']}[/B]\n[B][COLOR yellow]Thời gian: {time_str}[/COLOR][/B]"
    })
    li.setProperty("IsPlayable", "true")
    return li