import os
import random
import time
import shutil
import math
import multiprocessing

from scrapy.crawler import CrawlerProcess
from .news import makecrawler


class CrawlManager:
    """
    Manages the execution of the crawls of the given input sources
    Supports running crawls in multiple processes and controlling them
    via commands received from remote channels

    Usage:
    >> manager = CrawlManager(lang=lang, sources=sources,
                              save_path=save_path, remote=True)
    >> manager.start_crawl(crawl_settings)
    """

    def __init__(self, **params):
        self.remote = params.get('remote', False)
        self.sources = list(params['sources'])
        self.lang = params['lang']
        self.save_path = params['save_path']

        self.jobdir = os.path.join(self.save_path, 'jobs')
        self.backupdir = os.path.join(self.save_path, 'backup')
        self.htmldir = os.path.join(self.save_path, 'html')
        self.artsdir = os.path.join(self.save_path, 'arts')

        if os.path.isdir(self.jobdir):
            shutil.rmtree(self.jobdir)
            if os.path.isdir(self.backupdir):
                shutil.move(self.backupdir, self.jobdir)

        os.makedirs(self.jobdir, exist_ok=True)
        os.makedirs(self.backupdir, exist_ok=True)
        os.makedirs(self.htmldir, exist_ok=True)
        os.makedirs(self.artsdir, exist_ok=True)

        self.create_jobdirs()

        self.bkp_lock = multiprocessing.Lock()

    def start_control(self):
        while True:
            time.sleep(10)

    def create_jobdirs(self):
        # create job directories
        self.subjobdirs = {}
        for source in self.sources:
            name = source['name']
            subjobdir = os.path.join(self.jobdir, name)
            self.subjobdirs[name] = subjobdir
            os.makedirs(subjobdir, exist_ok=True)

    def start_procs(self, crawler_settings):
        """
        creates one crawler process per cpu and splits the sources
        uniformly among all the crawler processes
        """
        num_procs = multiprocessing.cpu_count()

        sys_procs = []
        quo = math.ceil(len(self.sources) / num_procs)
        for pid in range(num_procs):
            s, e = pid * quo, (pid+1) * quo
            sys_proc = multiprocessing.Process(target=self.start_crawl_proc,
                                               args=(crawler_settings, s, e))
            sys_proc.start()
            sys_procs.append(sys_proc)
        return sys_procs

    def start_crawl_proc(self, crawler_settings, start_idx, end_idx):
        while True:
            start = time.time()
            crawl_proc = CrawlerProcess(settings=crawler_settings)

            for source in self.sources[start_idx:end_idx]:
                crawler = makecrawler(source,
                                      JOBDIR=self.subjobdirs[source['name']])
                if crawler:
                    crawl_proc.crawl(crawler, source=source,
                                     arts_path=self.artsdir,
                                     html_path=self.htmldir)
            crawl_proc.start()
            end = time.time()
            elapsed_time = end - start

            if elapsed_time < 3600:
                print('spiders closed due to completion or network failure')
                break
            else:
                self.create_bkp()

    def create_bkp(self):
        self.bkp_lock.acquire()
        print('Creating Checkpoint...')
        shutil.copytree(self.jobdir, self.backupdir)
        self.bkp_lock.release()

    def start_crawl(self, **crawler_settings):
        procs = self.start_procs(crawler_settings)
        for proc in procs:
            proc.join()


