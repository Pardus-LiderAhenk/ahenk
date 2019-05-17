#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import threading
import time

from watchdog.observers import Observer

from base.plugin.file_handler import FileEventHandler


class PluginInstallListener(threading.Thread):
    def __init__(self, plugin_path):
        threading.Thread.__init__(self)
        self.path = plugin_path

    def run(self):
        observer = Observer()
        event_handler = FileEventHandler(self.path)
        observer.schedule(event_handler, self.path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
