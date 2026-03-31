import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import sys
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Get the workspace directory dynamically
base_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
os.chdir(base_dir)

print("=" * 80)
print("COMPREHENSIVE DATA CLEANING AND EXPLORATORY DATA ANALYSIS")
print("=" * 80)
print(f"Working Directory: {base_dir}")
print()

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("1. Loading data...")
print("-" * 80)
try:
    df = pd.read_excel('combined_single_dataset.xlsx', sheet_name='Customer_Information')
    print(f"   [OK] Loaded {len(df):,} records with {len(df.columns)} columns")
    print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
except Exception as e:
    print(f"   [ERROR] Error loading data: {e}")
    exit(1)
print()

# ============================================================================
# 2. INITIAL DATA EXPLORATION
# ============================================================================
print("2. Initial Data Exploration")
print("-" * 80)
print(f"Dataset shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"\nColumn names and types:")
for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
    print(f"  {i:2d}. {col:25s} ({dtype})")

print(f"\nMissing values summary:")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing Percentage': missing_pct
})
missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
if len(missing_df) > 0:
    print(missing_df.to_string())
    print(f"\n   Total missing values: {missing.sum():,}")
    print(f"   Columns with missing values: {len(missing_df)}/{len(df.columns)}")
else:
    print("   [OK] No missing values found!")
print()

# ============================================================================
# 3. DATA CLEANING
# ============================================================================
print("3. Data Cleaning")
print("-" * 80)

# Create a copy for cleaning
df_clean = df.copy()
initial_rows = len(df_clean)
initial_cols = len(df_clean.columns)

# 3.1 Check for duplicates
duplicates = df_clean.duplicated().sum()
print(f"3.1 Duplicate rows: {duplicates:,}")
if duplicates > 0:
    df_clean = df_clean.drop_duplicates()
    print(f"   [OK] Removed {duplicates:,} duplicate rows")
else:
    print("   [OK] No duplicate rows found")

# 3.2 Handle missing values
print(f"\n3.2 Handling missing values:")
missing_handled = {}
for col in df_clean.columns:
    missing_count = df_clean[col].isnull().sum()
    if missing_count > 0:
        pct = (missing_count / len(df_clean) * 100)
        print(f"   {col}: {missing_count:,} ({pct:.2f}%)")
        
        # For numeric columns, fill with median
        if df_clean[col].dtype in ['int64', 'float64']:
            median_val = df_clean[col].median()
            if pd.notna(median_val):
                df_clean[col].fillna(median_val, inplace=True)
                missing_handled[col] = f"median ({median_val:.2f})"
                print(f"      → Filled with median: {median_val:.2f}")
            else:
                df_clean[col].fillna(0, inplace=True)
                missing_handled[col] = "0"
                print(f"      → Filled with 0")
        # For object columns, fill with mode or 'Unknown'
        elif df_clean[col].dtype == 'object':
            mode_val = df_clean[col].mode()[0] if len(df_clean[col].mode()) > 0 else 'Unknown'
            df_clean[col].fillna(mode_val, inplace=True)
            missing_handled[col] = f"mode ({mode_val})"
            print(f"      → Filled with mode: {mode_val}")

if not missing_handled:
    print("   [OK] No missing values to handle")

# 3.3 Data type conversions
print(f"\n3.3 Data type conversions:")
date_cols = ['accept_time', 'time_window_start', 'time_window_end', 
             'pickup_time', 'pickup_gps_time', 'accept_gps_time']
converted_cols = []
for col in date_cols:
    if col in df_clean.columns:
        try:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            converted_cols.append(col)
            print(f"   [OK] {col} -> datetime")
        except Exception as e:
            print(f"   [ERROR] {col} -> conversion failed: {e}")

