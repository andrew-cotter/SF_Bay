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

The interactive dashboard is available online at:
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

### Secrets (Docker / production)

The app uses `st.connection("mysql", type="sql")`, which reads `[connections.mysql]` from `.streamlit/secrets.toml`. For Docker or AWS you can supply secrets in any of these ways:

1. **Environment variables (recommended)**  
   The image’s entrypoint builds `secrets.toml` from env vars when `MYSQL_HOST` is set. Set:
   - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`
   - Optional: `MYSQL_PORT` (default 3306), `MYSQL_DATABASE` (default `defaultdb`), `MYSQL_QUERY_CHARSET`  
   Example: `docker run -e MYSQL_HOST=... -e MYSQL_USER=... -e MYSQL_PASSWORD=... -p 8501:8501 baytemps`  
   On ECS/App Runner, pass these from **AWS Secrets Manager** (e.g. store a JSON and map keys to env) or **Systems Manager Parameter Store**.

2. **Mount a secrets file**  
   Build `.streamlit/secrets.toml` locally (or from a secret manager) and mount it:
   `docker run -v /path/to/secrets.toml:/app/.streamlit/secrets.toml -p 8501:8501 baytemps`

3. **AWS Secrets Manager at startup**  
   Use an IAM role and a small script that fetches the secret (e.g. `aws secretsmanager get-secret-value`), writes `.streamlit/secrets.toml`, then runs the Streamlit command. The current entrypoint only handles env vars; extend it or run a wrapper script if you prefer fetch-from-Secrets-Manager.

### EC2 deployment (Secrets Manager)

**New to this?** There’s a **step-by-step walkthrough** that explains why the app needs secrets and exactly what to run on EC2: **[docs/EC2-SETUP-WALKTHROUGH.md](docs/EC2-SETUP-WALKTHROUGH.md)**. Do that first if you’re unsure.

The repo includes scripts to run the app on EC2 using credentials stored in **AWS Secrets Manager**.

**Prerequisites on the EC2 instance:**

- IAM role with `secretsmanager:GetSecretValue` on your secret
- Docker installed and running (`sudo usermod -aG docker ec2-user` then log out/in so you can run `docker` without sudo)
- `jq` installed (`sudo yum install -y jq` or `sudo apt install -y jq`)
- Docker image available (build locally or pull from ECR)

**Secret format in Secrets Manager:** JSON with keys `host`, `port`, `username`, `password`, `database`. If your secret uses different key names, set the `SECRET_KEY_*` env vars when running the script (see script header).

**One-time run:**

```bash
# Copy script to the instance (e.g. to /opt/baytemps), then:
chmod +x /opt/baytemps/ec2-start-baytemps.sh
SECRET_ID=your-secret-name AWS_REGION=us-east-1 /opt/baytemps/ec2-start-baytemps.sh
```

If you need `sudo` for Docker: `DOCKER_CMD=sudo docker SECRET_ID=... AWS_REGION=... ./ec2-start-baytemps.sh`

**Run on every boot (systemd):**

1. Copy `scripts/ec2-start-baytemps.sh` and `scripts/baytemps.service` to the instance.
2. Put the script in `/opt/baytemps/` and run `chmod +x /opt/baytemps/ec2-start-baytemps.sh`.
3. Edit the service file: set `Environment=SECRET_ID=...` and `Environment=AWS_REGION=...` (and optionally `DOCKER_IMAGE` if using ECR).
4. Install the unit: `sudo cp baytemps.service /etc/systemd/system/` then `sudo systemctl daemon-reload && sudo systemctl enable baytemps && sudo systemctl start baytemps`.

After startup, the app is available on port **8501**; ensure the instance security group allows inbound traffic on that port.

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
