"""
San Francisco Bay water temperature dashboard.
Data: NOAA Tides & Currents and Garmin.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import arviz as az

import streamlit_funcs.baytemps as bt


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

YEAR_MIN, YEAR_MAX = 1994, 2026
TEMP_YLIM = (48, 67.5)
SOURCE_COLORS = {"Garmin": "blue", "NOAA": "teal"}
XTICK_DOY = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
XTICK_LABELS = [
    "Jan-1", "Feb-1", "Mar-1", "Apr-1", "May-1", "Jun-1",
    "Jul-1", "Aug-1", "Sep-1", "Oct-1", "Nov-1", "Dec-1",
]


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

def load_data():
    """Load and prepare NOAA + Garmin data; return main dataframe, daily stats, and outliers."""
    d = pd.read_csv("up_to_2024.csv")
    d["source"] = "NOAA"
    d2 = bt.garmin_data()
    d = pd.concat([d, d2])
    d, outliers = bt.outlier_detection(d)
    daily_average, da2 = bt.average_daily_data(data=d)
    return d, daily_average, da2, outliers


# -----------------------------------------------------------------------------
# Formatting helpers
# -----------------------------------------------------------------------------

def format_latest_reading(row):
    """Format the most recent reading as a short summary string."""
    return (
        f"{row['month']}-{row['day']}-{row['year']} at {row['time']} Pacific Time"
    )


def build_interval_data(daily_average, max_year=2026):
    """Build year x doy matrix for HDI plot; impute missing with cross-year mean."""
    interval_data = pd.DataFrame(
        daily_average.loc[daily_average.year <= max_year].pivot_table(
            index="year", columns="doy", values="Mean"
        )
    )
    return interval_data.fillna(interval_data.mean())


# -----------------------------------------------------------------------------
# UI: metrics and plot
# -----------------------------------------------------------------------------

def render_metrics(daily_average):
    """Render main metric (today's average) centered, then yesterday and 7 days ago on one row."""
    temp_col = "Mean"
    last = daily_average.iloc[-1]
    today_avg = last[temp_col]
    yesterday_avg = daily_average.iloc[-2][temp_col]
    week_ago_avg = daily_average.iloc[-7][temp_col]
    day_delta = (today_avg - yesterday_avg).round(1)
    week_delta = (today_avg - week_ago_avg).round(1)


    # Large centered main metric: today's average (most recent reading period)
    temp_str = f"{today_avg.round(1)}°F"
    st.markdown(
        f'<p style="text-align: center; margin: 0 0 0.1rem 0; font-size: 1.5rem; font-weight: 700; color: var(--text-secondary);">Today\'s Average Temperature</p>'
        f'<p style="text-align: center; margin: 0; font-size: 5rem; font-weight: 700; line-height: 1;">{temp_str}</p>',
        unsafe_allow_html=True,
    )

    # Smaller metrics on one line: yesterday and 7 days ago (same style, smaller)
    def delta_text_and_color(delta, period):
        if delta > 0:
            return f"↗ {abs(delta)}°F from {period} 🔥", "red"
        elif delta < 0:
            return f"↘ {abs(delta)}°F from {period} ❄️", "blue"
        else:
            return f"Unchanged from {period}", "white"

    day_text, day_color = delta_text_and_color(day_delta, "yesterday")
    week_text, week_color = delta_text_and_color(week_delta, "7 days ago")

    st.markdown(
        f'<p style="text-align: center; margin-top: 0rem; font-size: 1.25rem; font-weight: 600; color: {day_color};">{day_text}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="text-align: center; margin-top: -0.5rem; margin-bottom: 2rem; font-size: 1.25rem; font-weight: 600; color: {week_color};">{week_text}</p>',
        unsafe_allow_html=True,
    )


def plot_yearly_trends(daily_average, da2, interval_data, year):
    """Build matplotlib figure for yearly trends and selected year."""
    fig, ax = plt.subplots(figsize=(9, 6))
    az.plot_hdi(
        x=da2.doy,
        y=interval_data,
        hdi_prob=0.9,
        fill_kwargs={"label": "5th-95th Percentile (1994-2023)"},
    )
    plt.plot(da2.doy, da2.Mean, label="Average (1994-2023)", linestyle="--")

    for _, group in daily_average.groupby(["year", "source"]):
        plt.plot(group["doy"], group["Mean"], color="Grey", alpha=0.1)

    for source in daily_average.source.unique():
        data = daily_average[
            (daily_average.year == year) & (daily_average.source == source)
        ]
        if not data.empty:
            plt.plot(
                data["doy"], data["Mean"],
                color=SOURCE_COLORS[source],
                label=source,
                alpha=0.7,
            )

    plt.grid(axis="y", linestyle="--")
    ax.set_xlabel("Date")
    ax.set_ylabel("Average Temperature (\N{DEGREE SIGN}F)")
    ax.set_ylim(bottom=TEMP_YLIM[0], top=TEMP_YLIM[1])
    ax.set_xticks(XTICK_DOY)
    ax.set_xticklabels(XTICK_LABELS)
    ax.set_yticks(np.arange(49, 68, 1))
    ax.legend()
    plt.xticks(rotation=45)
    return fig


# -----------------------------------------------------------------------------
# Main app
# -----------------------------------------------------------------------------

def main():
    st.set_page_config(layout="centered")
    st.write("## San Francisco Bay Water Temperature")

    d, daily_average, da2, outliers = load_data()
    latest = d.iloc[-1]

    st.markdown("---")
    
    render_metrics(daily_average)
    st.markdown(
        f"<div style='display: block; width: 100%; text-align: center;'>{'Last measured ' + format_latest_reading(latest)}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.write("## Yearly trends")

    interval_data = build_interval_data(daily_average, max_year=YEAR_MAX)
    year = st.number_input(
        label=f"Enter a year between {YEAR_MIN} and {YEAR_MAX}",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=YEAR_MAX,
    )
    fig = plot_yearly_trends(daily_average, da2, interval_data, year)
    st.pyplot(fig)

    year_outliers = outliers.loc[outliers.year == year]
    if len(year_outliers.index) > 0:
        with st.expander(f"Outliers in {year}"):
            st.write(
                "The following data points in this year were detected as outliers "
                "and corrected to the average temperature for that day of the year:"
            )
            st.write(year_outliers.drop_duplicates().reset_index(drop=True))

    st.markdown(
        "Data from [NOAA Tides & Currents](https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290) "
        "and my personal [Garmin Watch](https://github.com/andrew-cotter/garmin_db)."
    )


if __name__ == "__main__":
    main()
