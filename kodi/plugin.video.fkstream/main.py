import os
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

if __name__ == "__main__":
    try:
        from lib.router import Router

        router = Router(sys.argv)
        router.run()
    except Exception:
        import xbmc
        xbmc.log(f"[FKStream] ERREUR: {traceback.format_exc()}", xbmc.LOGERROR)
