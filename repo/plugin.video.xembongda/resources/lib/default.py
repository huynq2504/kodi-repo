import sys
import xbmcplugin
import xbmcgui
import urllib.parse
from sites import cakhiatv


addon_handle = int(sys.argv[1])
base_url = sys.argv[0]
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))

action = params.get("action")

if action == "play":
    site = params.get("site")
    if site == "cakhiatv":
        cakhiatv.play_match(params.get("id"))

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

# =========================
# ROOT MENU
# =========================
def root_menu():

    websites = [
        {"name": "Cà khịa TV", "id": "cakhiatv"},
        {"name": "Trang Phim", "id": "phim"},
        {"name": "Trang TV", "id": "tv"},
    ]

    for site in websites:
        li = xbmcgui.ListItem(label=site["name"])
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
        xbmcgui.Dialog().notification("Addon", "Đang mở Trang Bóng Đá")

        # TODO: gọi hàm parse web bongda
        cakhiatv.list_matches()

    elif site_id == "phim":
        xbmcgui.Dialog().notification("Addon", "Đang mở Trang Phim")

        # TODO: gọi hàm parse web phim
        list_videos_from_phim()

    elif site_id == "tv":
        xbmcgui.Dialog().notification("Addon", "Đang mở Trang TV")

        # TODO: gọi hàm parse web tv
        list_videos_from_tv()


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