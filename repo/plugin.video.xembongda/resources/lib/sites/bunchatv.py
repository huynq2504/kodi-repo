import sys
import requests
import xbmcplugin
import xbmcgui
import xbmc
from datetime import datetime
import urllib.parse
import json
import utils
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse



def build_url(query):
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)

def get_base_url():
    short_url = "https://bit.ly/bunchatv"

    res = requests.get(short_url, allow_redirects=True, timeout=10)
    parsed = urlparse(res.url)

    return f"{parsed.scheme}://{parsed.netloc}"
    
BASE_URL = get_base_url()



ADDON_HANDLE = int(sys.argv[1])


def to_timestamp(date_str, time_str):
    try:
        dt = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
        return int(time.mktime(dt.timetuple()))
    except:
        return 0

def parse_match_datetime(date_text):
    # date_text dạng: "11:00 02/03"
    try:
        now = datetime.now()
        time_part, date_part = date_text.split()
        hour, minute = map(int, time_part.split(":"))
        day, month = map(int, date_part.split("/"))

        year = now.year
        dt = datetime(year, month, day, hour, minute)

        if dt < now and now.month == 12 and month == 1:
            dt = dt.replace(year=year + 1)

        return int(dt.timestamp())
    except:
        return 0

    
def list_matches(live_only=False, sport_slug="truc-tiep-bong-da-xoilac-tv"):

    url = f"{BASE_URL}/{sport_slug}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    items = []

    match_blocks = soup.find_all(
        "div",
        class_=lambda x: x and "grid-matches__item" in x
    )

    for block in match_blocks:

        link = block.find("a", href=lambda x: x and "/truc-tiep/" in x)
        if not link:
            continue
        title = link.get("title", "")
        match_url=link.get("href", "")

        href = link.get("href", "")
        match_id = href.rstrip("/").split("/")[-1]

        # 🔥 Tên giải
        league_tag = block.find("span", class_=lambda x: x and "text-ellipsis-max" in x)
        competition = league_tag.get_text(strip=True) if league_tag else ""

        # 🔥 LIVE hay không
        block_class = block.get("class", [])
        live = "stream_m_live" in block_class

        # 🔥 Thời gian
        match_time = 0

        date_tag = block.find("div", class_=lambda x: x and "grid-match__datef" in x)

        if date_tag:
            match_time = parse_match_datetime(date_tag.get_text(strip=True))


        # 🔥 Tên đội
        home_tag = block.find("span", class_=lambda x: x and "home-name" in x)
        away_tag = block.find("span", class_=lambda x: x and "away-name" in x)

        if not home_tag or not away_tag:
            continue

        home_name = home_tag.get_text(strip=True)
        away_name = away_tag.get_text(strip=True)

        # 🔥 Logo (lọc theo alt đúng tên đội cho chắc)
        home_logo = ""
        away_logo = ""

        imgs = block.find_all("img")
        for img in imgs:
            alt = img.get("alt", "")
            if alt == home_name:
                home_logo = img.get("src", "")
            if alt == away_name:
                away_logo = img.get("src", "")

        data = {
            "id": match_id,
            "match_id": match_id,
            "title": title,
            "match_time": int(match_time or 0),
            "competition": competition,
            "live": live,
            "home_team": {
                "name": home_name,
                "logo": home_logo
            },
            "away_team": {
                "name": away_name,
                "logo": away_logo
            }
        }


        li=utils.GetListItemFromData(data)
        
        # Tạo URL gọi lại addon để play

        play_url = build_url({
            "action": "play",
            "site":"bunchatv",
            "id": data["id"],
            "match_url": match_url
        })
        if(data["live"]):
            items.append((li, play_url))
        if(not live_only):
            xbmcplugin.addDirectoryItem(
                handle=ADDON_HANDLE,
                url=play_url,
                listitem=li,
                isFolder=False
            )
    if(not live_only):
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    else: 
        return items


def play_match(match_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    res = requests.get(f"{BASE_URL}{match_url}", headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    # tìm div có data-fileurl
    block = soup.find("div", attrs={"data-fileurl": True})

    if not block:
        return None

    stream_url = block.get("data-fileurl", "")

    if not stream_url:
        xbmcgui.Dialog().notification(
            "Thông báo",
            "Không có link xem",
            xbmcgui.NOTIFICATION_ERROR
        )
        return None

    # thêm header cho Kodi nếu cần
    stream_url += "|User-Agent=Mozilla/5.0"

    xbmc.log(f"Play stream: {stream_url}", xbmc.LOGINFO)

    li = xbmcgui.ListItem(path=stream_url)
    li.setProperty("IsPlayable", "true")

    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, li)

