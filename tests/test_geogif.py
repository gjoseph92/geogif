from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import hypothesis.strategies as st
import IPython.display
import matplotlib.cm
import matplotlib.colors
import pytest
import xarray as xr
from hypothesis import given, note, settings
from typing_extensions import Literal

from geogif import gif

from .strategies import colormaps, dataarrays, date_formats, rgb
from .util import fails, ignore, xerr


@pytest.fixture(scope="module")
def module_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("gifs")


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
    errs: list[tuple[bool, Exception]] = [
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

    if succeeded:
        if to is None:
            assert isinstance(out, IPython.display.Image)
        elif isinstance(to, BinaryIO):
            assert to.read(3) == b"GIF"
            assert len(to.read()) > 0
