import sys
import requests
import xbmcplugin
import xbmcgui
import xbmc
from datetime import datetime
import urllib.parse
import json
import utils
from sites import cakhiatv
from sites import colatv
from sites import quechoatv

ADDON_HANDLE = int(sys.argv[1])
def list_matches():
    all_items = []

    # lấy từ cakhiatv
    try:
        all_items.extend(cakhiatv.list_matches(live_only=True))
    except Exception as e:
        xbmc.log(f"Lỗi live cakhiatv", xbmc.LOGERROR)
    try:
        all_items.extend(colatv.list_matches(live_only=True))
    except Exception as e:
        xbmc.log(f"Lỗi live colatv", xbmc.LOGERROR)
    try:
        all_items.extend(quechoatv.list_matches(live_only=True))
    except Exception as e:
        xbmc.log(f"Lỗi live colatv", xbmc.LOGERROR)
    try:
        all_items.extend(quechoatv.list_matches(live_only=True, sport_slug="bong-chuyen"))
    except Exception as e:
        xbmc.log(f"Lỗi live colatv", xbmc.LOGERROR)

    # add vào Kodi
    for li, url in all_items:
        xbmcplugin.addDirectoryItem(
            handle=ADDON_HANDLE,
            url=url,
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(ADDON_HANDLE)