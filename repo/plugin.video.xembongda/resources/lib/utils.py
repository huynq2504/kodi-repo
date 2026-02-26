import xbmcgui
from datetime import datetime
import urllib.parse
import json

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
    title = f"[B]{data['title']} [COLOR red]{format_time(data['match_time'])}[/COLOR][/B] - {data['competition']}" 
    if data['live']:
        title=f"[B][COLOR red]● LIVE[/COLOR][/B] " + title
        
    li = xbmcgui.ListItem(label=title)
   
    li.setArt({
        "thumb": thumb,
        "icon": thumb,
    })

    li.setInfo("video", {
        "title": title,
        "plot": f"{data['competition']}\n{data['title']}\nThời gian: {format_time(data['match_time'])}"
    })
    li.setProperty("IsPlayable", "true")
    return li