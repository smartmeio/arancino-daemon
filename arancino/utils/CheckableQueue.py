from queue import Queue

class CheckableQueue(Queue):
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue