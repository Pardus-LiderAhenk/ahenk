from multiprocessing import Process


class SetupTimer:
    @staticmethod
    def start(timer):
        thread_timer = Process(target=timer.run)
        thread_timer.start()
