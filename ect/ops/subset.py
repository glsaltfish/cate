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

"""
Description
===========

Subset operations

Components
==========
"""

import xarray as xr
from ect.core.op import op_input, op_return, op


@op(tags=['geometric', 'subset', 'spatial'])
@op_input('ds', description='A dataset to subset')
@op_input('lat_min', description='Minimum latitude value to select')
@op_input('lat_max', description='Maximum latitude value to select')
@op_input('lon_min', description='Minimum longitude value to select')
@op_input('lon_max', description='Maximum longitude value to select')
@op_return(description='The subset dataset')
def subset_spatial(ds: xr.Dataset,
                   lat_min: float,
                   lat_max: float,
                   lon_min: float,
                   lon_max: float):
    """
    Do a spatial subset of the dataset

    :param ds: Dataset to subset
    :param lat_min: Minimum latitude value
    :param lat_max: Maximum latitude value
    :param lon_min: Minimum longitude value
    :param lon_max: Maximum longitude value
    :return: Subset dataset
    """
    lat_slice = slice(lat_min, lat_max)
    lon_slice = slice(lon_min, lon_max)
    indexers = {'lat': lat_slice, 'lon': lon_slice}
    return ds.sel(**indexers)


@op(tags=['subset', 'temporal'])
@op_input('ds', description='A dataset to subset')
@op_input('time_min', description='Minimum time to select')
@op_input('time_max', description='Maximum time to select')
@op_return(description='The subset dataset')
def subset_temporal(ds: xr.Dataset, time_min: str, time_max: str):
    """
    Do a temporal subset of the dataset

    :param ds: Dataset to subset
    :param time_min: Minimum time
    :param time_max: Maximum time
    :return: Subset dataset
    """
    time_slice = slice(time_min, time_max)
    indexers = {'time': time_slice}
    return ds.sel(**indexers)


@op(tags=['subset', 'temporal'])
@op_input('ds', description='A dataset to subset')
@op_input('time_ind_min', description='Minimum time index to select')
@op_input('time_ind_max', description='Maximum time index to select')
@op_return(description='The subset dataset')
def subset_temporal_index(ds: xr.Dataset, time_ind_min: int, time_ind_max: int):
    """
    Do a temporal indices based subset

    :param ds: Dataset to subset
    :param time_ind_min: Minimum time index to select
    :param time_ind_max: Maximum time index to select
    :return: Subset dataset
    """
    # we're creating a slice that includes both ends
    # to have the same functionality as subset_temporal
    time_slice = slice(time_ind_min, time_ind_max + 1)
    indexers = {'time': time_slice}
    return ds.isel(**indexers)
