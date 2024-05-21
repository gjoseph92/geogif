# Changelog

## 0.2 (2024-05-21)
* Make timestamp font size adjustable, and scale with image size by default

## 0.1.5 (2023-07-23)
* Fix `RuntimeError: getsize is deprecated and should be removed` with newer Pillow versions
* Require Pillow > 10.0.0
* Error immediately when trying to make a GIF of an empty array

## 0.1.4 (2023-02-09)
* Support `dask` calver

## 0.1.3 (2022-03-16)
* Support `xarray` calver
* Require Pillow > 9.0.1
* Fix `geogif.__version__` (used to return the version of `stackstac`!)

## 0.1.2 (2022-01-20)
Support 2022 versions of dask/distributed

## 0.1.1 (2021-04-07)
Loosen version restrictions of `xarray` (and `coiled`, `pystac-client`, and `stackstac` for docs build)

## 0.1.0 (2021-04-03)
Initial release 🎉
