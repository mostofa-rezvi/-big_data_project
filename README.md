# Rainfall, Food Prices, and External Debt in Bangladesh: Predictive and Clustering Analysis

## Project Overview

End-to-end big data pipeline analyzing the causal chain: **Rainfall → Food Prices → External Debt** in Bangladesh using PySpark and machine learning.

**Research Questions:**
1. Does rainfall predict food prices?
2. Do food prices drive external debt?
3. Can years/divisions be grouped by risk level (K-Means clustering)?

**Scope:** 1999–2024 | 8 Bangladeshi divisions (adm_level=1) | ~2,496 rows (26 years × 12 months × 8 divisions)


## Installation & Setup (Ubuntu + Jupyter + PySpark)

### Prerequisites
- **Ubuntu 20.04+** (tested on 24.04)
- **Python 3.8+** installed
- **Java 8+** (required for PySpark)
- **pip** (Python package manager)

### System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Java (required for PySpark)
sudo apt install -y default-jdk

# Verify Java installation
java -version

# Install system dev tools (optional but recommended)
sudo apt install -y build-essential python3-dev
```

### Install Dependencies

```bash
pip install pyspark==3.5.8
pip install pandas==2.0.3
pip install numpy==1.24.3
pip install matplotlib==3.7.1
pip install seaborn==0.12.2
pip install scikit-learn==1.3.0
pip install jupyter==1.0.0
pip install ipywidgets==8.1.0
```

### Enable Jupyter Widgets (for interactive demo)

```bash
# Enable ipywidgets extension for local Jupyter
jupyter nbextension enable --py widgetsnbextension

```

### Step 4: Verify Installations

```bash
# Check Python version
python3 --version

# Check PySpark installation
python3 -c "import pyspark; print(f'PySpark {pyspark.__version__}')"

# Check Jupyter installation
jupyter --version

# Verify Java for Spark
java -version
```


## Running the Project

### Jupyter Notebook

```bash
# Start Jupyter Notebook server
python3 -m notebook

# Open browser clicking the url (url will contain token)
# Locate the BigDataProject.ipynb
```


## Data Files
**Put the all .csv files in the same directory as .ipnyb:**
| File | Source | Rows | Columns | Notes |
|---|---|---|---|---|
| `bgdrainfallsubnatfull.csv` | FEWS NET/CHIRPS | 120K+ | 15 | Daily decadal rainfall, subnational |
| `wfp_food_prices_bgd.csv` | WFP VAM | 19K+ | 16 | Market-level price observations |
| `externaldebt_bgd.csv` | World Bank IDS | 2.6K | 6 | Annual national debt indicators |

**Notebook will auto-load from working directory:**
```python
rf = spark.read.csv('bgdrainfallsubnatfull.csv', header=True, inferSchema=True)
fp = spark.read.csv('wfp_food_prices_bgd.csv', header=True, inferSchema=True)
dbt = spark.read.csv('externaldebt_bgd.csv', header=True, inferSchema=True)
```


## Pipeline Steps

1. **Load Raw Data** → Spark DataFrames
2. **Data Cleaning** → Filter divisions, date parsing, unit normalization
3. **Merge on Grid** → Full 8 div × 26 year × 12 month grid
4. **Interpolation** → Window functions (zero nulls before ML)
5. **EDA** → Correlation heatmap, time series plots
6. **Supervised ML** → Rainfall → Food Prices (LR, DT, RF)
7. **Supervised ML** → Food Prices → Debt (LR, DT, RF)
8. **Unsupervised ML** → K-Means clustering (k=4, elbow method)
9. **Interactive Demo** → ipywidgets UI (price/debt/risk prediction)
10. **Export Results** → merged_bgd_dataset.csv, model summaries


## Project Outcomes

- **Mediation Chain:** Climate doesn't directly drive debt; rainfall influences rice prices (R² ≈ 0.15), while external debt is strongly tied to food prices (R² ≈ 0.75–0.77), with imported oil as the top predictor.
- **Risk Classification:** A 4-tier K-Means model flagged every division in Bangladesh as "Severe Risk" by 2024.
- **Methodological Win:** Fixed a major data leakage bug, ensuring robust machine learning results.
- **Key Caveat:** Findings show correlations, not strict causality, due to limited debt data (26 years, 2,496 rows) and early 2000s interpolation.
- **Core Insight:** Bangladesh's debt crisis is highly sensitive to food prices—especially imported oil—rather than localized climate shocks.

