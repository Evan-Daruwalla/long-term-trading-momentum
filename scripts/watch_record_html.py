"""Watch the Project Record .md for changes and re-render the .html instantly.

Event-driven (watchdog -> Windows ReadDirectoryChangesW), not polling. Runs
forever; meant to be launched once at logon (see watch_record_html.bat +
the TradingRecordWatch scheduled task) and left running in the background.

Usage: .venv\\Scripts\\python.exe -m scripts.watch_record_html
"""
import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from scripts.render_record_html import SRC, main as render

DOCS_DIR = os.path.dirname(SRC)
TARGET = os.path.basename(SRC)
DEBOUNCE_SEC = 1.0  # editors often emit several write events per save


class RecordHandler(FileSystemEventHandler):
    def __init__(self):
        self._last_run = 0.0

    def on_modified(self, event):
        if event.is_directory or os.path.basename(event.src_path) != TARGET:
            return
        now = time.time()
        if now - self._last_run < DEBOUNCE_SEC:
            return
        self._last_run = now
        try:
            render()
        except Exception as e:
            print(f"[watch_record_html] render failed: {e}")


def main():
    render()  # sync once at startup in case the .md changed while this wasn't running
    handler = RecordHandler()
    observer = Observer()
    observer.schedule(handler, DOCS_DIR, recursive=False)
    observer.start()
    print(f"[watch_record_html] watching {SRC} -> re-rendering on change (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
