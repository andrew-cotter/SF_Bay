import pandas as pd
import numpy as np
from scipy import stats
import streamlit as st

def doy(month,day):
    months = [31,28,31,30,31,30,31,31,30,31,30,31]
    return sum(months[0:month-1])+day

@st.cache_data(ttl = 60*60)
def import_data():
    """
    An argument-less function that imports all of the hourly SF Bay water data
    
    Returns:
        d (pd.DataFrame) - A dataframe containing hourly San Francisco Bay water temperatures between 1994 and 2023
    """

    d = pd.read_csv("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_temperature&application=NOS.COOPS.TAC.PHYSOCEAN&begin_date=19930414&end_date=19940413&station=9414290&time_zone=lst_ldt&units=english&interval=h&format=csv")
    for year in np.arange(start = 2023, stop = 2024):
        url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_temperature&application=NOS.COOPS.TAC.PHYSOCEAN&begin_date="+str(year)+"0414&end_date="+str(year+1)+"0413&station=9414290&time_zone=lst_ldt&units=english&interval=h&format=csv"
        #file = "data/water_temp/"+str(year)+".csv"
        year_data = pd.read_csv(url)
        d = pd.concat([d,year_data])
    d["Date Time"] = pd.to_datetime(d["Date Time"])
    d["Date Time"] = d["Date Time"].astype("str")
    d[["date","time"]] = d["Date Time"].str.split(" ", expand = True)   
    
    #Cleaning up the dataframe
    d.rename(columns = {d.columns[1]:"temp"}, inplace = True)
    d = d.loc[:,["date", "time", "temp"]]
    d.loc[d.temp == "-","temp"] = np.nan
    d.temp = d.temp.astype("float")
    d.reset_index(inplace = True)

    #Formatting year, month, day columns
    d.date = pd.to_datetime(d.date)
    #d.date = d.date - pd.timedelta(hours = 7)
    d["year"] = d.date.dt.year
    d["month"] = d.date.dt.month
    d["day"] = d.date.dt.day
   
    #Remove Feb29
    d = d[~((d.date.dt.month == 2) & (d.date.dt.day == 29))]
    
    #Tag each day with day of year, assuming no leap years
    d["doy"] = 0
    for i in d.index:
        d["doy"][i] = doy(d.month[i], d.day[i])

    d["source"]="NOAA"

    return d

@st.cache_data
def outlier_detection(df, measurement_column="temp", group_column="doy", z_thresh=3.5):
    #calculate mean temperature for each day of year
    mean_temps=df.groupby(group_column)[measurement_column].transform("mean")
    #calculate z score for temperatures within each day of year
    df["zscore"]=df.groupby(group_column)[measurement_column].transform(lambda x: stats.zscore(x, nan_policy="omit"))
    #outlier detection
    outliers=np.abs(df.zscore)>z_thresh
    outliers_df = df.copy(deep=True).loc[outliers,:]
    #replace outliers
    df.loc[outliers, measurement_column]=mean_temps[outliers]
    return df, outliers_df


@st.cache_data
def average_daily_data(data: pd.DataFrame):
    """
    Takes the raw hourly temperature data and summarizes it into daily averages

    Arguments:
        data (pd.DataFrame): Raw hourly temperature data, the same dataframe returned by import_data
    
    Returns:
        daily_average (pd.DataFrame): A dataframe containing the average temperature for every individual day going back to 1994
        da2 (pd.DataFrame): A dataframe containing the averate temperature for every day of the year across all years
    """
    #Calculating averages for each day for every DOY in the dataset (within each year)
    daily_average = data.groupby(by = ["year", "month", "day","doy", "source"], as_index = False).agg(Mean = ("temp", np.mean), Sd = ("temp", np.std))
    daily_average.sort_values(by = ["year","month","doy"], inplace = True)
    daily_average.reset_index(inplace = True)

    #Daily average across all years
    da2 = daily_average.groupby(by = ["doy","month","day"], as_index = False).agg(Mean = ("Mean", np.mean), Sd = ("Mean", np.std), N = ("Mean", len))
    da2.sort_values(by = ["doy"], inplace = True)
    da2.reset_index(inplace = True)


    return daily_average, da2

@st.cache_data
def garmin_data():

    """Pulls data from a personal garmin watch database and formats it to match the NOAA temperature data. Also applies a 5 day rolling average to smooth out the noise"""

    conn=st.connection("mysql", type='sql')
    
    query = "SELECT startTimeLocal date, minTemperature*1.8+32 temp FROM garmin.activities\
        WHERE activityName LIKE 'San Francisco%' \
        AND activityName LIKE '%Open Water Swimming'\
        AND elapsedDuration/3600 > 0.25\
        AND minTemperature IS NOT NULL\
    "
    d=conn.query(query, ttl=600).reset_index()
    d.date = pd.to_datetime(d.date)
    d=d.sort_values(by="date")
    d["temprolling"]=d["temp"].rolling(window=5).mean()
    d.temp=d.temprolling
    d=d.drop(labels="temprolling", axis=1)
    
    d["time"] = d.date.dt.time
    d["year"] = d.date.dt.year
    d["month"] = d.date.dt.month
    d["day"] = d.date.dt.day

    #Tag each day with day of year, assuming no leap years
    d["doy"] = 0
    for i in d.index:
        d["doy"][i] = doy(d.month[i], d.day[i])

    d=d[["index", "date", "time", "temp", "year", "month", "day", "doy"]]
    d["source"]="Garmin"
    return(d)
