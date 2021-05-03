from __future__ import annotations

from io import IOBase
from pathlib import Path
from typing import BinaryIO
from unittest import mock

import dask
import hypothesis.strategies as st
import IPython.display
import matplotlib.cm
import matplotlib.colors
import pytest
import xarray as xr
from hypothesis import given, note, settings
from typing_extensions import Literal

from geogif import dgif, gif

from .strategies import colormaps, dataarrays, date_formats, rgb
from .util import fails, ignore, xerr


@pytest.fixture(scope="module")
def module_tmp_path(tmp_path_factory):
    # Hypothesis complains about using a function-level fixture
    return tmp_path_factory.mktemp("gifs")


def xerrs(
    cmap: str | matplotlib.colors.Colormap | None,
    arr: xr.DataArray,
    date_format: str | None,
) -> list[tuple[bool, Exception]]:
    return [
        (
            bool(cmap) and arr.ndim == 4 and arr.shape[1] != 1,
            ValueError("Colormaps are only possible on single-band data"),
        ),
        (arr.ndim not in (3, 4), ValueError("Array must only have the dimensions")),
        (
            arr.ndim == 4 and arr.shape[1] not in (1, 3),
            ValueError("Array must have 1 or 3 bands"),
        ),
        (
            bool(date_format) and fails(lambda: arr[arr.dims[0]].dt.strftime),
            TypeError("dimension are not datetimes"),
        ),
    ]


@given(
    arr=dataarrays(),
    to=st.sampled_from([None, "tempfile"]) | st.from_type(BinaryIO),
    fps=st.integers(1, 60),
    robust=st.booleans(),
    vmin=st.none() | st.floats(),
    vmax=st.none() | st.floats(),
    cmap=colormaps,
    date_format=st.none() | date_formats,
    date_position=st.sampled_from(["ul", "ur", "ll", "lr"]),
    date_color=rgb,
    date_bg=st.none() | rgb,
)
@settings(max_examples=500)
def test_gif(
    arr: xr.DataArray,
    to,
    fps: int,
    robust: bool,
    vmin: float | None,
    vmax: float | None,
    cmap: str | matplotlib.colors.Colormap | None,
    date_format: str | None,
    date_position: Literal["ul", "ur", "ll", "lr"],
    date_color: tuple[int, int, int],
    date_bg: tuple[int, int, int] | None,
    module_tmp_path: Path,
):
    if to == "tempfile":
        to = module_tmp_path / "test.gif"

    succeeded = False
    errs = xerrs(cmap, arr, date_format)
    note(str([e for c, e in errs if c]))
    with ignore(ValueError(r"is less than the default (vmin|vmax)")), xerr(errs):
        out = gif(
            arr,
            to=to,
            fps=fps,
            robust=robust,
            vmin=vmin,
            vmax=vmax,
            cmap=cmap,
            date_format=date_format,
            date_position=date_position,
            date_color=date_color,
            date_bg=date_bg,
        )
        succeeded = True

    if not succeeded:
        return

    if to is None:
        assert isinstance(out, IPython.display.Image)
        data = out.data
    elif isinstance(to, Path):
        assert out is None
        with to.open("rb") as f:
            data = f.read()
        with to.open("wb") as f:
            # clear the file for our next run
            f.write(b"")
    elif isinstance(to, IOBase):
        to.seek(0)
        data = to.read()
    else:
        raise RuntimeError(f"unreachable. type(to): {type(to)}")

    header, rest = data[:3], data[3:]
    assert header == b"GIF"
    assert len(rest) > 0


@given(
    arr=dataarrays(dask=True),
    bytes_=st.booleans(),
    fps=st.integers(1, 60),
    robust=st.booleans(),
    vmin=st.none() | st.floats(),
    vmax=st.none() | st.floats(),
    cmap=colormaps,
    date_format=st.none() | date_formats,
    date_position=st.sampled_from(["ul", "ur", "ll", "lr"]),
    date_color=rgb,
    date_bg=st.none() | rgb,
)
@settings(max_examples=500)
def test_dgif(
    arr: xr.DataArray,
    bytes_: bool,
    fps: int,
    robust: bool,
    vmin: float | None,
    vmax: float | None,
    cmap: str | matplotlib.colors.Colormap | None,
    date_format: str | None,
    date_position: Literal["ul", "ur", "ll", "lr"],
    date_color: tuple[int, int, int],
    date_bg: tuple[int, int, int] | None,
):
    succeeded = False
    errs = xerrs(cmap, arr, date_format)
    note(str([e for c, e in errs if c]))
    with xerr(errs):

        def raise_on_compute(dsk, keys, **kwargs):
            raise RuntimeError(
                f"Attempted to dask compute while creating a delayed GIF.\nKeys:{keys}"
            )

        with dask.config.set(scheduler=raise_on_compute), mock.patch.object(
            dask, "optimize", wraps=dask.optimize
        ) as mock_optimize:
            delayed = dgif(
                arr,
                bytes=bytes_,
                fps=fps,
                robust=robust,
                vmin=vmin,
                vmax=vmax,
                cmap=cmap,
                date_format=date_format,
                date_position=date_position,
                date_color=date_color,
                date_bg=date_bg,
            )
            mock_optimize.assert_called_once()
        succeeded = True

    if not succeeded:
        return

    succeeded = False
    with ignore(ValueError(r"is less than the default (vmin|vmax)")):
        result = delayed.compute()
        succeeded = True

    if not succeeded:
        return

    if bytes_:
        assert isinstance(result, bytes)
        data = result
    else:
        assert isinstance(result, IPython.display.Image)
        data = result.data

    header, rest = data[:3], data[3:]
    assert header == b"GIF"
    assert len(rest) > 0
