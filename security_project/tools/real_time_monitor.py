from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.log'):
            print(f'Log file modified: {event.src_path}')

def start_monitoring(log_path):
    observer = Observer()
    observer.schedule(LogHandler(), path=log_path)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()