<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&duration=3500&pause=1200&color=58A6FF&center=true&vCenter=true&multiline=true&width=650&height=100&lines=Welcome+to+my+GitHub!;Data+science+%E2%80%A2+Last-mile+delivery)](https://github.com/prateekmishra118)

</div>

Datascience Work
# Last-Mile Delivery Dataset - Data Cleaning & Exploratory Data Analysis

## 📋 Overview

This repository contains a comprehensive dataset extracted from the LaDe (Last-Mile Delivery) dataset, focusing on pickup operations across five major Chinese cities. The dataset has been cleaned, processed, and analyzed to provide insights into delivery operations, customer distributions, and geographic patterns.

## 📊 Dataset Information

### Source
- **Original Dataset**: LaDe (Last-Mile Delivery Dataset)
- **Reference**: L. Wu, H. Wen, H. Hu, X. Mao, Y. Xia, E. Shan, J. Zhen, J. Lou, Y. Liang, L. Yang et al., "Lade: The first comprehensive last-mile delivery dataset from industry," arXiv preprint arXiv:2306.10675, 2023

### Cities Included
1. **Chongqing** - 1,470 customers (23.75%)
2. **Hangzhou** - 1,156 customers (18.68%)
3. **Jilin** - 767 customers (12.39%)
4. **Shanghai** - 1,285 customers (20.76%)
5. **Yantai** - 1,512 customers (24.43%)

**Total**: 6,190 customer records across 132 unique regions

### Data Extraction Details
- **Chongqing & Hangzhou**: Customer locations from May 1st
- **Jilin, Shanghai & Yantai**: Customer locations from June 7th
- Data refined using a greedy algorithm to remove redundant spatial information
- First three customer locations in each region designated as initial positions for truck-drone systems

## 📁 Project Structure

```
archive (1)/
│
├── README.md                          # This file
├── data_cleaning_combined.py           # Main data cleaning and analysis script
├── report_combined.txt                # Detailed analysis report
│
├── cleaned_combined_dataset.xlsx      # Cleaned dataset (main output)
├── combined_single_dataset.xlsx       # Combined dataset from all cities
├── combined_customer_information.xlsx # Combined customer data
├── combined_distance_matrices.xlsx    # Combined distance matrices
├── combined_adjacency_matrices.xlsx    # Combined precedence constraint matrices
│
├── plots/                             # Visualization directory
│   ├── 01_city_distribution.png
│   ├── 02_geographic_distribution.png
│   ├── 04_region_distribution.png
│   ├── 05_correlation_heatmap.png
│   ├── 06_courier_distribution.png
│   ├── 07_aoi_type_distribution.png
│   └── 08_boxplots_by_city.png
│
└── [city_name]/                       # Source data folders (5 cities)
    ├── customer_informatiton.xlsx
    ├── distance_matrices.xlsx
    └── adjacency_matrices.xlsx
```

## 🔧 Dataset Features

### Main Dataset Columns (21 columns)

| Column Name | Type | Description |
|------------|------|-------------|
| `order_id` | int64 | Unique order identifier |
| `region_id` | int64 | Region identifier (0-134) |
| `city` | object | City name |
| `courier_id` | int64 | Courier identifier |
| `accept_time` | datetime | Order acceptance timestamp |
| `time_window_start` | datetime | Service time window start |
| `time_window_end` | datetime | Service time window end |
| `lng` | float64 | Customer longitude |
| `lat` | float64 | Customer latitude |
| `aoi_id` | int64 | Area of Interest identifier |
| `aoi_type` | int64 | Type of area of interest (0-14) |
| `pickup_time` | datetime | Actual pickup timestamp |
| `pickup_gps_time` | datetime | GPS pickup timestamp |
| `pickup_gps_lng` | float64 | GPS pickup longitude |
| `pickup_gps_lat` | float64 | GPS pickup latitude |
| `accept_gps_time` | datetime | GPS acceptance timestamp |
| `accept_gps_lng` | float64 | GPS acceptance longitude |
| `accept_gps_lat` | float64 | GPS acceptance latitude |
| `ds` | int64 | Date identifier (501, 607) |
| `source_city` | object | Source city identifier |
| `time_window_duration` | float64 | Calculated time window duration (hours) |

## 🧹 Data Cleaning Process

### Steps Performed

1. **Duplicate Detection**
   - Checked for duplicate rows
   - Result: No duplicates found

2. **Missing Value Handling**
   - **GPS Pickup Data**: 1,734 missing values (28.01%)
     - Times filled with mode
     - Coordinates filled with median
   - **GPS Accept Data**: 2,681 missing values (43.31%)
     - Times filled with mode
     - Coordinates filled with median

3. **Data Type Conversions**
   - Converted 6 datetime columns to proper datetime format:
     - `accept_time`, `time_window_start`, `time_window_end`
     - `pickup_time`, `pickup_gps_time`, `accept_gps_time`

4. **Outlier Detection** (IQR Method)
   - **Longitude**: 2,237 outliers (36.14%)
   - **Pickup GPS Longitude**: 1,706 outliers (27.56%)
   - **Accept GPS Longitude**: 1,332 outliers (21.52%)
   - **Accept GPS Latitude**: 2,832 outliers (45.75%)

5. **Data Quality Validation**
   - Validated coordinate ranges (longitude: -180 to 180, latitude: -90 to 90)
   - Validated time window consistency (end > start)
   - All validations passed

## 📈 Key Statistics

### Geographic Coverage
- **Longitude Range**: 105.91° to 127.35° E
- **Latitude Range**: 28.94° to 44.43° N
- **Longitude Std Dev**: 6.61°
- **Latitude Std Dev**: 4.82°

### Operational Metrics
- **Total Regions**: 132 unique regions
- **Average Customers per Region**: 46.89
- **Median Customers per Region**: 49.00
- **Total Couriers**: 1,217 unique couriers
- **Average Orders per Courier**: 5.09
- **Median Orders per Courier**: 3.00
- **Max Orders per Courier**: 49

### AOI Type Distribution
- **Type 1**: 2,879 occurrences (46.5%)
- **Type 14**: 2,557 occurrences (41.3%)
- **Type 0**: 173 occurrences (2.8%)
- **Other types**: 581 occurrences (9.4%)

## 📊 Visualizations

The `plots/` directory contains 7 high-resolution visualizations (300 DPI):

1. **City Distribution** - Bar chart showing customer distribution across cities
2. **Geographic Distribution** - Scatter plot of customer locations by city
3. **Region Distribution** - Top 20 regions by customer count
4. **Correlation Heatmap** - Correlation matrix of key numeric variables
5. **Courier Distribution** - Top 20 couriers by order count
6. **AOI Type Distribution** - Frequency distribution of Area of Interest types
7. **Box Plots by City** - Comparative box plots for key variables across cities

## 🚀 Usage

### Running the Data Cleaning Script

```bash
python data_cleaning_combined.py
```

### Requirements

```python
pandas >= 1.3.0
numpy >= 1.21.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
openpyxl >= 3.0.0
```

### Output Files

The script generates:
1. **cleaned_combined_dataset.xlsx** - Cleaned dataset with summary sheet
2. **plots/** - Directory containing all visualizations
3. **report_combined.txt** - Comprehensive text report

## 📋 Matrix Files

### Distance Matrices
- **File**: `combined_distance_matrices.xlsx`
- **Content**: Pairwise distances between customers (in meters)
- **Naming Convention**: `[city]_[region_id]_[num_customers]`
- **Purpose**: Spatial relationship information for routing optimization

### Adjacency Matrices (Precedence Constraints)
- **File**: `combined_adjacency_matrices.xlsx`
- **Content**: Precedence constraint matrix based on time window end times
- **Naming Convention**: `[city]_[region_id]_[num_customers]`
- **Purpose**: Defines service order constraints (if element [x,y] = 1, customer x must be served before customer y)

## 🔍 Data Quality Notes

### Missing Data
- GPS tracking data has significant missing values (28-43%)
- Missing values were imputed using statistical methods (median/mode)
- Consider this when performing GPS-based analyses

### Outliers
- Geographic coordinates show natural clustering by city
- Outliers detected are likely valid data points representing different city locations
- No outliers were removed as they represent legitimate geographic diversity

### Time Windows
- Time window duration calculation may show NaN values if datetime conversion fails
- This is expected for some records with incomplete time data

## 📝 Notes

- The dataset is extracted from the "pickup" section of the LaDe dataset
- Initial positions for truck-drone systems are the first three customer locations in each region
- Sheet naming in matrix files follows: `region_id_number_of_customers`
- All visualizations are saved as PNG files at 300 DPI for publication quality

## 📄 License & Citation

If you use this dataset, please cite the original LaDe paper:

```
L. Wu, H. Wen, H. Hu, X. Mao, Y. Xia, E. Shan, J. Zhen, J. Lou, 
Y. Liang, L. Yang et al., "Lade: The first comprehensive last-mile 
delivery dataset from industry," arXiv preprint arXiv:2306.10675, 2023
```

## 🤝 Contributing

This is a processed and cleaned version of the LaDe dataset. For the original dataset, please refer to the LaDe project.

## 📧 Contact

For questions about the original dataset, please refer to the LaDe paper authors.

---

**Last Updated**: December 2024  
**Dataset Version**: 1.0  
**Total Records**: 6,190  
**Cities**: 5  
**Regions**: 132

#
