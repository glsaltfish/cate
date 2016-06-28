import sys
import unittest
from time import sleep

from ect.core.monitor import Monitor
from ect.core.util import fetch_std_streams
from ect.ui import cli


class CliTest(unittest.TestCase):
    def test_noargs(self):
        sys.argv = []
        with fetch_std_streams():
            status = cli.main()
            self.assertEqual(status, 0)

    def test_invalid_command(self):
        with fetch_std_streams():
            status = cli.main(['pipo'])
            self.assertEqual(status, 2)

    def test_option_version(self):
        with fetch_std_streams():
            status = cli.main(args=['--version'])
            self.assertEqual(status, 0)

    def test_option_help(self):
        with fetch_std_streams():
            status = cli.main(args=['--h'])
            self.assertEqual(status, 0)
            status = cli.main(args=['--help'])
            self.assertEqual(status, 0)


class CliDataSourceCommandTest(unittest.TestCase):
    def test_command_ds_info(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['ds', 'SOIL_MOISTURE_DAILY_FILES_ACTIVE_V02.2'])
            self.assertEqual(status, 0)
        out1 = stdout.getvalue()
        self.assertTrue('Base directory' in out1)
        self.assertEqual(stderr.getvalue(), '')

        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['ds', 'SOIL_MOISTURE_DAILY_FILES_ACTIVE_V02.2', '--info'])
            self.assertEqual(status, 0)
        out2 = stdout.getvalue()

        self.assertEqual(out1, out2)

    @unittest.skip(reason="skipped unless you want to debug data source synchronisation")
    def test_command_ds_sync(self):
        with fetch_std_streams():
            status = cli.main(args=['ds', 'SOIL_MOISTURE_DAILY_FILES_ACTIVE_V02.2', '--sync'])
            self.assertEqual(status, 0)

    @unittest.skip(reason="skipped unless you want to debug data source synchronisation")
    def test_command_ds_sync_with_period(self):
        with fetch_std_streams():
            status = cli.main(args=['ds', 'SOIL_MOISTURE_DAILY_FILES_ACTIVE_V02.2', '--sync', '--time', '2010-12'])
            self.assertEqual(status, 0)

    def test_command_ds_parse_time_period(self):
        from ect.ui.cli import DataSourceCommand
        from datetime import date

        self.assertEqual(DataSourceCommand.parse_time_period('2010'), (date(2010, 1, 1), date(2010, 12, 31)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-02'), (date(2010, 2, 1), date(2010, 2, 28)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-12'), (date(2010, 12, 1), date(2010, 12, 31)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-02-04'), (date(2010, 2, 4), date(2010, 2, 4)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-12-31'), (date(2010, 12, 31), date(2010, 12, 31)))

        self.assertEqual(DataSourceCommand.parse_time_period('2010,2014'), (date(2010, 1, 1), date(2014, 12, 31)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-02,2010-09'), (date(2010, 2, 1), date(2010, 9, 30)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-12,2011-12'),
                         (date(2010, 12, 1), date(2011, 12, 31)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-02-04,2019-02-04'),
                         (date(2010, 2, 4), date(2019, 2, 4)))
        self.assertEqual(DataSourceCommand.parse_time_period('2010-12-31,2010-01-06'),
                         (date(2010, 12, 31), date(2010, 1, 6)))

        # errors
        self.assertEqual(DataSourceCommand.parse_time_period('2010-12-31,2010-01'), None)
        self.assertEqual(DataSourceCommand.parse_time_period('2010,2010-01'), None)
        self.assertEqual(DataSourceCommand.parse_time_period('2010-01,2010-76'), None)
        self.assertEqual(DataSourceCommand.parse_time_period('2010-1-3-83,2010-01'), None)
        self.assertEqual(DataSourceCommand.parse_time_period('20L0-1-3-83,2010-01'), None)

    def test_command_run_no_args(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['ds'])
            self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(),
                         "usage: ect ds [-h] [--time PERIOD] [--info] [--sync] DS_NAME [DS_NAME ...]\n"
                         "ect: ect ds: error: the following arguments are required: DS_NAME\n\n")