# 3.4 Outlier detection for numeric columns
print(f"\n3.4 Outlier detection (using IQR method):")
numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
outliers_summary = {}
for col in numeric_cols:
    if df_clean[col].notna().sum() > 0:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR > 0:
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
            if outliers > 0:
                outliers_summary[col] = {
                    'count': outliers,
                    'percentage': outliers/len(df_clean)*100,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
                print(f"   {col}: {outliers:,} outliers ({outliers/len(df_clean)*100:.2f}%)")

if not outliers_summary:
    print("   [OK] No significant outliers detected")

# 3.5 Data quality checks
print(f"\n3.5 Data quality checks:")
# Check for invalid coordinates
if 'lng' in df_clean.columns and 'lat' in df_clean.columns:
    invalid_coords = ((df_clean['lng'] < -180) | (df_clean['lng'] > 180) | 
                     (df_clean['lat'] < -90) | (df_clean['lat'] > 90)).sum()
    if invalid_coords > 0:
        print(f"   [WARNING] Invalid coordinates found: {invalid_coords}")
        df_clean = df_clean[~((df_clean['lng'] < -180) | (df_clean['lng'] > 180) | 
                             (df_clean['lat'] < -90) | (df_clean['lat'] > 90))]
        print(f"   [OK] Removed {invalid_coords} rows with invalid coordinates")
    else:
        print("   [OK] All coordinates are valid")

# Check time window consistency
if 'time_window_start' in df_clean.columns and 'time_window_end' in df_clean.columns:
    invalid_windows = (df_clean['time_window_end'] < df_clean['time_window_start']).sum()
    if invalid_windows > 0:
        print(f"   [WARNING] Invalid time windows found: {invalid_windows}")
    else:
        print("   [OK] All time windows are valid")

print(f"\n   Summary:")
print(f"   Rows before cleaning: {initial_rows:,}")
print(f"   Rows after cleaning: {len(df_clean):,}")
print(f"   Rows removed: {initial_rows - len(df_clean):,}")
print()

# ============================================================================
# 4. EXPLORATORY DATA ANALYSIS
# ============================================================================
print("4. Exploratory Data Analysis")
print("-" * 80)

# 4.1 Summary Statistics
print("4.1 Summary Statistics for Numeric Columns:")
numeric_cols_clean = df_clean.select_dtypes(include=[np.number]).columns.tolist()
if numeric_cols_clean:
    print(df_clean[numeric_cols_clean].describe().round(2))
print()

# 4.2 City-wise Analysis
if 'source_city' in df_clean.columns:
    print("4.2 City-wise Distribution:")
    city_counts = df_clean['source_city'].value_counts()
    print(city_counts.to_string())
    print(f"\n   City percentages:")
    for city, count in city_counts.items():
        print(f"   {city:15s}: {count:6,} ({count/len(df_clean)*100:5.2f}%)")
    print()

# 4.3 Region Analysis
if 'region_id' in df_clean.columns:
    print("4.3 Region Analysis:")
    print(f"   Total unique regions: {df_clean['region_id'].nunique()}")
    region_counts = df_clean['region_id'].value_counts()
    print(f"   Average customers per region: {region_counts.mean():.2f}")
    print(f"   Median customers per region: {region_counts.median():.2f}")
    print(f"\n   Top 10 regions by customer count:")
    print(region_counts.head(10).to_string())
    print()

# 4.4 Geographic Analysis
if 'lng' in df_clean.columns and 'lat' in df_clean.columns:
    print("4.4 Geographic Analysis:")
    print(f"   Longitude range: {df_clean['lng'].min():.6f} to {df_clean['lng'].max():.6f}")
    print(f"   Latitude range: {df_clean['lat'].min():.6f} to {df_clean['lat'].max():.6f}")
    print(f"   Longitude std: {df_clean['lng'].std():.6f}")
    print(f"   Latitude std: {df_clean['lat'].std():.6f}")
    print()

# 4.5 Time Window Analysis
if 'time_window_start' in df_clean.columns and 'time_window_end' in df_clean.columns:
    print("4.5 Time Window Analysis:")
    df_clean['time_window_duration'] = (
        df_clean['time_window_end'] - df_clean['time_window_start']
    ).dt.total_seconds() / 3600
    print(f"   Average time window duration: {df_clean['time_window_duration'].mean():.2f} hours")
    print(f"   Median time window duration: {df_clean['time_window_duration'].median():.2f} hours")
    print(f"   Min time window duration: {df_clean['time_window_duration'].min():.2f} hours")
    print(f"   Max time window duration: {df_clean['time_window_duration'].max():.2f} hours")
    print(f"   Std time window duration: {df_clean['time_window_duration'].std():.2f} hours")
    print()

# 4.6 Courier Analysis
if 'courier_id' in df_clean.columns:
    print("4.6 Courier Analysis:")
    print(f"   Total unique couriers: {df_clean['courier_id'].nunique()}")
    courier_counts = df_clean['courier_id'].value_counts()
    print(f"   Average orders per courier: {courier_counts.mean():.2f}")
    print(f"   Median orders per courier: {courier_counts.median():.2f}")
    print(f"   Max orders per courier: {courier_counts.max()}")
    print()

# 4.7 AOI (Area of Interest) Analysis
if 'aoi_type' in df_clean.columns:
    print("4.7 AOI Type Analysis:")
    aoi_counts = df_clean['aoi_type'].value_counts()
    print(aoi_counts.to_string())
    print()

# ============================================================================
# 5. SAVE CLEANED DATASET
# ============================================================================
print("5. Saving cleaned dataset...")
print("-" * 80)
try:
    output_file = base_dir / 'cleaned_combined_dataset.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_clean.to_excel(writer, sheet_name='CleanedData', index=False)
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Records', 'Total Columns', 'Duplicate Rows Removed', 
                       'Rows Removed', 'Date Columns Converted', 'Outliers Detected'],
            'Value': [len(df_clean), len(df_clean.columns), duplicates,
                     initial_rows - len(df_clean), len(converted_cols), len(outliers_summary)]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='CleaningSummary', index=False)
    print(f"   [OK] Saved to: {output_file.name}")
