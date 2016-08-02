import os
import signal

from watchdog.events import FileSystemEventHandler

from base.command.commander import Commander
from base.system.system import System


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, plugin_path):
        self.path = plugin_path

    def process(self, event):

        if event.src_path != self.path[:-1]:
            print('event_type:'+str(event.event_type))
            if event.event_type in ('created', 'modified', 'moved'):
                plu_path = event.src_path
                if event.event_type == 'moved':
                    plu_path = event.dest_path
                print('plu_path'+str(plu_path))
                result = Commander().set_event([None, 'load', '-p', plu_path.replace(self.path, '')])
                if result is True and System.Ahenk.is_running() is True:
                    os.kill(int(System.Ahenk.get_pid_number()), signal.SIGALRM)
            elif event.event_type == 'deleted':
                result = Commander().set_event([None, 'remove', '-p', event.src_path.replace(self.path, '')])
                if result is True and System.Ahenk.is_running() is True:
                    os.kill(int(System.Ahenk.get_pid_number()), signal.SIGALRM)

    def on_any_event(self, event):
        if event.is_directory:
            self.process(event)