class CliRunCommandTest(unittest.TestCase):
    def test_command_run_with_unknown_op(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['run', 'pipapo', 'lat=13.2', 'lon=52.9'])
            self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), "ect: error: command 'run': unknown operation 'pipapo'\n")

    def test_command_run_noargs(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['run'])
            self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), "ect: error: command 'run' requires OP argument\n")

    def test_command_run_with_op(self):
        from ect.core.op import OP_REGISTRY as OP_REGISTRY

        op_reg = OP_REGISTRY.add_op(timeseries, fail_if_exists=True)

        try:
            # Run without progress monitor
            with fetch_std_streams() as (stdout, stderr):
                status = cli.main(args=['run', op_reg.meta_info.qualified_name, 'lat=13.2', 'lon=52.9'])
                self.assertEqual(status, 0)
            soutv = stdout.getvalue()
            self.assertTrue('Running operation ' in soutv)
            self.assertTrue('lat=13.2 lon=52.9 method=nearest' in soutv)
            self.assertTrue('Output: [0.3, 0.25, 0.05, 0.4, 0.2, 0.1, 0.5]' in soutv)
            self.assertEqual(stderr.getvalue(), '')

            # Run with progress monitor
            with fetch_std_streams() as (stdout, stderr):
                status = cli.main(args=['run', '--monitor', op_reg.meta_info.qualified_name, 'lat=13.2', 'lon=52.9'])
                self.assertEqual(status, 0)
            soutv = stdout.getvalue()
            self.assertTrue('Running operation ' in soutv)
            self.assertTrue('lat=13.2 lon=52.9 method=nearest' in soutv)
            self.assertTrue('Extracting timeseries data: started' in soutv)
            self.assertTrue('Extracting timeseries data:  33%' in soutv)
            self.assertTrue('Extracting timeseries data: done' in soutv)
            self.assertTrue('Output: [0.3, 0.25, 0.05, 0.4, 0.2, 0.1, 0.5]' in soutv)
            self.assertEqual(stderr.getvalue(), '')

            # Run with invalid keyword
            with fetch_std_streams() as (stdout, stderr):
                status = cli.main(args=['run', op_reg.meta_info.qualified_name, 'l*t=13.2', 'lon=52.9'])
                self.assertEqual(status, 2)
            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), "ect: error: command 'run': keyword 'l*t' is not a valid identifier\n")

        finally:
            OP_REGISTRY.remove_op(op_reg.operation, fail_if_not_exists=True)

    def test_command_run_with_workflow(self):
        from ect.core.op import OP_REGISTRY as OP_REGISTRY
        import os.path

        op_reg = OP_REGISTRY.add_op(timeseries, fail_if_exists=True)

        workflow_file = os.path.join(os.path.dirname(__file__), 'timeseries.json')
        self.assertTrue(os.path.exists(workflow_file), msg='missing test file %s' % workflow_file)

        try:
            # Run without progress monitor
            with fetch_std_streams() as (stdout, stderr):
                status = cli.main(args=['run', workflow_file, 'lat=13.2', 'lon=52.9'])
                self.assertEqual(status, 0)
            soutv = stdout.getvalue()
            self.assertTrue('Running workflow ' in soutv)
            self.assertTrue('lat=13.2 lon=52.9' in soutv)
            self.assertTrue('Output: return = [0.3, 0.25, 0.05, 0.4, 0.2, 0.1, 0.5]' in soutv)
            self.assertEqual(stderr.getvalue(), '')

            # Run with progress monitor
            with fetch_std_streams() as (stdout, stderr):
                status = cli.main(args=['run', '--monitor', workflow_file, 'lat=13.2', 'lon=52.9'])
                self.assertEqual(status, 0)
            soutv = stdout.getvalue()
            self.assertTrue('Running workflow ' in soutv)
            self.assertTrue('lat=13.2 lon=52.9' in soutv)
            self.assertTrue('Extracting timeseries data: started' in soutv)
            self.assertTrue('Extracting timeseries data:  33%' in soutv)
            self.assertTrue('Extracting timeseries data: done' in soutv)
            self.assertTrue('Output: return = [0.3, 0.25, 0.05, 0.4, 0.2, 0.1, 0.5]' in soutv)
            self.assertEqual(stderr.getvalue(), '')

        finally:
            OP_REGISTRY.remove_op(op_reg.operation, fail_if_not_exists=True)

    def test_command_run_help(self):
        with fetch_std_streams():
            status = cli.main(args=['run', '-h'])
            self.assertEqual(status, 0)

        with fetch_std_streams():
            status = cli.main(args=['run', '--help'])
            self.assertEqual(status, 0)


class CliListCommandTest(unittest.TestCase):
    def test_command_list(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['list'])
            self.assertEqual(status, 0)
        self.assertIn('operation', stdout.getvalue())
        self.assertIn('found', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')

        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['list', 'op'])
            self.assertEqual(status, 0)
        self.assertIn('operation', stdout.getvalue())
        self.assertIn('found', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')

        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['list', 'pi'])
            self.assertEqual(status, 0)
        self.assertIn('plugin', stdout.getvalue())
        self.assertIn('found', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')

        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['list', 'ds'])
            self.assertEqual(status, 0)
        self.assertIn('data source', stdout.getvalue())
        self.assertIn('found', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')

        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['list', '--pattern', 'sst*', 'ds'])
            self.assertEqual(status, 0)
        self.assertIn('data source', stdout.getvalue())
        self.assertIn('found', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')


class CliLicenseCommandTest(unittest.TestCase):
    def test_command_license(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['lic'])
            self.assertEqual(status, 0)
        self.assertIn('GNU GENERAL PUBLIC LICENSE', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')


class CliCopyrightCommandTest(unittest.TestCase):
    def test_command_copyright(self):
        with fetch_std_streams() as (stdout, stderr):
            status = cli.main(args=['cr'])
            self.assertEqual(status, 0)
        self.assertIn('European Space Agency', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), '')


def timeseries(lat: float, lon: float, method: str = 'nearest', monitor=Monitor.NULL) -> list:
    """Timeseries dummy function for testing."""
    print('lat=%s lon=%s method=%s' % (lat, lon, method))
    work_units = [0.3, 0.25, 0.05, 0.4, 0.2, 0.1, 0.5]
    with monitor.starting('Extracting timeseries data', sum(work_units)):
        for work_unit in work_units:
            sleep(work_unit / 10.)
            monitor.progress(work_unit)
    return work_units
