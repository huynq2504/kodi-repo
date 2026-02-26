import sys
import requests
import xbmcplugin
import xbmcgui
import xbmc
from datetime import datetime
import urllib.parse
import json
import utils


def build_url(query):
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)


BASE = "https://api-ck.686868.me/api/livestream/client"


ADDON_HANDLE = int(sys.argv[1])




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
    detail = detail_res.json()["data"]

    streams = []
    labels = []

    # ===== STREAM CHÍNH =====
    main_name = detail["commentator_info"]["full_name"].strip()
    main_urls = json.loads(detail["stream_urls"])

    for url in main_urls:
        streams.append(url)

        if ".m3u8" in url:
            labels.append(f"{main_name} (m3u8)")
        elif ".flv" in url:
            labels.append(f"{main_name} (flv)")
        else:
            labels.append(main_name)

    # ===== STREAM DỰ PHÒNG =====
    if "otherSimilarStreams" in detail:
        for other in detail["otherSimilarStreams"]:

            other_name = other["commentator_info"]["full_name"].strip()
            other_urls = json.loads(other["stream_urls"])

            for url in other_urls:
                streams.append(url)

                if ".m3u8" in url:
                    labels.append(f"{other_name} (m3u8)")
                elif ".flv" in url:
                    labels.append(f"{other_name} (flv)")
                else:
                    labels.append(other_name)

    if not streams:
        xbmcgui.Dialog().notification(
            "Thông báo",
            "Không có link xem",
            xbmcgui.NOTIFICATION_ERROR
        )
        return

    # ===== POPUP CHỌN LINK =====
    dialog = xbmcgui.Dialog()
    index = dialog.select("Chọn người bình luận", labels)

    if index == -1:
        return

    stream = streams[index]

    xbmc.log(f"Play stream: {stream}", xbmc.LOGINFO)

    li = xbmcgui.ListItem(path=stream)
    li.setProperty("IsPlayable", "true")

    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, li)

# =========================
# Parse danh sách trận
# =========================
def list_matches(live_only=False):
    url = BASE + "/all?date=" + str(utils.today_timestamp()) + "&sport_type=0"
    xbmc.log(url, xbmc.LOGINFO)
    items = []
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
        li=utils.GetListItemFromData(data)
        
        # Tạo URL gọi lại addon để play

        play_url = build_url({
            "action": "play",
            "site":"cakhiatv",
            "id": data["id"]
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