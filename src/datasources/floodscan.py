from datetime import datetime, timedelta

import ocha_stratus as stratus
import pandas as pd
import xarray as xr
from sqlalchemy import text

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


def get_raster_stats(iso3, pcode, issue_date, band, date_range=10):
    date_obj = datetime.strptime(issue_date, "%Y-%m-%d")

    # Create a list of MM-DD strings to match
    mm_dd_list = []
    for i in range(date_range):
        day = date_obj - timedelta(i)
        mm_dd_list.append(day.strftime("%m-%d"))

    query = text(
        """
        SELECT *
        FROM floodscan
        WHERE
            TO_CHAR(valid_date, 'MM-DD') IN :mm_dd_list
            AND iso3 = :iso3
            AND pcode = :pcode
            AND band = :band
        ORDER BY valid_date DESC;
        """
    )

    engine = stratus.get_engine("prod")
    with engine.connect() as con:
        df = pd.read_sql(
            query,
            con,
            params={
                "pcode": pcode,
                "iso3": iso3,
                "band": band,
                "mm_dd_list": tuple(mm_dd_list),
            },
        )

    df["valid_date"] = pd.to_datetime(df["valid_date"])
    df["valid_year"] = df["valid_date"].dt.year

    df = df.sort_values("valid_date")
    df["group"] = (
        df["valid_date"].diff().dt.days > 30
    ).cumsum()  # Account for some potential gaps
    df["month_day"] = df["valid_date"].dt.strftime("%d-%b")

    return df
