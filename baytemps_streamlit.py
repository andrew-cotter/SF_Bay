import streamlit as st
import streamlit_funcs.baytemps as bt

import arviz as az

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime as dt

st.set_page_config(layout = "centered")
st.write("## San Francisco Bay Water Temperature")

#Try/except to account for times when the data retrieval from NOAA fails
# try:
#     new_df = bt.import_data()
#     old_df = pd.read_csv("up_to_2024.csv")
#     d = pd.concat([old_df, new_df])
#     d2=bt.garmin_data()
# except:
# st.markdown("##### :red[There was an error retrieving the most recent data. You are viewing an archived subset.]")
# st.markdown("##### :red[Feel free to visit the [NOAA webiste](https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290) to view more up-to-date info, or check back here in a few hours]")

st.markdown(""":red[
            The NOAA temperature gauge has been offline for most of 2024 due to it being buried in the sand.
            Therefore, the temperature data since then is comprised of minimum temperatures collected by my Garmin watch on the days that I swim.
            ]""")

#Read in historial data (NOAA)
d = pd.read_csv("up_to_2024.csv")
d["source"]="NOAA"

#Read in garmin data
d2=bt.garmin_data()
d=pd.concat([d, d2])

#Outlier detection and produce summaries
d, outliers = bt.outlier_detection(d)
daily_average, da2 = bt.average_daily_data(data = d)

# df = bt.import_data()
# st.write(df)
# df.to_csv("up_to_2024.csv", index = False)


st.markdown("""---""")
st.write(
    "#### Most recent: "+
    str(d.iloc[-1,3].round(1))+"\N{DEGREE SIGN}F on "+ #temp
    str(d.iloc[-1,5])+"-"+ #month
    str(d.iloc[-1,6])+"-"+ #day
    str(d.iloc[-1,4])+ #year
    " at "+str(d.iloc[-1,2])+" Pacific Time" #Time
    )

temp_col = 6
todays_average = daily_average.iloc[-1,temp_col]
yesterdays_average = daily_average.iloc[-2,temp_col]
last_week_average = daily_average.iloc[-7,temp_col]
day_delta = (todays_average - yesterdays_average).round(1)
week_delta = (todays_average - last_week_average).round(1)
col1,col2,col3 = st.columns(3)
with col1:
    st.metric("Today's Average Temperature", str(todays_average.round(1))+"\N{DEGREE SIGN}F")
with col2:
    st.metric("Yesterday's Average Temperature", str(yesterdays_average.round(1))+"\N{DEGREE SIGN}F", day_delta)
with col3:
    st.metric("7 Days Ago", str(last_week_average.round(1))+"\N{DEGREE SIGN}F", week_delta)


st.markdown("""---""")
st.write("## Yearly trends")


#Creating a year x day matrix of mean temperature values for use in the az.plot_hdi function
interval_data = pd.DataFrame(
    daily_average.loc[
        daily_average.year<=2026,:
    ].pivot_table(
        index = "year",columns = "doy", values = "Mean"
        )
)
#Imputing missing values (average temperature from all other years)
interval_data = interval_data.fillna(interval_data.mean())

#Interactive plotting
year = st.number_input(
    label = "Enter a year between 1994 and 2026",
    min_value = 1994, max_value = 2026, 
    value = 2026
)
fig, ax = plt.subplots(figsize = (9,6))
#Creating the 90% interval shaded region
az.plot_hdi(
    x = da2.doy, y = interval_data, 
    hdi_prob = 0.9, fill_kwargs = {"label": "5th-95th Percentile (1994-2023)"}
    )
#Average daily temperatures across all years
plt.plot(da2.doy, da2.Mean, label = "Average (1994-2023)", linestyle = "--")

for year_trace in daily_average.year.unique():
    plt.plot(
        daily_average.loc[daily_average.year == year_trace,"doy"],
        daily_average.loc[daily_average.year == year_trace,"Mean"], 
        color = "Grey", alpha = 0.1
    )

source_colors = {'Garmin': 'blue', 'NOAA': 'teal'} 
#Average daily temperature from selected year
# Loop over each source for the selected year
for source in daily_average.source.unique():
    # Filter data for the current year and source
    data = daily_average[(daily_average.year == year) & (daily_average.source == source)]
    
    # Only plot if there is data for that source in the selected year
    if not data.empty:
        plt.plot(
            data["doy"],
            data["Mean"],
            color=source_colors[source],  # Assign color based on source
            label=f'{source}',  # Label with the source
            alpha=0.7  # Adjust transparency for better visualization
        )


plt.grid(axis='y', linestyle = "--")
ax.set_xlabel("Date")
ax.set_ylabel("Average Temperature (\N{DEGREE SIGN}F)")
ax.set_ylim(bottom = 48, top = 67.5)
ax.set_xticks([1,32,60,91,121,152,182,213,244,274,305,335])
ax.set_xticklabels(["Jan-1","Feb-1","Mar-1","Apr-1","May-1","Jun-1","Jul-1","Aug-1","Sep-1","Oct-1","Nov-1","Dec-1"])
ax.set_yticks(np.arange(49,68,1))
ax.legend()
plt.xticks(rotation = 45)
st.pyplot(fig)

year_outliers=outliers.loc[outliers.year==year]
if len(year_outliers.index)>0:
    with st.expander(f"Outliers in {year}"):
        st.write("The following data points in this year were detected as outliers and corrected to the average temperature for that day of the year:")
        st.write(year_outliers.drop_duplicates().reset_index(drop=True))

st.markdown("Data from [NOAA Tides & Currents](https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290) and my personal Garmin Watch.")
