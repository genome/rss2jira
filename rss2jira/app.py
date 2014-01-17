import logging
import time

class MainLoop(object):
    def __init__(self, config, binding_factory, sleep_time, stop_condition):
        self.logger = logging.getLogger('rss2jira')
        self.sleep_time = sleep_time
        self.bindings = [binding_factory.create(x) for x in config['sources']]
        self.stop_condition = stop_condition
        self.iteration_count = 0

    def run(self):
        while self.stop_condition() is False:
            self.iteration_count += 1
            self.logger.info("Begin iteration {}".format(self.iteration_count))

            for b in self.bindings:
                b.pump()

            self.logger.debug('Going to sleep for {} seconds.'.format(
                    self.sleep_time))
            time.sleep(self.sleep_time)
