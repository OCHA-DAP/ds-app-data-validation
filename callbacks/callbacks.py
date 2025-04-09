import dash
import ocha_stratus as stratus
import pandas as pd
from dash.dependencies import Input, Output, State
from rasterio.errors import RasterioIOError
from sqlalchemy import text

from constants import STAGE
from src.datasources import codab, floodscan, seas5
from src.utils import date_utils, plot_utils, raster


def register_callbacks(app):
    @app.callback(
        Output("iso3-data", "data"), Input("interval-component", "n_intervals")
    )
    def load_iso3_data(_):
        print("Loading ISO3 data...")
        engine = stratus.get_engine(STAGE)
        with engine.connect() as conn:
            df_iso3 = pd.read_sql(
                "select iso3, max_adm_level, floodscan from iso3", con=conn
            )
        return df_iso3.to_dict()

    @app.callback(
        Output("band-select-div", "style"), Input("dataset-dropdown", "value")
    )
    def display_band(dataset):
        if dataset == "floodscan":
            return {}
        return {"display": "none"}

    @app.callback(
        Output("issue-date-dropdown", "options"),
        Output("issue-date-dropdown", "value"),
        Input("dataset-dropdown", "value"),
    )
    def update_issue_dates(dataset):
        dates = date_utils.get_date_range(dataset)
        return dates, dates[0]

    @app.callback(
        Output("iso3-dropdown", "options"),
        Output("iso3-dropdown", "value"),
        Input("dataset-dropdown", "value"),
        Input("iso3-data", "data"),
    )
    def update_iso3(dataset, iso3_data):
        if iso3_data:
            df_iso3 = pd.DataFrame.from_dict(iso3_data)
            if dataset == "floodscan":
                df_iso3 = df_iso3[df_iso3["floodscan"]]
            iso3s = list(df_iso3["iso3"])
            return iso3s, iso3s[0]
        return dash.no_update, dash.no_update

    @app.callback(
        Output("adm-level-dropdown", "options"),
        Input("iso3-dropdown", "value"),
        Input("iso3-data", "data"),
    )
    def update_adm_level(iso3, iso3_data):
        if iso3_data:
            df_iso3 = pd.DataFrame.from_dict(iso3_data)
            max_adm_level = df_iso3.loc[
                df_iso3["iso3"] == iso3, "max_adm_level"
            ].values[0]
            return list(range(max_adm_level + 1))
        return dash.no_update

    @app.callback(
        Output("pcode-dropdown", "options"),
        Output("pcode-dropdown", "value"),
        Input("iso3-dropdown", "value"),
        Input("adm-level-dropdown", "value"),
    )
    def update_pcode(iso3, adm_level):
        engine = stratus.get_engine(STAGE)
        with engine.connect() as conn:
            df_pcodes = pd.read_sql(
                text(
                    """
                select iso3, pcode, name, adm_level from polygon
                where iso3=:iso3 and
                adm_level=:adm_level
                """
                ),
                con=conn,
                params={"iso3": iso3, "adm_level": adm_level},
            )
        options = [
            {"label": row["name"], "value": row["pcode"]}
            for _, row in df_pcodes.iterrows()
        ]
        pcode_value = options[0]["value"] if len(options) == 1 else None
        return options, pcode_value

    @app.callback(
        Output("raster-stats-data", "data"),
        Output("chart-leadtime-series", "figure"),
        Input("dataset-dropdown", "value"),
        Input("iso3-dropdown", "value"),
        Input("adm-level-dropdown", "value"),
        Input("pcode-dropdown", "value"),
        Input("issue-date-dropdown", "value"),
        Input("band-select", "value"),
    )
    def get_raster_stats(dataset, iso3, adm_level, pcode, issue_date, band):
        if dataset and iso3 and adm_level and pcode and issue_date:
            if dataset == "seas5":
                df = seas5.get_raster_stats(iso3, pcode, issue_date)
            elif dataset == "floodscan":
                df = floodscan.get_raster_stats(iso3, pcode, issue_date, band)
            return df.to_dict("records"), dash.no_update
        return None, dash.no_update

    @app.callback(
        Output("chart-leadtime-series", "figure", allow_duplicate=True),
        Input("raster-stats-data", "data"),
        Input("stat-dropdown", "value"),
        State("dataset-dropdown", "value"),
        State("issue-date-dropdown", "value"),
        prevent_initial_call=True,
    )
    def plot_raster_stats(data, stat, dataset, issued_date):
        if data:
            df = pd.DataFrame(data)
            if dataset == "seas5":
                return plot_utils.plot_seas5_timeseries(df, issued_date, stat)
            elif dataset == "floodscan":
                return plot_utils.plot_floodscan_timeseries(
                    df, issued_date, stat
                )
        elif data == []:
            return plot_utils.blank_plot("No data available")
        return plot_utils.blank_plot("Select AOI from dropdowns")

    @app.callback(
        Output("chart-cog", "figure"),
        Input("iso3-dropdown", "value"),
        Input("adm-level-dropdown", "value"),
        Input("pcode-dropdown", "value"),
        Input("issue-date-dropdown", "value"),
        Input("raster-display", "value"),
        Input("band-select", "value"),
        State("dataset-dropdown", "value"),
    )
    def plot_cogs(
        iso3, adm_level, pcode, issue_date, raster_display, band, dataset
    ):
        if iso3 and adm_level and pcode and issue_date:
            # Get the geo bounds
            gdf = codab.load_codab_from_blob(iso3, admin_level=adm_level)
            gdf = gdf[gdf[f"ADM{adm_level}_PCODE"] == pcode]

            # Get the seas5 rasters
            try:
                if dataset == "seas5":
                    title = "Pixelwise precipitation (mm/day) across leadtimes"
                    da = seas5.open_seas5_rasters(issue_date)
                elif dataset == "floodscan":
                    title = "Pixelwise flooded fraction"
                    da = floodscan.open_floodscan_rasters(issue_date, band)
                else:
                    return plot_utils.blank_plot("Invalid dataset")
            except RasterioIOError:
                return plot_utils.blank_plot("No data available")

            # Upsample if needed
            if raster_display == "upsampled":
                da = da.rio.clip(gdf.geometry, all_touched=True)
                da = raster.upsample_raster(da)
            try:
                da = da.rio.clip(gdf.geometry).sel(date=issue_date)
            except Exception:
                return plot_utils.blank_plot("No data in bounds")

            # Now plot
            return plot_utils.plot_cogs(da, title)
        return plot_utils.blank_plot("Select AOI from dropdowns")
