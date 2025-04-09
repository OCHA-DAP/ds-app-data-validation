import ocha_stratus as stratus
import xarray as xr

from src.constants import STAGE


def open_floodscan_cog(valid_date_str: str):
    blob_name = f"floodscan/daily/v5/processed/aer_area_300s_v{valid_date_str}_v05r01.tif"
    return stratus.open_blob_cog(
        blob_name, stage=STAGE, container_name="raster"
    )


def open_floodscan_rasters(valid_date_str: str, band: str):
    das = []
    bands = {"SFED": 1, "MFED": 2}
    da_in = open_floodscan_cog(valid_date_str).sel(band=bands[band])
    da_in = da_in.squeeze(drop=True)
    das.append(da_in)
    da_out = xr.combine_by_coords(das, combine_attrs="drop_conflicts")
    da_out = da_out.expand_dims(date=[valid_date_str])

    return da_out
