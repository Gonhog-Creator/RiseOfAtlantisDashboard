# YAML File Parser

This repository contains Python scripts for parsing various YAML configuration files and converting them into different formats for easier analysis and visualization. The project includes both traditional YAML parsers and a comprehensive analytics dashboard for game data analysis.

## Scripts

### MapCells Parser
**File:** `MapCellsParser.py`

A Python script that parses YAML files containing map cell data and exports the information to a formatted Excel spreadsheet.

**Features:**
- Parses YAML files with terrain/cell type definitions
- Extracts data for multiple levels per terrain type
- Organizes output into structured columns:
  - Column 1: Target Type (capitalized terrain name)
  - Column 2: Target Level
  - Columns 3-6: Resource Gains (Food, Stone, Metal, Lumber)
  - Following columns: Unique items with drop probabilities
  - Final columns: Troop compositions with counts
- Auto-adjusts column widths for better readability
- Handles missing data gracefully (fills with 0)

**Usage:**
```bash
python3 MapCellsParser.py
```

### Buildings Parser
**File:** `BuildingsParser.py`

A Python script that parses YAML files containing building data and exports the information to a formatted Excel spreadsheet.

**Features:**
- Parses YAML files with building type definitions
- Extracts data for multiple levels per building type
- Organizes output into structured columns:
  - Column 1: Building Type (capitalized building name)
  - Column 2: Building Level
  - Columns 3-7: Resource Costs (Food, Lumber, Stone, Metal, Gold)
  - Column 8: Duration
  - Column 9: Population
  - Column 10: Capacity
  - Following columns: Generated Resources (Gen prefix)
  - After resources: Building Requirements (Req prefix)
  - Final columns: Effects (Effect prefix)
- Auto-adjusts column widths for better readability
- Handles missing data gracefully (fills with 0)

**Usage:**
```bash
python3 BuildingsParser.py
```

### Buildings Excel to YAML Converter
**File:** `BuildingsExcelToYamlConverter.py`

A Python script that imports Excel files in the same format as BuildingsParser output and generates updated YAML files while preserving the exact original structure, comments, and formatting.

**Features:**
- Imports Excel files with the exact column structure from BuildingsParser
- Preserves original YAML comments, formatting, and structure
- Maintains effects sections and other metadata from original YAML
- Converts column names back to YAML format (Title Case -> snake_case)
- Handles missing data gracefully
- Preserves building types that weren't modified in the Excel file

**Usage:**
```bash
python3 BuildingsExcelToYamlConverter.py
```

**Workflow:**
1. Use BuildingsParser.py to convert YAML to Excel
2. Edit the Excel file with your changes
3. Use BuildingsExcelToYamlConverter.py to convert back to YAML
4. The output YAML maintains perfect compatibility with the original system

### MapCells Excel to YAML Converter
**File:** `ExcelToYamlMapCells.py`

A Python script that imports Excel files in the same format as MapCellsParser output and generates updated YAML files while preserving the exact original structure, comments, and formatting.

**Features:**
- Imports Excel files with the exact column structure from MapCellsParser
- Preserves original YAML comments, formatting, and structure
- Maintains effects sections and other metadata from original YAML
- Converts column names back to YAML format (Title Case -> snake_case)
- Handles missing data gracefully
- Preserves cell types that weren't modified in the Excel file

**Usage:**
```bash
python3 ExcelToYamlMapCells.py
```

**Workflow:**
1. Use MapCellsParser.py to convert YAML to Excel
2. Edit the Excel file with your changes
3. Use ExcelToYamlMapCells.py to convert back to YAML
4. The output YAML maintains perfect compatibility with the original system

## Daily Report Tools

**Directory:** `DailyReportTools/`

A comprehensive Streamlit-based analytics dashboard for analyzing game data from CSV reports. The dashboard provides real-time insights into player statistics, resources, buildings, troops, items, and special protection status.

### Features

#### **Core Analytics**
- **Overview Tab**: Resource totals, daily growth rates, per-player averages, and attack protection analysis
- **Player Count**: Population trends and growth analysis
- **Resources**: Detailed resource tracking with historical trends
- **Power**: Player power distribution and rankings
- **Speedups**: Speedup item usage and availability

#### **Advanced Analytics**
- **Items**: Comprehensive item inventory analysis with enhanced tracking
- **Troops**: Troop composition and strength analysis
- **Buildings**: Building levels and construction analysis
- **Skins**: Player cosmetic items tracking
- **Quests & Research**: Quest completion and research progress analysis

#### **Attack Prevention Analysis** (New)
- **Comprehensive Detection**: Identifies all attack prevention effects (ceasefire, truce, armistice, etc.)
- **Resource Control**: Shows which players control protected resources
- **Player Rankings**: Power-sorted list of protected players
- **Resource Distribution**: Pie charts showing resource control among protected players
- **Protection Metrics**: Total protected resources and player percentages

### Key Features

