from rss2jira.app import MainLoop
import mock

import unittest


class TestMainLoop(unittest.TestCase):
    def setUp(self):
        self.config = {"sources": [1, 2]}

    def test_run(self):
        stop_condition = mock.Mock(side_effect=[False, False, False, True])
        binding_factory = mock.Mock()
        binding_factory.create.side_effect = lambda x: mock.Mock()
        loop = MainLoop(self.config, binding_factory, sleep_time=0.1,
                stop_condition=stop_condition)

        self.assertEqual(2, len(loop.bindings))

        loop.run()
        self.assertEqual(3, loop.iteration_count)
        self.assertEqual(3, len(loop.bindings[0].pump.mock_calls))
        self.assertEqual(3, len(loop.bindings[0].pump.mock_calls))
