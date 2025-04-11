from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def blank_plot(center_text=None):
    fig = go.Figure()

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350,
        font=dict(
            family="Source Sans Pro, sans-serif",
            color="#888888",  # Colors all text
        ),
    )

    fig.update_xaxes(
        showgrid=False,  # Remove grid lines
        zeroline=False,  # Remove zero line
        showline=False,  # Show axis line
        linecolor="black",  # Axis line color
        linewidth=1,
        ticks="",  # Remove ticks
        showticklabels=False,  # Remove tick labels
    )

    fig.update_yaxes(
        showgrid=False,  # Remove grid lines
        zeroline=False,  # Remove zero line
        showline=False,  # Show axis line
        linecolor="black",  # Axis line color
        linewidth=1,
        ticks="",  # Remove ticks
        showticklabels=False,  # Remove tick labels
    )
    if center_text:
        fig.add_annotation(
            text=center_text,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=24,
            ),
        )
    return fig


def plot_floodscan_timeseries(df, issued_date, stat="mean"):
    cur_year = datetime.strptime(issued_date, "%Y-%m-%d").year

    fig = go.Figure()
    unique_group = sorted(df["group"].unique())

    # Add a trace for each year
    for group in unique_group:
        year_data = df[df["group"] == group]
        year_end = list(year_data["valid_year"])[-1]

        color = "#c25048" if year_end == cur_year else "#f7a29c"
        width = 4 if year_end == cur_year else 1

        fig.add_trace(
            go.Scatter(
                x=year_data["month_day"],
                y=year_data[stat],
                mode="lines",
                name=str(year_end),
                line=dict(color=color, width=width),
                hovertemplate="<b>Valid Date:</b> %{x}<br>"
                + "<b>Value:</b> %{y:.3f}<extra></extra>",
            )
        )

    # Add a point just for the recent update
    df["valid_date"] = pd.to_datetime(df["valid_date"])
    df_single = df[df["valid_date"] == issued_date]
    fig.add_trace(
        go.Scatter(
            x=df_single["month_day"],
            y=df_single[stat],
            mode="markers",
            marker_size=15,
            name="Selected point",
            marker_color="#c25048",
        )
    )
    fig.update_layout(
        template="simple_white",
        xaxis_title="Date",
        yaxis_title=stat,
        legend_title_text="Year",
    )

    fig.update_layout(
        legend=dict(traceorder="reversed"),
        margin={"l": 0, "r": 0, "t": 50, "b": 10},
        font=dict(
            family="Source Sans Pro, sans-serif",
            color="#888888",  # Colors all text
        ),
        title=f"{stat.capitalize()} of Floodscan flooded fraction",
    )

    return fig


def plot_seas5_timeseries(df, issued_date, stat="mean"):
    cur_year = datetime.strptime(issued_date, "%Y-%m-%d").year

    fig = go.Figure()
    unique_years = sorted(df["issued_year"].unique())

    for year in unique_years:
        year_data = df[df["issued_year"] == year]
        color = "#c25048" if year == cur_year else "#f7a29c"
        width = 4 if year == cur_year else 1

        fig.add_trace(
            go.Scatter(
                x=year_data["leadtime"],
                y=year_data[stat],
                mode="lines",
                name=str(year),
                line=dict(color=color, width=width),
                hovertemplate="<b>Valid Date:</b> %{customdata[0]|%Y-%m-%d}<br>"
                + "<b>Leadtime:</b> %{x} months<br>"
                + "<b>Issued Date:</b> %{customdata[1]|%Y-%m-%d}<br>"
                + "<b>Value:</b> %{y:.3f}<extra></extra>",
                customdata=year_data[["valid_date", "issued_date"]].values,
            )
        )

    fig.update_layout(
        template="simple_white",
        xaxis_title="Leadtime",
        yaxis_title=stat,
        legend_title_text="Year",
        height=350,
        title=f"{stat.capitalize()} of SEAS5 precipitation (mm/day) across forecast leadtimes",
    )

    fig.update_layout(
        legend=dict(traceorder="reversed"),
        margin={"l": 0, "r": 0, "t": 50, "b": 10},
        font=dict(
            family="Source Sans Pro, sans-serif",
            color="#888888",  # Colors all text
        ),
    )

    return fig


def plot_cogs(da, title):
    units = da.attrs["units"]
    # Eg. if leadtime dimension
    if len(da.shape) == 3:
        fig = px.imshow(
            da.values,
            color_continuous_scale="Blues",
            template="simple_white",
            facet_col=0,
            facet_col_wrap=4,
            labels={"color": units},
        )
    elif len(da.shape) == 2:
        fig = px.imshow(
            da.values,
            color_continuous_scale="Blues",
            template="simple_white",
            labels={"color": units},
            zmin=0,
            zmax=1,
        )
    fig.update_layout(
        margin={"l": 20, "r": 0, "t": 50, "b": 10},
        height=350,
        font=dict(
            family="Source Sans Pro, sans-serif",
            color="#888888",  # Colors all text
        ),
        title=title,
    )

    # This only shows up now for SEAS5
    leadtime_units = da.attrs["leadtime_units"]
    for annotation in fig.layout.annotations:
        lead_time = annotation.text.split("=")[1]
        annotation.text = f"Leadtime: {lead_time} {leadtime_units}"

    fig.update_traces(hovertemplate=f"%{{z:.4f}} {units}<extra></extra>")
    fig.update_xaxes(showline=False, ticks="", showticklabels=False)
    fig.update_yaxes(showline=False, ticks="", showticklabels=False)
    return fig
