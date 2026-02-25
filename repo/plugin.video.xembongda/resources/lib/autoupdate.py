import xbmc
import xbmcgui
import xbmcaddon
import threading
import time

ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')


def run_update():
    try:
        xbmc.log(f"[{ADDON_ID}] Checking for updates...", xbmc.LOGINFO)

        # Refresh repository
        xbmc.executebuiltin('UpdateAddonRepos')

        # Đợi 3 giây cho Kodi load repo
        time.sleep(3)

        # Check và cài update nếu có
        xbmc.executebuiltin('UpdateLocalAddons')

        xbmcgui.Dialog().notification(
            "Giai Tri",
            "Đang kiểm tra cập nhật...",
            xbmcgui.NOTIFICATION_INFO,
            3000
        )

    except Exception as e:
        xbmc.log(f"[{ADDON_ID}] Update error: {e}", xbmc.LOGERROR)


def start():
    thread = threading.Thread(target=run_update)
    thread.start()


if __name__ == "__main__":
    start()