import logging
import time

class MainLoop(object):
    def __init__(self, config, binding_factory, sleep_time):
        self.logger = logging.getLogger('rss2jira')
        self.sleep_time = sleep_time
        self.bindings = [binding_factory.create(x) for x in config['sources']]
        self.running = True

    def run(self):
        while self.running:
            for b in self.bindings:
                b.pump()
            self.logger.debug('Going to sleep for {} seconds.'.format(self.sleep_time))
            time.sleep(self.sleep_time)
