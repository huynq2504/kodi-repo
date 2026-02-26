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


BASE = "https://api19.colatv88xd.cc/api"


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
    try:
        # gọi API detail
        url = f"{BASE}/detail/{match_id}"
        xbmc.log("Fetch stream: " + url, xbmc.LOGINFO)

        res = requests.get(url, timeout=10)
        detail = res.json()

        # parse JSON string stream_urls
        stream_urls_str = detail.get("data", {}).get("stream_urls", "[]")
        urls = json.loads(stream_urls_str)

        if not urls:
            xbmc.log("No stream found", xbmc.LOGERROR)
            xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem())
            return

        # ưu tiên m3u8
        stream = next((u for u in urls if ".m3u8" in u), urls[0])

        xbmc.log("Play stream: " + stream, xbmc.LOGINFO)

        # play stream
        li = xbmcgui.ListItem(path=stream)
        li.setProperty("IsPlayable", "true")

        xbmcplugin.setResolvedUrl(
            ADDON_HANDLE,
            True,
            li
        )

    except Exception as e:
        xbmc.log("play_match error: " + str(e), xbmc.LOGERROR)
        xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem())

# =========================
# Parse danh sách trận
# =========================
def list_matches(live_only=False):
    url = f"{BASE}/matches?t={utils.today_timestamp()}"
    xbmc.log(url, xbmc.LOGINFO)
    items = []
    try:
        res = requests.get(url, timeout=10)
        json_data = res.json()
    except Exception as e:
        xbmc.log("API error: " + str(e), xbmc.LOGERROR)
        return
        
    matches = json_data["data"].values()
    for match in matches:
        try:
            data = {
                "id": match.get("id", ""),
                "match_id": match.get("matchId"),
                "title": match.get("title", match.get("homeTeamName", "") +' vs '+match.get("awayTeamName", "")),
                "match_time": match.get("matchTime", 0),
                "competition": match.get("competitionName", "No title"),
                "live": match.get("match_status") == "live",
                "home_team": {
                    "name": match.get("homeTeamName", ""),
                    "logo": match.get("homeTeamLogo", "")
                },
                "away_team": {
                    "name": match.get("awayTeamName", ""),
                    "logo": match.get("awayTeamName", "")
                },
                "video_url":match.get("video_url", "")
            }

            li=utils.GetListItemFromData(data)

            if(data["live"]):
                items.append((li, play_url))
            if(not live_only):
                xbmcplugin.addDirectoryItem(
                    handle=ADDON_HANDLE,
                    url=data["video_url"],
                    listitem=li,
                    isFolder=False
                )

        except Exception as e:
            xbmc.log(f"Lỗi match {match.get('matchId')}: {e}", xbmc.LOGERROR)

    if(not live_only):
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    else: 
        return items