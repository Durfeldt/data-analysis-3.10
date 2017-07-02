import time

from persistqueue import Queue, Empty

import dataanalysis.caches
import dataanalysis.caches.cache_core
import dataanalysis.core as da


class DelegatedNoticeException(da.AnalysisDelegatedException):
    pass

class DelegatingCache(dataanalysis.caches.cache_core.Cache):

    def restore(self,hashe,obj,restore_config=None):
        raise da.AnalysisDelegatedException(hashe)


class QueueCache(dataanalysis.caches.cache_core.Cache):

    def __init__(self,queue_file="/tmp/queue"):
        self.queue_file=queue_file
        self.queue = Queue(self.queue_file)

    def restore(self,hashe,obj,restore_config=None):
        self.queue.put([obj.get_factory_name(),dataanalysis.core.AnalysisFactory.get_module_description(),hashe])

        raise DelegatedNoticeException(hashe)

    def wipe_queue(self):
        while True:
            try:
                item=self.queue.get(block=False)
            except Empty:
                break
            self.queue.task_done()


class QueueCacheWorker(object):
    def __init__(self,queue_file="/tmp/queue"):
        self.queue_file = queue_file
        self.queue = Queue(self.queue_file)

    def run_once(self):
        object_name,hashe,modules=self.queue.get(block=False)
        print("object name",object_name)
        print("modules",modules)
        print("hashe",hashe)

        A=dataanalysis.core.AnalysisFactory[object_name]

        return A.get()

    def run_all(self,burst=True):
        while True:
            print(time.time())

            try:
                item=self.queue.get(block=False)
            except Empty:
                break

            hashe, modules = item
            print(hashe)
            print(modules)
            self.queue.task_done()




