import pandas as pd
import numpy as np
import streamlit as st

@st.experimental_memo()
def import_data():
    """
    An argument-less function that imports all of the hourly SF Bay water data
    
    Returns:
        d (pd.DataFrame) - A dataframe containing hourly San Francisco Bay water temperatures between 1994 and 2023
    """
    
    d = pd.read_csv("water_temp_data/1994.csv")
    for year in np.arange(start = 1995, stop = 2023):
        file = "water_temp_data/"+str(year)+".csv"
        year_data = pd.read_csv(file)
        d = pd.concat([d,year_data])
    
    #Cleaning up the dataframe
    d.rename(columns = {d.columns[0]:"date", d.columns[1]:"time", d.columns[2]: "temp"}, inplace = True)
    d = d.loc[:,["date", "time", "temp"]]
    d.loc[d.temp == "-","temp"] = np.nan
    d.temp = d.temp.astype("float")
    d.reset_index(inplace = True)

    #Formatting year, month, day columns
    d.date = pd.to_datetime(d.date)
    d["year"] = d.date.dt.year
    d["month"] = d.date.dt.month
    d["day"] = d.date.dt.day
    d["doy"] = d.date.dt.dayofyear

    return d

@st.experimental_memo
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
    daily_average = data.groupby(by = ["year", "month", "day","doy"], as_index = False).agg(Mean = ("temp", np.mean), Sd = ("temp", np.std))
    daily_average.sort_values(by = ["year","month","doy"], inplace = True)
    daily_average.reset_index(inplace = True)

    #Daily average across all years
    da2 = daily_average.groupby(by = ["doy"], as_index = False).agg(Mean = ("Mean", np.mean), Sd = ("Mean", np.std), N = ("Mean", len))
    da2.sort_values(by = ["doy"], inplace = True)
    da2.reset_index(inplace = True)

    #5 Warmest and coldest days of the year on average
    da2.sort_values(by = "Mean", inplace = False)

    return daily_average, da2