import xbmcgui
from datetime import datetime
import urllib.parse
import json
from PIL import Image
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

def get_merged_thumb(match_id, img_urls):
    """
    match_id: id trận đấu (để cache)
    img_urls: list 3 url ảnh
    return: đường dẫn file thumb đã ghép
    """

    addon = xbmcaddon.Addon()
    profile_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    cache_dir = os.path.join(profile_path, "thumb_cache")

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Tạo tên file theo hash để tránh trùng
    hash_name = hashlib.md5(match_id.encode()).hexdigest()
    output_path = os.path.join(cache_dir, f"{hash_name}.jpg")

    # Nếu đã tồn tại thì dùng luôn
    if os.path.exists(output_path):
        return output_path

    try:
        images = []

        for i, url in enumerate(img_urls):
            r = requests.get(url, timeout=10)
            img_path = os.path.join(cache_dir, f"{hash_name}_{i}.jpg")

            with open(img_path, "wb") as f:
                f.write(r.content)

            images.append(Image.open(img_path))

        # Resize về cùng chiều cao
        height = min(img.height for img in images)
        resized = []

        for img in images:
            w = int(img.width * height / img.height)
            resized.append(img.resize((w, height)))

        total_width = sum(img.width for img in resized)

        merged = Image.new("RGB", (total_width, height))

        x_offset = 0
        for img in resized:
            merged.paste(img, (x_offset, 0))
            x_offset += img.width

        merged.save(output_path, quality=85)

        return output_path

    except Exception as e:
        xbmc.log("Merge thumb error: " + str(e), xbmc.LOGERROR)
        return None
 
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