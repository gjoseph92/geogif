from __future__ import annotations

from string import printable

import dask.array as da
import hypothesis.strategies as st
import matplotlib.cm
import matplotlib.colors
import numpy as np
import xarray as xr
from hypothesis.extra import numpy as npst, pandas as pdst

time_inds = st.sampled_from(
    [np.dtype("datetime64[ns]"), np.dtype("timedelta64[ns]"), np.dtype(int)]  # type: ignore
    # No overloads for "__new__" match the provided arguments
    #   Argument types: (Literal['datetime64[ns]'])
).flatmap(lambda dtype: pdst.indexes(dtype=dtype, min_size=1, max_size=10))
bands = st.lists(st.text(printable, max_size=6), unique=True)
xy_sizes = st.integers(min_value=1, max_value=64)


@st.composite
def dataarrays(draw, dask: bool = False) -> xr.DataArray:
    times = draw(time_inds)
    bandnames = draw(bands)
    height, width = draw(xy_sizes), draw(xy_sizes)

    shape = [len(times), len(bandnames), height, width]
    if len(bandnames) == 0:
        shape.pop(1)
    shape = tuple(shape)

    arr = draw(
        npst.arrays(
            dtype=st.one_of(
                npst.integer_dtypes(),
                npst.floating_dtypes(),
                npst.unsigned_integer_dtypes(),
                st.just(np.dtype(bool)),
            ),
            shape=shape,
        )
    )
    if dask:
        arr = da.from_array(arr)

    ndim = len(shape)
    dim_names = draw(
        st.lists(st.text(printable), min_size=ndim, max_size=ndim, unique=True)
    )
    coords = dict(zip(dim_names, [times, bandnames] if bandnames else [times]))

    return xr.DataArray(
        arr,
        coords=coords,
        dims=dim_names,
    )


# "_cmap_registry" is not a known member of module
colormaps = st.none() | st.sampled_from(list(matplotlib.cm._cmap_registry)).flatmap(  # type: ignore
    lambda cm: st.sampled_from([cm, matplotlib.cm.get_cmap(cm)])
)

datecodes = st.sampled_from(
    [
        "%a",
        "%A",
        "%w",
        "%d",
        "%b",
        "%B",
        "%m",
        "%y",
        "%Y",
        "%H",
        "%I",
        "%p",
        "%M",
        "%S",
        "%f",
        "%z",
        "%Z",
        "%j",
        "%U",
        "%W",
        "%c",
        "%x",
        "%X",
        "%%",
        "%G",
        "%u",
        "%V",
    ]
)

date_formats = st.recursive(
    datecodes | st.text(printable),
    lambda s: st.tuples(s, s).map("".join),
    max_leaves=10,
)
rgb = st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255))
