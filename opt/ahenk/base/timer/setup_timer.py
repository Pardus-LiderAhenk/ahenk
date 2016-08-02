
class SetupTimer:
    @staticmethod
    def start(timer):
        timer.setDaemon(True)
        timer.start()
