# The MIT License (MIT)
# Copyright (c) 2016 by the ECT Development Team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os.path
from abc import ABCMeta

import xarray as xr
from ect.core.monitor import Monitor
from ect.core.objectio import OBJECT_IO_REGISTRY, ObjectIO
from ect.core.op import op_input, op


@op(tags=['io'])
@op_input('ds_name')
@op_input('start_date')
@op_input('end_date')
@op_input('sync')
def open_dataset(ds_name: str,
                 start_date: str = None,
                 end_date: str = None,
                 sync: bool = False,
                 monitor: Monitor = Monitor.NULL) -> xr.Dataset:
    """
    Open a dataset from a data source identified by *ds_name*.

    :param ds_name: The name of data source.
    :param start_date: Optional start date of the requested dataset.
    :param end_date: Optional end date of the requested dataset.
    :param sync: Whether to synchronize local and remote data files before opening the dataset.
    :param monitor: a progress monitor, used only if *sync* is ``True``.
    :return: An new dataset instance.
    """
    import ect.core.io
    return ect.core.io.open_dataset(ds_name, start_date=start_date, end_date=end_date, sync=sync, monitor=monitor)


# noinspection PyShadowingBuiltins
@op(tags=['io'], no_cache=True)
@op_input('ds')
@op_input('file')
@op_input('format')
def save_dataset(ds: xr.Dataset, file: str, format: str = None):
    ds.to_netcdf(file, format=format)


# noinspection PyShadowingBuiltins
@op(tags='io')
@op_input('file')
@op_input('format')
def read_object(file: str, format: str = None) -> object:
    import ect.core.objectio
    obj, _ = ect.core.objectio.read_object(file, format_name=format)
    return obj


# noinspection PyShadowingBuiltins
@op(tags='io', no_cache=True)
@op_input('obj')
@op_input('file')
@op_input('format')
def write_object(obj, file: str, format: str = None):
    import ect.core.objectio
    ect.core.objectio.write_object(obj, file, format_name=format)


@op(tags=['io'])
@op_input('file')
@op_input('encoding')
def read_text(file: str, encoding: str = None) -> str:
    if isinstance(file, str):
        with open(file, 'r', encoding=encoding) as fp:
            return fp.read()
    else:
        # noinspection PyUnresolvedReferences
        return file.read()


@op(tags=['io'], no_cache=True)
@op_input('obj')
@op_input('file')
@op_input('encoding')
def write_text(obj: object, file: str, encoding: str = None):
    if isinstance(file, str):
        with open(file, 'w', encoding=encoding) as fp:
            fp.write(str(obj))
    else:
        # noinspection PyUnresolvedReferences
        return file.write(str(obj))


@op(tags=['io'])
@op_input('file')
@op_input('encoding')
def read_json(file: str, encoding: str = None) -> object:
    if isinstance(file, str):
        with open(file, 'r', encoding=encoding) as fp:
            return json.load(fp)
    else:
        return json.load(file)


@op(tags=['io'], no_cache=True)
@op_input('obj')
@op_input('file')
@op_input('encoding')
@op_input('indent')
@op_input('separators')
def write_json(obj: object, file: str, encoding: str = None, indent: str = None, separators: str = None):
    if isinstance(file, str):
        with open(file, 'w', encoding=encoding) as fp:
            json.dump(obj, fp, indent=indent, separators=separators)
    else:
        return json.dump(obj, file, indent=indent, separators=separators)


@op(tags=['io'])
@op_input('file')
@op_input('drop_variables')
@op_input('decode_cf')
@op_input('decode_times')
@op_input('engine')
def read_netcdf(file: str, drop_variables: str = None, decode_cf: bool = True, decode_times: bool = True,
                engine: str = None) -> xr.Dataset:
    return xr.open_dataset(file, drop_variables=drop_variables,
                           decode_cf=decode_cf, decode_times=decode_times, engine=engine)


@op(tags=['io'], no_cache=True)
@op_input('obj')
@op_input('file')
@op_input('engine')
def write_netcdf3(obj: xr.Dataset, file: str, engine: str = None):
    obj.to_netcdf(file, format='NETCDF3_64BIT', engine=engine)


@op(tags=['io'], no_cache=True)
@op_input('obj')
@op_input('file')
@op_input('engine')
def write_netcdf4(obj: xr.Dataset, file: str, engine: str = None):
    obj.to_netcdf(file, format='NETCDF4', engine=engine)


# noinspection PyAbstractClass
class TextObjectIO(ObjectIO):
    @property
    def description(self):
        return "Plain text format"

    @property
    def format_name(self):
        return 'TEXT'

    @property
    def filename_ext(self):
        return '.txt'

    @property
    def read_op(self):
        return read_text

    @property
    def write_op(self):
        return write_text

    def read_fitness(self, file):
        # Basically every object can be written to a text file: str(obj)
        return 1 if isinstance(file, str) and os.path.isfile(file) else 0

    def write_fitness(self, obj):
        return 1000 if isinstance(obj, str) else 1


# noinspection PyAbstractClass
class JsonObjectIO(ObjectIO):
    @property
    def description(self):
        return 'JSON format (plain text, UTF8)'

    @property
    def format_name(self):
        return 'JSON'

    @property
    def filename_ext(self):
        return '.json'

    @property
    def read_op(self):
        return read_json

    @property
    def write_op(self):
        return write_json

    def read_fitness(self, file):
        return 1 if isinstance(file, str) and os.path.isfile(file) else 0

    def write_fitness(self, obj):
        return 1000 if isinstance(obj, str) \
                       or isinstance(obj, float) \
                       or isinstance(obj, int) \
                       or isinstance(obj, list) \
                       or isinstance(obj, dict) else 0


class NetCDFObjectIO(ObjectIO, metaclass=ABCMeta):
    @property
    def filename_ext(self):
        return '.nc'

    def read_fitness(self, file):
        # noinspection PyBroadException
        try:
            dataset = self.read(file)
            dataset.close()
            return 100000
        except Exception:
            return -1

    def write_fitness(self, obj):
        # TODO (forman, 20160905): add support for numpy-like arrays
        return 100000 if isinstance(obj, xr.Dataset) or (hasattr(obj, 'to_netcdf') and callable(obj.to_netcdf)) \
            else 0


# noinspection PyAbstractClass
class NetCDF3ObjectIO(NetCDFObjectIO):
    @property
    def description(self):
        return "netCDF 3 file format, which fully supports 2+ GB files."

    @property
    def format_name(self):
        return 'NETCDF3'

    @property
    def read_op(self):
        return read_netcdf

    @property
    def write_op(self):
        return write_netcdf3


# noinspection PyAbstractClass
class NetCDF4ObjectIO(NetCDFObjectIO):
    @property
    def description(self):
        return "netCDF 4 file format (HDF5 file format, using netCDF 4 API features)"

    @property
    def format_name(self):
        return 'NETCDF4'

    @property
    def read_op(self):
        return read_netcdf

    @property
    def write_op(self):
        return write_netcdf4


OBJECT_IO_REGISTRY.object_io_list.extend([
    TextObjectIO(),
    JsonObjectIO(),
    NetCDF4ObjectIO(),
    NetCDF3ObjectIO()
])