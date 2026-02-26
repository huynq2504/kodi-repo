import sys
import xbmcplugin
import xbmcgui
import urllib.parse
from sites import cakhiatv
from sites import colatv
from sites import livestv
from sites import quechoatv
import xbmcaddon
import os

addon_handle = int(sys.argv[1])
base_url = sys.argv[0]
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')


if xbmc.Player().isPlaying():
    xbmc.Player().stop()

action = params.get("action")

if action == "play":
    site = params.get("site")
    if site == "cakhiatv":
        cakhiatv.play_match(params.get("id"))
    if site == "colatv":
        colatv.play_match(params.get("id"))
    if site == "quechoatv":
        quechoatv.play_match(params.get("streams"))    

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

# =========================
# ROOT MENU
# =========================
def root_menu():

    websites = [
        {"name": "[COLOR yellow][B]Trực tiếp[/B][/COLOR]", "id": "livestv", "icon":os.path.join(addon_path,"resources","lib","sites","media","livestv.png")},
        {"name": "Quê Choa TV - [COLOR yellow]Bóng đá[/COLOR]", "id": "quechoatv", "icon":os.path.join(addon_path,"resources","lib","sites","media","quechoatv.png")}, 
        {"name": "Quê Choa TV - [COLOR yellow]Bóng chuyền[/COLOR]", "id": "quechoatv-bongchuyen", "icon":os.path.join(addon_path,"resources","lib","sites","media","quechoatv.png")}, 
        {"name": "Cà khịa TV" , "id": "cakhiatv", "icon": os.path.join(addon_path,"resources","lib","sites","media","cakhiatv.png")},
        {"name": "Cò lả TV", "id": "colatv", "icon":os.path.join(addon_path,"resources","lib","sites","media","colatv.png")}, 
    ]

    for site in websites:
        li = xbmcgui.ListItem(label=site["name"])
        li.setArt({
            "icon": site["icon"],
            "thumb": site["icon"],
            "fanart": site["icon"]
        })
        url = build_url({"mode": "site", "site": site["id"]})

        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True
        )

    xbmcplugin.endOfDirectory(addon_handle)


# =========================
# HANDLE WEBSITE
# =========================
def open_site(site_id):

    if site_id == "cakhiatv":
        # TODO: gọi hàm parse web bongda
        cakhiatv.list_matches()

    elif site_id == "colatv":
        #xbmcgui.Dialog().notification("Addon", "Đang mở Trang Phim")
        colatv.list_matches()

    elif site_id == "livestv":
        livestv.list_matches()
        
    elif site_id == "quechoatv":
        quechoatv.list_matches()
    elif site_id == "quechoatv-bongchuyen":
        quechoatv.list_matches(sport_slug="bong-chuyen")


# =========================
# Ví dụ function riêng từng web
# =========================
def list_videos_from_bongda():
    li = xbmcgui.ListItem(label="Video mẫu Bóng Đá")
    xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    xbmcplugin.endOfDirectory(addon_handle)

def list_videos_from_phim():
    li = xbmcgui.ListItem(label="Video mẫu Phim")
    xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    xbmcplugin.endOfDirectory(addon_handle)

def list_videos_from_tv():
    li = xbmcgui.ListItem(label="Video mẫu TV")
    xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    xbmcplugin.endOfDirectory(addon_handle)


# =========================
# ROUTER
# =========================
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))

mode = params.get("mode")
site = params.get("site")

if mode == "site":
    open_site(site)
else:
    root_menu()