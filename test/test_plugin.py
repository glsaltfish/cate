from unittest import TestCase

from ect.core import plugin
from ect.core.util import fetch_std_streams


class PluginTest(TestCase):
    def test_that_test_plugins_are_loaded(self):
        self.assertIsNotNone(plugin.PLUGIN_REGISTRY)

    def test_ect_init(self):
        # Yes, this is really a silly test :)
        # But this way we cover one more (empty) statement.
        plugin.ect_init(True, False, a=1, b=2)

    def test_error_reporting(self):
        with fetch_std_streams() as (stdout, stderr):
            plugin._report_plugin_error_msg('XXX')
        self.assertEqual(stderr.getvalue(), 'error: XXX\n')

        with fetch_std_streams() as (stdout, stderr):
            plugin._report_plugin_exception('YYY')
        self.assertEqual(stderr.getvalue(), 'error: YYY\n')




