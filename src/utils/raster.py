import logging

import numpy as np
import xarray as xr
from rasterio.enums import Resampling


def validate_dimensions(ds):
    required_dims = {"x", "y", "date"}
    missing_dims = required_dims - set(ds.dims)
    if missing_dims:
        raise ValueError(
            f"Dataset missing required dimensions: {missing_dims}"
        )
    # Get the fourth dimension if it exists (not x, y, or date)
    dims = list(ds.dims)
    fourth_dim = next(
        (dim for dim in dims if dim not in {"x", "y", "date"}), None
    )
    return fourth_dim


def upsample_raster(ds, resampled_resolution=0.05, logger=None):
    """
    Upsample a raster to a higher resolution using nearest neighbor resampling,
    via the `Resampling.nearest` method from `rasterio`.

    Parameters
    ----------
    ds : xarray.Dataset
        The raster data set to upsample. Must have dimensions 'x', 'y', and 'date',
        with an optional fourth dimension (e.g., 'band' or 'leadtime').
    resampled_resolution : float, optional
        The desired resolution for the upsampled raster.

    Returns
    -------
    xarray.Dataset
        The upsampled raster as a Dataset with the new resolution.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.NullHandler())

    fourth_dim = validate_dimensions(ds)

    # Assuming square resolution
    input_resolution = ds.rio.resolution()[0]
    upscale_factor = input_resolution / resampled_resolution

    logger.debug(
        f"Input resolution is {input_resolution}. Upscaling by a factor of {upscale_factor}."
    )

    new_width = int(ds.rio.width * upscale_factor)
    new_height = int(ds.rio.height * upscale_factor)

    logger.debug(
        f"New raster will have a width of {new_width} pixels and height of {new_height} pixels."
    )

    if ds.rio.crs is None:
        logger.warning(
            "Input raster data did not have CRS defined. Setting to EPSG:4326."
        )
        ds = ds.rio.write_crs("EPSG:4326")

    if fourth_dim:  # 4D case
        resampled_arrays = []

        for val in ds[fourth_dim].values:
            ds_ = ds.sel({fourth_dim: val})
            ds_ = ds_.rio.reproject(
                ds_.rio.crs,
                shape=(new_height, new_width),
                resampling=Resampling.nearest,
                nodata=np.nan,
            )
            # Expand along the fourth dimension
            if fourth_dim == "band":
                # Falls under different bands, use the long_name instead of integer value
                if int(ds_["band"]) == 1:
                    ds_ = ds_.expand_dims({"band": ["SFED"]})
                else:
                    ds_ = ds_.expand_dims({"band": ["MFED"]})
            else:
                ds_ = ds_.expand_dims([fourth_dim])
            resampled_arrays.append(ds_)

        ds_resampled = xr.combine_by_coords(
            resampled_arrays, combine_attrs="drop"
        )
    else:  # 3D case (x, y, date)
        ds_resampled = ds.rio.reproject(
            ds.rio.crs,
            shape=(new_height, new_width),
            resampling=Resampling.nearest,
            nodata=np.nan,
        )

    return ds_resampled
