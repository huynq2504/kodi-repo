import sys
import requests
import xbmcplugin
import xbmcgui
import xbmc
from datetime import datetime
import urllib.parse
import json

def build_url(query):
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)


BASE = "https://api-ck.686868.me/api/livestream/client"


ADDON_HANDLE = int(sys.argv[1])


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


# =========================
# Lấy HTML
# =========================
def get_html(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        return response.text
    except Exception as e:
        print("Lỗi lấy HTML:", str(e))
        return None

def play_match(match_id):
    xbmc.log(f"{BASE}/detail/{match_id}", xbmc.LOGINFO)
    detail_res = requests.get(f"{BASE}/detail/{match_id}")
    detail = detail_res.json()

    urls = json.loads(detail["data"]["stream_urls"])
    xbmc.log(json.dumps(urls, indent=2), xbmc.LOGINFO)
    # ưu tiên m3u8
    stream = next((u for u in urls if ".m3u8" in u), urls[0])

    li = xbmcgui.ListItem(path=stream)
    li.setProperty("IsPlayable", "true")

    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, li)

# =========================
# Parse danh sách trận
# =========================
def list_matches():
    url = BASE + "/all?date=" + str(today_timestamp()) + "&sport_type=0"
    xbmc.log(url, xbmc.LOGINFO)
    try:
        res = requests.get(url)
        data = res.json()
    except Exception as e:
        log("API error: " + str(e))
        return

    matches = data.get("data", [])

    for match in matches:
        data = {
            "id": match.get("id", ""),
            "match_id": match.get("match_id", ""),
            "title": match.get("title", "No title"),
            "match_time": match.get("match_time", 0),
            "competition": match["competition"].get("name"),
            "live": match.get("is_live", False),
            "home_team": {
                "name": match["home_info"].get("name"),
                "logo": match["home_info"].get("logo")
            },
            "away_team": {
                "name": match["away_info"].get("name"),
                "logo": match["away_info"].get("logo")
            }
        }

        # Lấy logo
        thumb = data["home_team"]["logo"]

        # Tạo ListItem
        title = f"{data['title']} [{format_time(data['match_time'])}]" 
        if data['live']:
            title=f"[COLOR red]● LIVE[/COLOR] " + title
            
        li = xbmcgui.ListItem(label=title)
       
        li.setArt({
            "thumb": thumb,
            "icon": thumb,
        })

        li.setInfo("video", {
            "title": title,
            "plot": f"{data['title']}\n{data['competition']}\nThời gian: {format_time(data['match_time'])}"
        })
        # Tạo URL gọi lại addon để play

        play_url = build_url({
            "action": "play",
            "site":"cakhiatv",
            "id": data["id"]
        })


        li.setProperty("IsPlayable", "true")

        xbmcplugin.addDirectoryItem(
            handle=ADDON_HANDLE,
            url=play_url,
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(ADDON_HANDLE)