#### **Smart Data Processing**
- **Multi-format Support**: Handles both legacy and comprehensive CSV formats
- **Automatic Detection**: Identifies and processes different report types automatically
- **Data Aggregation**: Combines data from multiple time periods for trend analysis
- **Error Handling**: Graceful handling of missing or corrupted data

#### **Visual Analytics**
- **Interactive Charts**: Plotly-powered visualizations with zoom and filtering
- **Resource Pie Charts**: Distribution analysis for major resources (excluding rubies)
- **Trend Analysis**: Historical data tracking with growth rates
- **Comparative Analysis**: Side-by-side comparisons of different metrics

#### **Attack Prevention Insights**
- **Effect Detection**: Finds all `prevent_attacks:1` effects regardless of source
- **Resource Protection**: Calculates protected vs unprotected resource amounts
- **Player Identification**: Lists all players under attack prevention
- **Strategic Analysis**: Shows resource control concentration among protected players

### Installation & Setup

1. **Install Dependencies:**
```bash
pip install streamlit pandas plotly openpyxl
```

2. **Navigate to Daily Report Tools:**
```bash
cd DailyReportTools
```

3. **Run the Dashboard:**
```bash
streamlit run dashboard.py
```

4. **Access the Dashboard:**
   - Open your browser to the provided URL (typically `http://localhost:8501`)
   - The dashboard will automatically load and process available CSV files

### Data Requirements

The dashboard expects CSV files in the `Daily Reports/` directory with the following formats:

#### **Legacy Format**: Basic player statistics
#### **Comprehensive Format**: Full player data including:
- `active_effects`: Player status effects (required for attack prevention analysis)
- `resource_*`: Resource amounts (gold, lumber, stone, metal, food, ruby)
- `power`: Player power levels
- `troop_*`: Troop compositions
- `item_*`: Item inventories
- `buildings_metadata`: Building information
- And many more fields...

### Dashboard Tabs Overview

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| **Overview** | Main metrics dashboard | Resource totals, growth rates, attack protection badges |
| **Player Count** | Population analysis | Growth trends, player statistics |
| **Resources** | Resource tracking | Historical trends, resource distribution |
| **Power** | Power analysis | Player rankings, power distribution |
| **Speedups** | Speedup items | Usage patterns, availability |
| **Items** | Item inventory | Comprehensive item tracking |
| **Troops** | Military analysis | Troop composition, strength metrics |
| **Buildings** | Construction analysis | Building levels, progression |
| **Skins** | Cosmetics tracking | Player customization items |
| **Quests & Research** | Progress tracking | Quest completion, research status |
| **Attack Prevention** | Protection analysis | Ceasefire, truce, armistice effects |

### Recent Updates

#### **Attack Prevention Enhancement**
- **Expanded Detection**: Now captures all attack prevention effects, not just specific types
- **Resource Analysis**: Detailed breakdown of protected resources by player
- **Visual Improvements**: Non-overlapping legends, better chart layouts
- **Data Integration**: Seamless integration with comprehensive CSV format

#### **UI/UX Improvements**
- **Clean Layout**: Removed debug output, streamlined interface
- **Better Organization**: Logical tab ordering and grouping
- **Responsive Design**: Optimized for different screen sizes
- **Error Handling**: Graceful degradation for missing data

### Troubleshooting

#### **Common Issues**
- **No Data Displayed**: Ensure CSV files are in `Daily Reports/` directory
- **Attack Prevention Tab Empty**: Verify CSV files contain `active_effects` column
- **Chart Overlap**: Refresh the page if legends overlap
- **Slow Loading**: Large CSV files may take time to process initially

#### **Data Format Issues**
- **Missing Columns**: Dashboard gracefully handles missing data fields
- **Format Changes**: Supports both old and new CSV formats
- **Encoding Issues**: Uses UTF-8 encoding for international characters
## Requirements

### YAML Parser Scripts
Most traditional scripts require the following Python packages:
- `yaml` - For parsing YAML files
- `pandas` - For data manipulation and Excel export
- `openpyxl` - For Excel file writing

### Daily Report Tools Dashboard
The Streamlit dashboard requires additional packages:
- `streamlit` - Web application framework
- `plotly` - Interactive visualizations
- `pandas` - Data processing (already listed above)

### Installation

#### For YAML Parsers Only:
```bash
pip install pyyaml pandas openpyxl
```

#### For Full Dashboard Experience:
```bash
pip install streamlit plotly pandas openpyxl pyyaml
```

## General Output Format

Excel-based parsers typically generate worksheets with the following structure:
- **Target Type**: The category or type being parsed
- **Target Level**: The level or tier within that type
- **Resource columns**: Various resource amounts or gains
- **Item columns**: Item probabilities or amounts
- **Other data columns**: Additional parsed information specific to each script

## Notes

- Scripts automatically discover all unique items and entities across the YAML data
- Missing data is typically filled with 0 values
- Column names are formatted for readability (underscores replaced with spaces, proper capitalization)
- Each script handles its specific YAML structure appropriately
