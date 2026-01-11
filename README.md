# San Francisco Bay Water Temperature Analysis

A comprehensive data analysis and visualization project tracking water temperatures in the San Francisco Bay from 1994 to present. This project combines historical NOAA buoy data with personal Garmin watch measurements to provide insights into long-term temperature trends and daily conditions for open water swimmers.

## 🌊 About

This repository contains tools and analyses for monitoring and visualizing San Francisco Bay water temperatures. The project was created by an open water swimmer to track temperature trends and make data-driven decisions about swimming conditions. All temperature data is sourced from the NOAA buoy located on the west end of Crissy Field near the south tower of the Golden Gate Bridge (Station ID #9414290).

**Note:** Since 2024, the NOAA temperature gauge has been offline (buried in sand), so recent data is supplemented with minimum temperatures collected from a personal Garmin watch during swimming sessions.

## ✨ Features

- **Interactive Dashboard**: Streamlit web application for exploring temperature trends
- **Historical Analysis**: Jupyter notebook with statistical analysis of 30+ years of data
- **Outlier Detection**: Automated detection and correction of anomalous temperature readings
- **Yearly Comparisons**: Visualize how any year compares to historical averages and percentiles
- **Daily Metrics**: Track current conditions with comparisons to yesterday and last week
- **Multi-Source Data**: Combines NOAA buoy data (1994-2023) with Garmin watch data (2024+)

## 🚀 Live Demo

The interactive dashboard is available online at
**[https://sfbaytemp.streamlit.app](https://sfbaytemp.streamlit.app)**

## 📊 Data Sources

- **NOAA Tides & Currents**: Hourly water temperature data from Station #9414290 (1994-2023)
  - Data available at: [NOAA Website](https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290)
- **Garmin Watch**: Personal swimming activity data (2024+)
  - Minimum temperatures recorded during open water swimming sessions
  - Data smoothed with a 5-day rolling average

## 📁 Project Structure

```
SF_Bay/
├── baytemps_streamlit.py      # Main Streamlit dashboard application
├── streamlit_funcs/
│   └── baytemps.py            # Helper functions for data processing
├── analysis.ipynb             # Jupyter notebook with statistical analysis
├── water_temp_data/           # Historical CSV files (1994-2022)
│   ├── 1994.csv
│   ├── 1995.csv
│   └── ...
├── up_to_2024.csv            # Consolidated NOAA data through 2024
├── requirements.txt           # Python dependencies
└── images/                    # Supporting images and visualizations
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository** (or download the files)

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Running the Streamlit Dashboard

To launch the interactive dashboard locally:

```bash
streamlit run baytemps_streamlit.py
```

The dashboard will open in your default web browser, typically at `http://localhost:8501`.

### Features of the Dashboard

- **Current Conditions**: View the most recent temperature reading with date and time
- **Daily Metrics**: Compare today's average temperature with yesterday and last week
- **Yearly Trends**: Select any year (1994-2026) to see how it compares to:
  - Historical average (1994-2023)
  - 5th-95th percentile range
  - Individual year traces
- **Outlier Detection**: View and review any temperature outliers detected and corrected for the selected year

### Running the Analysis Notebook

Open `analysis.ipynb` in Jupyter Notebook or JupyterLab to explore the statistical analysis:

```bash
jupyter notebook analysis.ipynb
```

## 📈 Key Insights

The analysis includes:
- Long-term temperature trends from 1994 to present
- Seasonal patterns and year-to-year variations
- Statistical modeling using PyMC for temperature predictions
- Comparison of different data sources (NOAA vs. Garmin)

## 🔧 Technical Details

### Data Processing

- **Outlier Detection**: Uses z-score analysis (threshold: 3.5) grouped by day of year
- **Data Aggregation**: Hourly data is averaged to daily means
- **Missing Data**: Handled through imputation using historical averages
- **Leap Years**: February 29th data is excluded for consistency

### Technologies Used

- **Streamlit**: Interactive web dashboard
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Data visualization
- **PyMC/ArviZ**: Bayesian statistical modeling
- **NumPy/SciPy**: Numerical computations
- **MySQL**: Garmin watch data storage (via Streamlit connections)

## 📝 Notes

- The NOAA buoy temperature readings are typically 1-2°F warmer than temperatures experienced in Aquatic Park Cove (a popular swimming location)
- Absolute temperature values may differ from other locations, but trends and comparisons should be consistent
- Recent data (2024+) relies on personal Garmin watch measurements, which represent minimum temperatures during swimming sessions

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to open issues or submit pull requests.

## 📄 License

This project uses publicly available NOAA data and personal measurements. Please refer to NOAA's data usage policies for the temperature data.

## 🔗 Links

- [NOAA Tides & Currents - Station #9414290](https://tidesandcurrents.noaa.gov/stationhome.html?id=9414290)
- [Live Dashboard](https://sfbaytemp.streamlit.app)

---

*Last Updated: 2024*
