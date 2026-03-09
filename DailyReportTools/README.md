# Realm Analytics Dashboard

An interactive dashboard for analyzing daily realm analytics CSV files.

## Features

- 📊 **Interactive Time Series Graphs**: Visualize resources, items, and player counts over time
- 📈 **Multi-metric Analysis**: Track multiple resources and items simultaneously
- 🎮 **Player Trends**: Monitor player count changes
- 📅 **Date Filtering**: Filter data by specific date ranges
- 📋 **Raw Data View**: Access the underlying data table

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

3. **Open Browser**: Navigate to the URL shown in terminal (usually `http://localhost:8501`)

## File Structure

```
DailyReportTools/
├── dashboard.py          # Main dashboard application
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── Daily Reports/       # Folder for CSV files
    ├── realm_Ruby_analytics_2026-03-05_220406.csv
    ├── realm_Ruby_analytics_2026-03-06_221843.csv
    └── ...
```

## CSV Format

The dashboard expects CSV files with this structure:
- Realm Summary section (realm name, total players)
- Resources section (resource types with total amounts)
- Items section (item definitions with amounts)

## Dashboard Sections

### 📊 Overview Tab
- Player count trends over time
- Key metrics summary

### 📈 Resources Tab
- Select and visualize multiple resources
- Individual graphs for each resource type
- Hover tooltips for exact values

### 🎮 Items Tab
- Track item amounts over time
- Multi-item comparison views

## Adding New Data

Simply drop new CSV files into the `Daily Reports` folder and refresh the dashboard - it will automatically detect and parse new files.

## Customization

The dashboard is built with Streamlit and Plotly, making it easy to:
- Add new chart types
- Customize styling
- Add additional metrics
- Export data or charts
