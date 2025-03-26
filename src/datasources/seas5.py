import ocha_stratus as stratus
import pandas as pd
import xarray as xr
from sqlalchemy import text

from src.constants import STAGE


def open_seas5_cog(issued_date_str: str, lt: int):
    blob_name = (
        f"seas5/monthly/processed/precip_em_i{issued_date_str}_lt{lt}.tif"
    )
    return stratus.open_blob_cog(
        blob_name, stage="prod", container_name="raster"
    )


def open_seas5_rasters(issued_date_str: str, gdf):
    das = []
    for lt in range(0, 7):
        da_in = open_seas5_cog(issued_date_str, lt)
        da_in = da_in.squeeze(drop=True)
        da_in["lt"] = da_in.attrs["leadtime"]
        da_in = da_in.expand_dims(["lt"])
        das.append(da_in)
    da_out = xr.combine_by_coords(das, combine_attrs="drop_conflicts")
    da_out = da_out.expand_dims(date=[issued_date_str])

    return da_out


def get_raster_stats(iso3, pcode, issue_date):
    query = text(
        """
        SELECT
            *
        FROM seas5
        WHERE
            EXTRACT(MONTH FROM issued_date) = EXTRACT(MONTH FROM DATE :issued_date) AND
            EXTRACT(DAY FROM issued_date) = EXTRACT(DAY FROM DATE :issued_date) AND
            issued_date >= DATE :issued_date - INTERVAL '40 YEAR' AND
            pcode=:pcode AND
            iso3=:iso3
        ORDER BY issued_date, leadtime;
        """
    )
    engine = stratus.get_engine(STAGE)
    with engine.connect() as con:
        df = pd.read_sql(
            query,
            con,
            params={
                "pcode": pcode,
                "iso3": iso3,
                "issued_date": issue_date,
            },
        )

    df["issued_date"] = pd.to_datetime(df["issued_date"])
    df["issued_year"] = df["issued_date"].dt.year

    return df
