import os
import signal
import time

# from watchdog.events import FileSystemEventHandler
# from watchdog.observers import Observer

from base.command.commander import Commander
from base.system.system import System

"""
class FileEventHandler(FileSystemEventHandler):
    def __init__(self, plugin_path):
        self.path = plugin_path

    def process(self, event):
        if event.event_type == 'created':
            result = Commander().set_event([None, 'load', '-p', event.src_path.replace(self.path, '')])
            if result is True:
                if System.Ahenk.is_running() is True:
                    os.kill(int(System.Ahenk.get_pid_number()), signal.SIGALRM)
        elif event.event_type == 'deleted':
            # TODO
            print('plugin removed')

    def on_created(self, event):
        if event.is_directory:
            self.process(event)

    def on_deleted(self, event):
        if event.is_directory:
            self.process(event)

    def on_modified(self,event):
        print("MODIFIED-"+str(event.src_path))

"""
class PluginInstallListener:

    def listen(self, path):
        pass
        """
        observer = Observer()
        event_handler = FileEventHandler(path)
        observer.schedule(event_handler, path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        """
