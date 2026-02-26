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


BASE = f"https://quechoa5.live/api/trpc/public.match.countByFilters,public.tournament.listAll,public.match.featured,public.match.list,public.match.list?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22sportSlug%22%3A%22bong-da%22%2C%22tournamentSlug%22%3Anull%7D%2C%22meta%22%3A%7B%22values%22%3A%7B%22tournamentSlug%22%3A%5B%22undefined%22%5D%7D%2C%22v%22%3A1%7D%7D%2C%221%22%3A%7B%22json%22%3A%7B%22sportSlug%22%3A%22bong-da%22%2C%22limit%22%3A100%7D%7D%2C%222%22%3A%7B%22json%22%3A%7B%22limit%22%3A8%2C%22filterBy%22%3A%22featured%22%2C%22sportSlug%22%3A%22bong-da%22%7D%7D%2C%223%22%3A%7B%22json%22%3A%7B%22sportSlug%22%3A%22bong-da%22%2C%22status%22%3A%5B%22upcoming%22%5D%2C%22limit%22%3A12%7D%7D%2C%224%22%3A%7B%22json%22%3A%7B%22sportSlug%22%3A%22bong-da%22%2C%22status%22%3A%5B%22live%22%5D%2C%22limit%22%3A100%7D%7D%7D"


ADDON_HANDLE = int(sys.argv[1])



def play_match(streams_json):

    streams = json.loads(streams_json)

    if not streams:
        xbmcgui.Dialog().notification("Error", "No stream")
        return

    labels = [s["label"] for s in streams]

    idx = xbmcgui.Dialog().select("Chọn link phát", labels)

    if idx == -1:
        return

    stream_url = streams[idx]["url"]

    li = xbmcgui.ListItem(path=stream_url)
    li.setProperty("IsPlayable", "true")

    xbmcplugin.setResolvedUrl(
        ADDON_HANDLE,
        True,
        li
    )

# =========================
# Parse danh sách trận
# =========================


BASE = "https://quechoa5.live/api/trpc"


def list_matches(live_only=False, sport_slug="bong-da"):

    url = BASE + "/public.match.list?batch=1"

    input_json = {
        "0": {
            "json": {
                "sportSlug": sport_slug,
                "status": ["live"] if live_only else ["live", "upcoming"],
                "limit": 100
            }
        },
    }

    params = {
        "batch": "1",
        "input": json.dumps(input_json, separators=(',', ':'))
    }

    xbmc.log(url, xbmc.LOGINFO)

    items = []

    try:
        res = requests.get(url, params=params, timeout=10)
        response = res.json()
        #xbmc.log(
        #    "QUECHOA5 RESPONSE:\n" + json.dumps(response, indent=2, ensure_ascii=False),
        #    xbmc.LOGINFO
        #)
    except Exception as e:
        xbmc.log("API error: " + str(e), xbmc.LOGERROR)
        return

    try:
        matches = response[0]["result"]["data"]["json"]
    except:
        xbmc.log("Invalid response", xbmc.LOGERROR)
        return

    for match in matches:

        home = match.get("homeTeam", {})
        away = match.get("awayTeam", {})
        tournament = match.get("tournament", {})

        data = {
            "id": match.get("id", ""),
            "match_id": match.get("id", ""),
            "title": home.get("name", "") + " vs " + away.get("name", ""),
            "match_time": utils.iso_to_timestamp(match.get("startTime", "0")),
            "competition": tournament.get("name", ""),
            "live": match.get("isLive", False),
            "home_team": {
                "name": home.get("name"),
                "logo": home.get("logoUrl")
            },

            "away_team": {
                "name": away.get("name"),
                "logo": away.get("logoUrl")
            }
        }

        li = utils.GetListItemFromData(data)
        
        commentators = match.get("commentators", [])

        # lưu toàn bộ streamUrls
        streams = []

        for c in commentators:
            account = c.get("account", {})
            name = account.get("name", "")

            for s in account.get("streamUrls", []):
                streams.append({
                    "label": "[%s] %s" % (name, s.get("label")),
                    "url": s.get("url")
                })


        play_url = build_url({
            "action": "play",
            "site": "quechoatv",
            "streams": json.dumps(streams)
        })

        if data["live"]:
            items.append((li, play_url))

        if not live_only:
            xbmcplugin.addDirectoryItem(
                handle=ADDON_HANDLE,
                url=play_url,
                listitem=li,
                isFolder=False
            )

    if not live_only:
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    else:
        return items