except Exception as e:
    print(f"   [ERROR] Error saving: {e}")
print()

# ============================================================================
# 6. CREATE VISUALIZATIONS
# ============================================================================
print("6. Creating visualizations...")
print("-" * 80)

# Create output directory for plots
plots_dir = base_dir / 'eda_plots'
plots_dir.mkdir(exist_ok=True)

plot_count = 0

try:
    # 6.1 City Distribution
    if 'source_city' in df_clean.columns:
        plt.figure(figsize=(12, 7))
        city_counts = df_clean['source_city'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(city_counts)))
        bars = plt.bar(city_counts.index, city_counts.values, color=colors, edgecolor='black', linewidth=1.2)
        plt.title('Customer Distribution by City', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('City', fontsize=13, fontweight='bold')
        plt.ylabel('Number of Customers', fontsize=13, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(plots_dir / '01_city_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        plot_count += 1
        print(f"   [OK] City distribution plot saved")

    # 6.2 Geographic Scatter Plot
    if 'lng' in df_clean.columns and 'lat' in df_clean.columns and 'source_city' in df_clean.columns:
        plt.figure(figsize=(16, 10))
        cities = df_clean['source_city'].unique()
        colors_map = plt.cm.tab10(np.linspace(0, 1, len(cities)))
        
        for idx, city in enumerate(cities):
            city_data = df_clean[df_clean['source_city'] == city]
            # Sample if too many points for better visualization
            if len(city_data) > 5000:
                city_data = city_data.sample(n=5000, random_state=42)
            plt.scatter(city_data['lng'], city_data['lat'], 
                       label=f'{city} (n={len(city_data):,})', 
                       alpha=0.5, s=15, color=colors_map[idx])
        
        plt.xlabel('Longitude', fontsize=13, fontweight='bold')
        plt.ylabel('Latitude', fontsize=13, fontweight='bold')
        plt.title('Geographic Distribution of Customers by City', fontsize=16, fontweight='bold', pad=20)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(plots_dir / '02_geographic_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        plot_count += 1
        print(f"   [OK] Geographic distribution plot saved")

    # 6.3 Time Window Duration Distribution
    if 'time_window_duration' in df_clean.columns:
        plt.figure(figsize=(12, 7))
        duration_data = df_clean['time_window_duration'].dropna()
        if len(duration_data) > 0:
            plt.hist(duration_data, bins=50, color='coral', edgecolor='black', alpha=0.7)
            plt.xlabel('Time Window Duration (hours)', fontsize=13, fontweight='bold')
            plt.ylabel('Frequency', fontsize=13, fontweight='bold')
            plt.title('Distribution of Time Window Durations', fontsize=16, fontweight='bold', pad=20)
            mean_val = duration_data.mean()
            median_val = duration_data.median()
            plt.axvline(mean_val, color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {mean_val:.2f} hrs')
            plt.axvline(median_val, color='blue', linestyle='--', linewidth=2,
                       label=f'Median: {median_val:.2f} hrs')
            plt.legend(fontsize=11)
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            plt.savefig(plots_dir / '03_time_window_duration.png', dpi=300, bbox_inches='tight')
            plt.close()
            plot_count += 1
            print(f"   [OK] Time window duration plot saved")

    # 6.4 Region Distribution (Top 20)
    if 'region_id' in df_clean.columns:
        plt.figure(figsize=(16, 8))
        region_counts = df_clean['region_id'].value_counts().head(20)
        bars = plt.bar(range(len(region_counts)), region_counts.values, 
                      color='teal', edgecolor='black', linewidth=1.2)
        plt.xlabel('Region ID', fontsize=13, fontweight='bold')
        plt.ylabel('Number of Customers', fontsize=13, fontweight='bold')
        plt.title('Top 20 Regions by Customer Count', fontsize=16, fontweight='bold', pad=20)
        plt.xticks(range(len(region_counts)), region_counts.index, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(plots_dir / '04_region_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        plot_count += 1
        print(f"   [OK] Region distribution plot saved")

    # 6.5 Correlation Heatmap
    if len(numeric_cols_clean) > 1:
        # Select key numeric columns
        key_numeric = [col for col in numeric_cols_clean 
                      if col in ['lng', 'lat', 'region_id', 'time_window_duration', 
                                'courier_id', 'aoi_id', 'aoi_type', 'pickup_gps_lng', 
                                'pickup_gps_lat', 'accept_gps_lng', 'accept_gps_lat']]
        if len(key_numeric) > 1:
            plt.figure(figsize=(14, 12))
            corr_matrix = df_clean[key_numeric].corr()
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, linewidths=1, cbar_kws={"shrink": 0.8}, mask=mask,
                       annot_kws={'size': 9})
            plt.title('Correlation Matrix of Key Numeric Variables', fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            plt.savefig(plots_dir / '05_correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
            plot_count += 1
            print(f"   [OK] Correlation heatmap saved")

    # 6.6 Courier Distribution (Top 20)
    if 'courier_id' in df_clean.columns:
        plt.figure(figsize=(16, 8))
        courier_counts = df_clean['courier_id'].value_counts().head(20)
        bars = plt.bar(range(len(courier_counts)), courier_counts.values,
                      color='purple', edgecolor='black', linewidth=1.2)
        plt.xlabel('Courier ID', fontsize=13, fontweight='bold')
        plt.ylabel('Number of Orders', fontsize=13, fontweight='bold')
        plt.title('Top 20 Couriers by Order Count', fontsize=16, fontweight='bold', pad=20)
        plt.xticks(range(len(courier_counts)), courier_counts.index, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(plots_dir / '06_courier_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        plot_count += 1
        print(f"   [OK] Courier distribution plot saved")

    # 6.7 AOI Type Distribution
    if 'aoi_type' in df_clean.columns:
        plt.figure(figsize=(12, 7))
        aoi_counts = df_clean['aoi_type'].value_counts().sort_index()
        bars = plt.bar(aoi_counts.index.astype(str), aoi_counts.values,
                      color='orange', edgecolor='black', linewidth=1.2)
        plt.xlabel('AOI Type', fontsize=13, fontweight='bold')
        plt.ylabel('Frequency', fontsize=13, fontweight='bold')
        plt.title('Distribution of AOI Types', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(plots_dir / '07_aoi_type_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        plot_count += 1
        print(f"   [OK] AOI type distribution plot saved")

    # 6.8 Box plots for numeric variables by city
    if 'source_city' in df_clean.columns and len(numeric_cols_clean) > 0:
        key_vars = [col for col in ['time_window_duration', 'lng', 'lat'] 
                   if col in numeric_cols_clean]
        if key_vars:
            fig, axes = plt.subplots(1, len(key_vars), figsize=(6*len(key_vars), 8))
            if len(key_vars) == 1:
                axes = [axes]
            
            for idx, var in enumerate(key_vars):
                data_to_plot = [df_clean[df_clean['source_city'] == city][var].dropna() 
                               for city in df_clean['source_city'].unique()]
                bp = axes[idx].boxplot(data_to_plot, labels=df_clean['source_city'].unique(),
                                       patch_artist=True)
                axes[idx].set_title(f'{var.replace("_", " ").title()} by City', 
                                   fontsize=14, fontweight='bold')
                axes[idx].set_ylabel(var.replace("_", " ").title(), fontsize=12)
                axes[idx].set_xlabel('City', fontsize=12)
                axes[idx].tick_params(axis='x', rotation=45)
                axes[idx].grid(axis='y', alpha=0.3, linestyle='--')
                
                # Color the boxes
                colors = plt.cm.Pastel1(np.linspace(0, 1, len(bp['boxes'])))
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
            
            plt.tight_layout()
            plt.savefig(plots_dir / '08_boxplots_by_city.png', dpi=300, bbox_inches='tight')
            plt.close()
            plot_count += 1
            print(f"   [OK] Box plots by city saved")

except Exception as e:
    print(f"   [ERROR] Error creating visualizations: {e}")
    import traceback
    traceback.print_exc()

print(f"\n   Total plots created: {plot_count}")
print()

# ============================================================================
# 7. GENERATE EDA REPORT
# ============================================================================
print("7. Generating EDA Report...")
print("-" * 80)
try:
    report_file = base_dir / 'EDA_Report_Combined.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPREHENSIVE EXPLORATORY DATA ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("DATASET OVERVIEW\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Records: {len(df_clean):,}\n")
        f.write(f"Total Columns: {len(df_clean.columns)}\n")
        if 'accept_time' in df_clean.columns:
            f.write(f"Date Range: {df_clean['accept_time'].min()} to {df_clean['accept_time'].max()}\n")
        f.write("\n")
        
        f.write("DATA CLEANING SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Initial Records: {initial_rows:,}\n")
        f.write(f"Final Records: {len(df_clean):,}\n")
        f.write(f"Records Removed: {initial_rows - len(df_clean):,}\n")
        f.write(f"Duplicate Rows Removed: {duplicates:,}\n")
        f.write(f"Date Columns Converted: {len(converted_cols)}\n")
        f.write(f"  - {', '.join(converted_cols)}\n\n")
        
        f.write("MISSING VALUES HANDLING\n")
        f.write("-" * 80 + "\n")
        if missing_handled:
            for col, method in missing_handled.items():
                f.write(f"{col}: Filled with {method}\n")
        else:
            f.write("No missing values found after cleaning.\n")
        f.write("\n")
        
        f.write("OUTLIERS DETECTED\n")
        f.write("-" * 80 + "\n")
        if outliers_summary:
            for col, info in outliers_summary.items():
                f.write(f"{col}:\n")
                f.write(f"  Count: {info['count']:,} ({info['percentage']:.2f}%)\n")
                f.write(f"  Lower bound: {info['lower_bound']:.2f}\n")
                f.write(f"  Upper bound: {info['upper_bound']:.2f}\n\n")
        else:
            f.write("No significant outliers detected.\n\n")
        
        f.write("CITY-WISE DISTRIBUTION\n")
        f.write("-" * 80 + "\n")
        if 'source_city' in df_clean.columns:
            city_counts = df_clean['source_city'].value_counts()
            for city, count in city_counts.items():
                f.write(f"{city:15s}: {count:6,} ({count/len(df_clean)*100:5.2f}%)\n")
        f.write("\n")
        
        f.write("REGION ANALYSIS\n")
        f.write("-" * 80 + "\n")
        if 'region_id' in df_clean.columns:
            f.write(f"Total unique regions: {df_clean['region_id'].nunique()}\n")
            region_counts = df_clean['region_id'].value_counts()
            f.write(f"Average customers per region: {region_counts.mean():.2f}\n")
            f.write(f"Median customers per region: {region_counts.median():.2f}\n")
            f.write(f"Top 10 regions:\n")
            for region, count in region_counts.head(10).items():
                f.write(f"  Region {region}: {count:,} customers\n")
        f.write("\n")
        
        f.write("GEOGRAPHIC ANALYSIS\n")
        f.write("-" * 80 + "\n")
        if 'lng' in df_clean.columns and 'lat' in df_clean.columns:
            f.write(f"Longitude range: {df_clean['lng'].min():.6f} to {df_clean['lng'].max():.6f}\n")
            f.write(f"Latitude range: {df_clean['lat'].min():.6f} to {df_clean['lat'].max():.6f}\n")
            f.write(f"Longitude std: {df_clean['lng'].std():.6f}\n")
            f.write(f"Latitude std: {df_clean['lat'].std():.6f}\n")
        f.write("\n")
        
        f.write("TIME WINDOW ANALYSIS\n")
        f.write("-" * 80 + "\n")
        if 'time_window_duration' in df_clean.columns:
            f.write(f"Average duration: {df_clean['time_window_duration'].mean():.2f} hours\n")
            f.write(f"Median duration: {df_clean['time_window_duration'].median():.2f} hours\n")
            f.write(f"Min duration: {df_clean['time_window_duration'].min():.2f} hours\n")
            f.write(f"Max duration: {df_clean['time_window_duration'].max():.2f} hours\n")
            f.write(f"Std duration: {df_clean['time_window_duration'].std():.2f} hours\n")
        f.write("\n")
        
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(df_clean[numeric_cols_clean].describe().to_string())
        f.write("\n\n")
        
        f.write("COLUMN INFORMATION\n")
        f.write("-" * 80 + "\n")
        for col in df_clean.columns:
            f.write(f"{col:25s}: {df_clean[col].dtype}\n")
    
    print(f"   [OK] Report saved to: {report_file.name}")
except Exception as e:
    print(f"   [ERROR] Error generating report: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("DATA CLEANING AND EDA COMPLETE!")
print("=" * 80)
print(f"\nOutputs created:")
print(f"  1. cleaned_combined_dataset.xlsx - Cleaned dataset with summary sheet")
print(f"  2. eda_plots/ - Directory with {plot_count} visualization plots")
print(f"  3. EDA_Report_Combined.txt - Comprehensive analysis report")
print()
print("=" * 80)

