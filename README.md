# GeoGIF
[![Documentation Status](https://readthedocs.org/projects/geogif/badge/?version=latest)](https://geogif.readthedocs.io/en/latest/?badge=latest)


Make GIFs from time-stacked `xarray.DataArray`s (`time`, [optional `band`], `y`, `x`), dead-simple.

```python
from geogif import gif, dgif
gif(data_array)
dgif(dask_data_array).compute()
```

![Animation of shoreline moving on the coast of Cape Cod](docs/capecod.gif)

The "geo" part is a lie, actually. The arrays don't have to be geospatial in nature. But I called it GeoGIF because:

1. Wanting to animate a time-stack of imagery (like you'd get from [stackstac](https://stackstac.readthedocs.io/)) is a common task in the earth-observation/geospatial world.
1. I think `GeoGIF` is a hilarious idea<sup>[1](#geotiff)</sup>.


<a name="geotiff">1</a>: To ruin the joke, it sounds like GeoTIFF, a ubiquitous geospatial image format. If you also think this is a funny idea, and believe you'd have a better use for the name than I do, I'd happily cede it to you.

## Installation

```bash
pip install geogif
```

## Documentation

See https://geogif.readthedocs.io/en/latest/.

## Development

GeoGIF is managed by [Poetry](https://python-poetry.org/), so be sure that's installed first. To develop locally, first fork or clone the repo. Then, to set up a virtual environment and install the necessary dependencies:

```bash
cd geogif
poetry install
```

### Running Tests

GeoGIF has some basic end-to-end tests, written with [Hypothesis](https://hypothesis.readthedocs.io/en/latest/index.html). To run:

```bash
pytest
```

This will take ~30 seconds (longer the first time), as Hypothesis generates fake data to root out possible errors.

### Code style

GeoGIF is formatted with [shed](https://github.com/Zac-HD/shed), in order to allow for as few opinions as possible.
