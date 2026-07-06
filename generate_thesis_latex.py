import sys
import io
import re

# Force standard output to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read docx dump
with open(r'd:\github\-big_data_project\raw_docx_dump.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

paragraphs = []
current_para = None
mode = 'paras'
tables = {}
current_table_idx = None
current_table_rows = []
current_row_idx = None
current_cell_idx = None
current_cell_lines = []

for line in lines:
    line_stripped = line.strip()
    if line_stripped == '=== PARAGRAPHS ===':
        mode = 'paras'
        continue
    elif line_stripped == '=== TABLES ===':
        mode = 'tables'
        continue
    
    if mode == 'paras':
        m_para_start = re.match(r'^PARAGRAPH (\d+) \(Style: ([^\)]+)\):', line_stripped)
        if m_para_start:
            if current_para is not None:
                paragraphs.append(current_para)
            current_para = {
                'idx': int(m_para_start.group(1)),
                'style': m_para_start.group(2),
                'text_lines': []
            }
        else:
            if current_para is not None:
                current_para['text_lines'].append(line)
    elif mode == 'tables':
        m_table_start = re.match(r'^TABLE (\d+) \(Rows: (\d+), Cols: (\d+)\):', line_stripped)
        if m_table_start:
            if current_table_idx is not None:
                tables[current_table_idx] = current_table_rows
            current_table_idx = int(m_table_start.group(1))
            current_table_rows = []
            current_row_idx = None
            current_cell_idx = None
        else:
            m_row_start = re.match(r'^  Row (\d+):', line_stripped)
            if m_row_start:
                if current_row_idx is not None:
                    # Save last cell
                    if current_cell_idx is not None and 'current_row_cells' in locals():
                        current_row_cells[current_cell_idx] = '\n'.join(current_cell_lines).strip()
                    if 'current_row_cells' in locals():
                        current_table_rows.append(current_row_cells)
                current_row_idx = int(m_row_start.group(1))
                current_row_cells = {}
                current_cell_idx = None
            else:
                m_cell_start = re.match(r'^    Cell (\d+):', line_stripped)
                if m_cell_start:
                    if current_cell_idx is not None:
                        current_row_cells[current_cell_idx] = '\n'.join(current_cell_lines).strip()
                    current_cell_idx = int(m_cell_start.group(1))
                    current_cell_lines = []
                else:
                    if current_cell_idx is not None:
                        current_cell_lines.append(line)

# Save final paragraph and table
if current_para is not None:
    paragraphs.append(current_para)
if current_table_idx is not None:
    if current_cell_idx is not None and 'current_row_cells' in locals():
        current_row_cells[current_cell_idx] = '\n'.join(current_cell_lines).strip()
    if 'current_row_cells' in locals():
        current_table_rows.append(current_row_cells)
    tables[current_table_idx] = current_table_rows

# Clean paragraph text
for p in paragraphs:
    p['text'] = ''.join(p['text_lines']).strip()

print(f'Parsed {len(paragraphs)} paragraphs and {len(tables)} tables.')

# Let's inspect the paragraphs in more detail to map them to LaTeX sections
# We will construct a clean list of document elements: either heading, paragraph, list, code_block, table_placeholder, figure_placeholder
doc_elements = []

# Hand-crafted mappings for headings
headings_map = {
    '1. INTRODUCTION': ('section', 'Introduction'),
    '2. LITERATURE REVIEW': ('section', 'Literature Review'),
    '3. DATA AND METHODOLOGY': ('section', 'Data and Methodology'),
    '3.1 Data Sources & Preprocessing': ('subsection', 'Data Sources \\& Preprocessing'),
    'Rainfall Data Processing': ('subsubsection', 'Rainfall Data Processing'),
    'Food Price Data Processing': ('subsubsection', 'Food Price Data Processing'),
    'External Debt Data Processing': ('subsubsection', 'External Debt Data Processing'),
    'Merging and the Full Grid Approach': ('subsubsection', 'Merging and the Full Grid Approach'),
    'Interpolation Strategy': ('subsubsection', 'Interpolation Strategy'),
    'Final Dataset': ('subsubsection', 'Final Dataset'),
    '3.2 Exploratory Data Analysis': ('subsection', 'Exploratory Data Analysis'),
    '3.3 Supervised Learning Methodology': ('subsection', 'Supervised Learning Methodology'),
    'Task A, Rainfall → Food Prices': ('subsubsection', 'Task A: Rainfall $\\rightarrow$ Food Prices'),
    'Task B, Food Prices → External Debt': ('subsubsection', 'Task B: Food Prices $\\rightarrow$ External Debt'),
    '3.4 Unsupervised Learning Methodology': ('subsection', 'Unsupervised Learning Methodology'),
    '3.5 Evaluation Metrics': ('subsection', 'Evaluation Metrics'),
    '4. IMPLEMENTATION': ('section', 'Implementation'),
    '4.1 Data Loading & Processing': ('subsection', 'Data Loading \\& Processing'),
    'Environment': ('subsubsection', 'Environment'),
    'Schema Inspection': ('subsubsection', 'Schema Inspection'),
    'Rainfall Processing': ('subsubsection', 'Rainfall Processing'),
    'Food Price Processing': ('subsubsection', 'Food Price Processing'),
    'Debt Processing and Broadcasting': ('subsubsection', 'Debt Processing and Broadcasting'),
    'Full Grid Merge and Pre-Interpolation Null Check': ('subsubsection', 'Full Grid Merge and Pre-Interpolation Null Check'),
    'Interpolation Execution and Verification': ('subsubsection', 'Interpolation Execution and Verification'),
    'Problems Encountered and Fixes': ('subsubsection', 'Problems Encountered and Fixes'),
    '4.2 EDA Visualizations': ('subsection', 'EDA Visualizations'),
    '4.3 Supervised & Unsupervised Model Implementation': ('subsection', 'Supervised \\& Unsupervised Model Implementation'),
    'Supervised Pipeline, Rainfall → Food Prices': ('subsubsection', 'Supervised Pipeline: Rainfall $\\rightarrow$ Food Prices'),
    'Supervised Pipeline, Food Prices → Debt': ('subsubsection', 'Supervised Pipeline: Food Prices $\\rightarrow$ Debt'),
    'Unsupervised Pipeline, K-Means Risk Clustering': ('subsubsection', 'Unsupervised Pipeline: K-Means Risk Clustering'),
    '4.4 Interactive Demo': ('subsection', 'Interactive Demo'),
    '5. RESULTS AND ANALYSIS': ('section', 'Results and Analysis'),
    '5.1 Descriptive & Correlation Analysis': ('subsection', 'Descriptive \\& Correlation Analysis'),
    '5.2 Prediction Results': ('subsection', 'Prediction Results'),
    'Rainfall → Food Prices': ('subsubsection', 'Rainfall $\\rightarrow$ Food Prices'),
    'Food Prices → External Debt': ('subsubsection', 'Food Prices $\\rightarrow$ External Debt'),
    '5.3 Clustering Results': ('subsection', 'Clustering Results'),
    '5.4 Interactive Demo Results': ('subsection', 'Interactive Demo Results'),
    '6. CONCLUSION': ('section', 'Conclusion'),
    'REFERENCES': ('section*', 'References'),
    'APPENDICES': ('section*', 'Appendices'),
    'Appendix A: Full List of Divisions and PCODEs': ('subsection*', 'Appendix A: Full List of Divisions and PCODEs'),
    'Appendix B: Full Commodity Mapping': ('subsection*', 'Appendix B: Full Commodity Mapping'),
    'Appendix C: Final Merged Dataset Column Dictionary': ('subsection*', 'Appendix C: Final Merged Dataset Column Dictionary'),
    'Appendix D: Environment and Reproducibility Notes': ('subsection*', 'Appendix D: Environment and Reproducibility Notes'),
    'Appendix E: Repository Link': ('subsection*', 'Appendix E: Repository Link'),
}

# Define figure captions to recognize them and place a figure environment
figure_captions = {
    'Figure 1: Project data pipeline, system architecture diagram': ('report_images/image2.png', 'fig:pipeline'),
    'Figure 2: Schema Inspection': ('report_images/image3.png', 'fig:schema'),
    'Figure 3: The final merged dataset': ('report_images/image4.png', 'fig:merged'),
    'Figure 4: Correlation heatmap of all numeric variables': ('report_images/image5.png', 'fig:corrheatmap'),
    'Figure 5: Time series rainfall, food price, debt stock (1999–2024)': ('report_images/image6.png', 'fig:timeseries'),
    'Figure 6: Elbow plot for K-Means (inertia vs. k)': ('report_images/image7.png', 'fig:elbow'),
    'Figure 7: Screenshot of interactive demo widget price prediction panel': ('report_images/image8.png', 'fig:demo_price'),
    'Figure 8: Screenshot of interactive demo widget debt prediction panel': ('report_images/image9.png', 'fig:demo_debt'),
    'Figure 9: Screenshot of interactive demo widget risk classification panel': ('report_images/image10.png', 'fig:demo_risk'),
}

# Define table captions to recognize them and place a table environment
table_captions = {
    'Table 1: Summary of source datasets': 3,
    'Table 2: Commodity-to-category mapping (excerpt)': 4,
    'Table 3: External debt indicators used and their definitions': 5,
    'Table 4: Null counts before and after interpolation': 6,
    'Table 5: Descriptive statistics of merged dataset (post-cleaning)': 7,
    'Table 6: Model comparison, rainfall → individual commodity prices': 8,
    'Table 7: Model comparison, food prices → debt indicators': 9,
    'Table 8: K-Means cluster centers and risk label assignment': 10,
    'Table 9: Division-year risk classification counts': 11,
    'Table 10: Interactive demo sample inputs and outputs': 12,
    'Appendix A: Full List of Divisions and PCODEs': 13, # Table 13 is actually in Appendix A
    'Appendix C: Final Merged Dataset Column Dictionary': 14, # Table 14 is in Appendix C
}

# We can group sequential code blocks. Let's see what paragraphs are code blocks.
code_block_ranges = [
    (58, 65), (77, 83), (90, 91), (96, 103), (110, 127),
    (177, 184), (189, 196), (200, 212), (217, 237), (240, 256),
    (261, 272), (280, 286), (303, 313), (316, 325), (330, 349),
    (353, 366), (368, 391), (408, 421), (423, 429)
]

code_blocks_map = {}
for start, end in code_block_ranges:
    for i in range(start, end + 1):
        code_blocks_map[i] = (start, end)

# Beautifully wrapped and formatted python listings to prevent any line overflow in final PDF
override_code_blocks = {
    58: r"""rf_m = rf.groupBy('PCODE', 'year', 'month').agg(
    F.sum('rfh').alias('rainfall_mm'),
    F.sum('rfh_avg').alias('rainfall_historic_avg_mm')
).withColumn(
    'rainfall_anomaly_pct',
    (F.col('rainfall_mm') - F.col('rainfall_historic_avg_mm')) 
    / F.col('rainfall_historic_avg_mm') * 100
).withColumnRenamed('PCODE', 'pcode')""",

    77: r"""# Average food price calculation with custom array aggregation expressions
expr_str = """ + '"""' + r"""
aggregate(
    filter(
        array(
            rice_price_usd_per_kg, flour_price_usd_per_kg, 
            oil_price_usd_per_l, lentils_price_usd_per_kg
        ),
        x -> x is not null
    ),
    0D, (acc, x) -> acc + x
) / size(
    filter(
        array(
            rice_price_usd_per_kg, flour_price_usd_per_kg, 
            oil_price_usd_per_l, lentils_price_usd_per_kg
        ),
        x -> x is not null
    )
)
""" + '"""' + r"""
fp_m = fp_m.withColumn('avg_food_price_usd_per_kg', F.expr(expr_str))""",

    90: r"""# Cross-joining to expand the debt series subnationally
dbt_m = dbt_p.crossJoin(
    spark.createDataFrame([(y,) for y in range(YMIN, YMAX+1)], ['year'])
).crossJoin(div_df)""",

    96: r"""# Creating the full template grid
grid = spark.createDataFrame(
    [(d,) for d in divisions], ['pcode']
).crossJoin(
    spark.createDataFrame([(y,) for y in range(YMIN, YMAX+1)], ['year'])
).crossJoin(
    spark.createDataFrame([(m,) for m in range(1, 13)], ['month'])
)""",

    110: r"""# Window definition for linear interpolation
w_back = Window.partitionBy('pcode', 'commodity').orderBy('rn') \
               .rowsBetween(Window.unboundedPreceding, 0)
w_fwd = Window.partitionBy('pcode', 'commodity').orderBy('rn') \
              .rowsBetween(0, Window.unboundedFollowing)

prev_val = F.last(c, ignorenulls=True).over(w_back)
next_val = F.first(c, ignorenulls=True).over(w_fwd)

prev_rn = F.last(
    F.when(F.col(c).isNotNull(), F.col('rn')), 
    ignorenulls=True
).over(w_back)

next_rn = F.first(
    F.when(F.col(c).isNotNull(), F.col('rn')), 
    ignorenulls=True
).over(w_fwd)

interp_val = prev_val + (next_val - prev_val) * (F.col('rn') - prev_rn) \
             / (next_rn - prev_rn)

fp_interp = fp_grid.withColumn(
    c, 
    F.when(F.col(c).isNotNull(), F.col(c))
     .when(prev_val.isNotNull() & next_val.isNotNull(), interp_val)
     .when(prev_val.isNotNull(), prev_val)
     .otherwise(next_val)
)""",

    177: r"""!pip install -q pyspark
import os
import sys
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName('BDA_Project').getOrCreate()
YMIN, YMAX = 1999, 2024""",

    189: r"""rf_raw = spark.read.csv(
    'bgdrainfallsubnatfull.csv', header=True, inferSchema=True
)
fp_raw = spark.read.csv(
    'wfp_food_prices_bgd.csv', header=True, inferSchema=True
)
dbt_raw = spark.read.csv(
    'externaldebt_bgd.csv', header=True, inferSchema=True
)""",

    200: r"""# Rainfall aggregation and anomaly computation
rf = rf_raw.filter(F.col('adm_level') == 1)
rf_m = rf.groupBy('PCODE', 'year', 'month').agg(
    F.sum('rfh').alias('rainfall_mm'),
    F.sum('rfh_avg').alias('rainfall_historic_avg_mm')
).withColumn(
    'rainfall_anomaly_pct',
    (F.col('rainfall_mm') - F.col('rainfall_historic_avg_mm')) 
    / F.col('rainfall_historic_avg_mm') * 100
).withColumnRenamed('PCODE', 'pcode')""",

    217: r"""# Division name to PCODE mapping and commodity aggregation
map_expr = F.create_map([F.lit(x) for x in [
    'Barisal', 'BD10', 'Chittagong', 'BD20', 'Dhaka', 'BD30', 
    'Khulna', 'BD40', 'Mymensingh', 'BD45', 'Rajshahi', 'BD50', 
    'Rangpur', 'BD55', 'Sylhet', 'BD60'
]])

fp = fp_raw.withColumn('pcode', map_expr[F.col('admin1')]) \
           .filter(F.col('pcode').isNotNull())

RICE = [
    'Rice (coarse, BR-8/ 11/, Guti Sharna)', 'Rice (coarse)',
    'Rice (medium grain)', 'Rice (medium grain, Pyzam)', 
    'Rice (medium grain, BRRI-28/29)',
    'Rice (medium grain, BRRI-28/ 29/ 49)', 'Rice (medium grain, Kajla)',
    'Rice (medium grain, Nurjahan)', 'Rice (medium grain, Pyzam/BRRI-28/29)',
    'Rice (coarse, BRRI-28/29)', 'Rice (medium grain, Gazi)'
]

fp = fp.withColumn(
    'commodity_cat',
    F.when(F.col('name').isin(RICE), 'rice')
     .when(F.col('name') == 'Wheat flour', 'flour')
     .when(F.col('name').isin('Oil (palm)', 'Oil (mustard)', 'Oil (soybean, fortified)'), 'oil')
     .when(F.col('name') == 'Lentils (masur)', 'lentils')
).filter(F.col('commodity_cat').isNotNull())

fp = fp.withColumn(
    'norm_price',
    F.when(F.col('unit') == '100 KG', F.col('usdprice') / 100.0)
     .otherwise(F.col('usdprice'))
)

# Pivot categories to wide format
fp_wide = fp.groupBy('pcode', 'year', 'month', 'commodity_cat') \
            .agg(F.mean('norm_price').alias('price')) \
            .groupBy('pcode', 'year', 'month') \
            .pivot('commodity_cat', ['rice', 'flour', 'oil', 'lentils']) \
            .agg(F.first('price'))

# Rename columns
for cat in ['rice', 'flour', 'oil', 'lentils']:
    unit = 'l' if cat == 'oil' else 'kg'
    fp_wide = fp_wide.withColumnRenamed(cat, f'{cat}_price_usd_per_{unit}')""",

    240: r"""IND = {
    'External debt stocks, total (DOD, current US$)': 'debt_stock_total_usd',
    'Debt service on external debt, total (TDS, current US$)': 'debt_service_total_usd',
    'External debt stocks (% of GNI)': 'debt_stock_pct_gni'
}

dbt = dbt_raw.filter(
    (F.col('Country Code') == 'BGD') & 
    F.col('Indicator Name').isin(list(IND.keys()))
)

dbt_p = dbt.groupBy('Year') \
           .pivot('Indicator Name', list(IND.keys())) \
           .agg(F.first('Value'))

dbt_p = dbt_p.withColumnRenamed('Year', 'year') \
             .filter((F.col('year') >= YMIN) & (F.col('year') <= YMAX))

# Rename and scale debt indicators
for ind_name, col_name in IND.items():
    dbt_p = dbt_p.withColumnRenamed(ind_name, col_name)

# Expand nationally-reported debt to all 8 divisions
divisions = ['BD10', 'BD20', 'BD30', 'BD40', 'BD45', 'BD50', 'BD55', 'BD60']
div_df = spark.createDataFrame([(d,) for d in divisions], ['pcode'])
dbt_m = dbt_p.crossJoin(div_df)""",

    261: r"""# Constructing template grid and merging
grid = spark.createDataFrame([(d,) for d in divisions], ['pcode']) \
            .crossJoin(spark.createDataFrame([(y,) for y in range(YMIN, YMAX+1)], ['year'])) \
            .crossJoin(spark.createDataFrame([(m,) for m in range(1, 12+1)], ['month']))

merged = grid.join(rf_m, ['pcode', 'year', 'month'], 'left') \
             .join(fp_wide, ['pcode', 'year', 'month'], 'left') \
             .join(dbt_m, ['pcode', 'year', 'month'], 'left')

# Add date column
merged = merged.withColumn(
    'date', 
    F.to_date(F.concat_ws('-', 'year', 'month', F.lit(1)))
)""",

    280: r"""# Null check
num_cols = [
    c for c in merged.columns 
    if c not in ('pcode', 'year', 'month', 'date')
]
merged.select(
    [F.sum(F.col(c).isNull().cast('int')).alias(c) for c in num_cols]
).show()""",

    303: r"""import matplotlib.pyplot as plt
import seaborn as sns

m = merged
cols = [
    'rainfall_mm', 'avg_food_price_usd_per_kg', 'rice_price_usd_per_kg', 
    'flour_price_usd_per_kg', 'oil_price_usd_per_l', 'lentils_price_usd_per_kg', 
    'debt_stock_total_usd', 'debt_service_total_usd', 'debt_stock_pct_gni'
]
corr_pd = m.select(cols).toPandas()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_pd.corr(), annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()""",

    316: r"""# National average trends
nat = m.groupBy('date').agg(
    F.mean('rainfall_mm').alias('rainfall_mm'),
    F.mean('avg_food_price_usd_per_kg').alias('avg_food_price_usd_per_kg'),
    F.mean('debt_stock_total_usd').alias('debt_stock_total_usd')
).orderBy('date').toPandas()

fig, ax = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
ax[0].plot(nat['date'], nat['rainfall_mm'], color='steelblue')
ax[0].set_ylabel('Rainfall (mm)')

ax[1].plot(nat['date'], nat['avg_food_price_usd_per_kg'], color='darkorange')
ax[1].set_ylabel('Avg Food Price (USD/kg)')

ax[2].plot(nat['date'], nat['debt_stock_total_usd'], color='seagreen')
ax[2].set_ylabel('Debt Stock (USD)')

plt.tight_layout()
plt.show()""",

    330: r"""# Supervised modeling: Rainfall -> Food Prices
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor, RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

train, test = m.randomSplit([0.8, 0.2], seed=1)
idx = StringIndexer(inputCol='pcode', outputCol='pcode_idx')
ohe = OneHotEncoder(inputCol='pcode_idx', outputCol='pcode_ohe')
va = VectorAssembler(
    inputCols=[
        'rainfall_mm', 'rainfall_historic_avg_mm', 
        'rainfall_anomaly_pct', 'month', 'pcode_ohe'
    ], 
    outputCol='features'
)

price_targets = [
    'rice_price_usd_per_kg', 'flour_price_usd_per_kg', 
    'oil_price_usd_per_l', 'lentils_price_usd_per_kg', 
    'avg_food_price_usd_per_kg'
]

for target in price_targets:
    ev = RegressionEvaluator(
        labelCol=target, predictionCol='prediction', metricName='r2'
    )
    for Reg, name, kw in [
        (LinearRegression, 'LR', {}),
        (DecisionTreeRegressor, 'DT', {'maxDepth': 5, 'minInstancesPerNode': 20}),
        (RandomForestRegressor, 'RF', {'numTrees': 100, 'maxDepth': 6, 'minInstancesPerNode': 20})
    ]:
        pipe = Pipeline(stages=[idx, ohe, va, Reg(featuresCol='features', labelCol=target, **kw)])
        model = pipe.fit(train)
        r2_tr = ev.evaluate(model.transform(train))
        r2_te = ev.evaluate(model.transform(test))
        print(f"{target} ({name}): TrainR2={r2_tr:.3f} TestR2={r2_te:.3f} Gap={r2_tr-r2_te:.3f}")""",

    353: r"""# Supervised modeling: Food Prices -> Debt
va2 = VectorAssembler(
    inputCols=[
        'rice_price_usd_per_kg', 'flour_price_usd_per_kg', 
        'oil_price_usd_per_l', 'lentils_price_usd_per_kg', 
        'avg_food_price_usd_per_kg'
    ], 
    outputCol='features'
)

debt_targets = ['debt_stock_total_usd', 'debt_stock_pct_gni']

for target in debt_targets:
    ev = RegressionEvaluator(
        labelCol=target, predictionCol='prediction', metricName='r2'
    )
    for Reg, name, kw in [
        (LinearRegression, 'LR', {}),
        (DecisionTreeRegressor, 'DT', {'maxDepth': 5, 'minInstancesPerNode': 20}),
        (RandomForestRegressor, 'RF', {'numTrees': 100, 'maxDepth': 6, 'minInstancesPerNode': 20})
    ]:
        pipe = Pipeline(stages=[va2, Reg(featuresCol='features', labelCol=target, **kw)])
        model = pipe.fit(train)
        r2_tr = ev.evaluate(model.transform(train))
        r2_te = ev.evaluate(model.transform(test))
        print(f"{target} ({name}): TrainR2={r2_tr:.3f} TestR2={r2_te:.3f} Gap={r2_tr-r2_te:.3f}")""",

    368: r"""# Unsupervised modeling: K-Means Clustering
from pyspark.ml.clustering import KMeans as SparkKMeans
from pyspark.ml.feature import StandardScaler as SparkScaler

agg = m.groupBy('pcode', 'year').agg(
    F.mean('rainfall_anomaly_pct').alias('rainfall_anomaly_pct'),
    F.mean('avg_food_price_usd_per_kg').alias('avg_food_price_usd_per_kg'),
    F.mean('debt_stock_pct_gni').alias('debt_stock_pct_gni'),
    F.mean('debt_service_total_usd').alias('debt_service_total_usd')
)

feat_cols = [
    'rainfall_anomaly_pct', 'avg_food_price_usd_per_kg', 
    'debt_stock_pct_gni', 'debt_service_total_usd'
]
va3 = VectorAssembler(inputCols=feat_cols, outputCol='raw_features')
scaler = SparkScaler(
    inputCol='raw_features', outputCol='features', 
    withMean=True, withStd=True
)
pipe = Pipeline(stages=[va3, scaler])
scaled_df = pipe.fit(agg).transform(agg)

# Find optimal k using inertia
inertias = {}
for k in range(2, 8):
    km = SparkKMeans(featuresCol='features', k=k, seed=1)
    model = km.fit(scaled_df)
    inertias[k] = model.summary.trainingCost

# Run K-Means with k=4
km_final = SparkKMeans(featuresCol='features', k=4, seed=1)
kmodel_full = km_final.fit(scaled_df)
result = kmodel_full.transform(scaled_df)

result.groupBy('prediction').count().show()
print("centers:", kmodel_full.clusterCenters())""",

    408: r"""def predict_prices(rainfall_mm, hist_avg_mm, month, pcode):
    anomaly = (rainfall_mm - hist_avg_mm) / hist_avg_mm * 100
    row = spark.createDataFrame(
        [(pcode, float(rainfall_mm), float(hist_avg_mm), float(anomaly), int(month))], 
        ['pcode', 'rainfall_mm', 'rainfall_historic_avg_mm', 'rainfall_anomaly_pct', 'month']
    )
    return {
        t: round(price_models[t].transform(row).select('prediction').first()[0], 3) 
        for t in price_targets
    }

def predict_debt(rice, flour, oil, lentils):
    avg = (rice + flour + oil + lentils) / 4.0
    row = spark.createDataFrame(
        [(float(rice), float(flour), float(oil), float(lentils), avg)], 
        ['rice_price_usd_per_kg', 'flour_price_usd_per_kg', 'oil_price_usd_per_l', 
         'lentils_price_usd_per_kg', 'avg_food_price_usd_per_kg']
    )
    return round(debt_model.transform(row).select('prediction').first()[0], 2)

def predict_risk(rainfall_anomaly_pct, avg_food_price, debt_pct_gni, debt_service):
    row = spark.createDataFrame(
        [(float(rainfall_anomaly_pct), float(avg_food_price), 
          float(debt_pct_gni), float(debt_service))], 
        feat_cols
    )
    cl = kmodel_full.transform(row).select('prediction').first()[0]
    return risk_labels[cl]""",

    423: r"""print("prices:", predict_prices(50, 200, 4, 'BD30'))
print("debt:", predict_debt(0.5, 0.5, 1.2, 1.0))
print("risk:", predict_risk(-30, 0.9, 30, 8e9))"""
}

# Let's start assembling the LaTeX code
latex_doc = []

# Add LaTeX Header
latex_header = r"""% ============================================================
%  Big Data Analytics – Project Report
%  Course: MITE 431  |  Institute of Information Technology, University of Dhaka
%  Converted from ProjectReport.docx (Full Thesis-Level Report)
% ============================================================
\documentclass[12pt,a4paper]{article}

% ---------- Packages ----------
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[left=3cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{setspace}
\usepackage{parskip}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{caption}
\usepackage{float}
\usepackage{microtype}
\usepackage{lmodern}
\usepackage{tocloft}
\usepackage{mdframed}

% ---------- Line Spacing ----------
\onehalfspacing

% ---------- Colours ----------
\definecolor{codeblue}{RGB}{0,83,156}
\definecolor{codegray}{RGB}{245,245,245}
\definecolor{codecomment}{RGB}{100,100,100}
\definecolor{codestring}{RGB}{163,21,21}
\definecolor{codenumber}{RGB}{100,100,100}
\definecolor{titleblue}{RGB}{0,51,102}
\definecolor{sectionblue}{RGB}{0,83,156}

% ---------- Listings style ----------
\lstdefinestyle{pythonstyle}{
  language=Python,
  backgroundcolor=\color{codegray},
  basicstyle=\ttfamily\footnotesize,
  keywordstyle=\color{codeblue}\bfseries,
  stringstyle=\color{codestring},
  commentstyle=\color{codecomment}\itshape,
  numberstyle=\tiny\color{codenumber},
  numbers=left,
  stepnumber=1,
  numbersep=8pt,
  showstringspaces=false,
  breaklines=true,
  breakatwhitespace=false,
  frame=single,
  framerule=0.5pt,
  rulecolor=\color{gray!50},
  captionpos=b,
  tabsize=4,
  columns=fullflexible,
  keepspaces=true,
  xleftmargin=15pt,
  xrightmargin=5pt,
  aboveskip=8pt,
  belowskip=8pt,
}
\lstset{style=pythonstyle}

% ---------- Section formatting ----------
\titleformat{\section}{\large\bfseries\color{titleblue}}{\thesection}{1em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries\color{sectionblue}}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\itshape}{\thesubsubsection}{1em}{}
\titlespacing*{\section}{0pt}{3.5ex plus 1ex minus .2ex}{2.3ex plus .2ex}
\titlespacing*{\subsection}{0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}
\titlespacing*{\subsubsection}{0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}

% ---------- Header / Footer ----------
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textit{Big Data Analytics -- Project Report}}
\fancyhead[R]{\small\textit{MITE 431}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% ---------- Hyperlinks ----------
\hypersetup{
  colorlinks=true,
  linkcolor=sectionblue,
  urlcolor=sectionblue,
  citecolor=sectionblue,
  pdftitle={Big Data Analytics - Project Report},
  pdfauthor={Md. Mamun Ur Rashed, Mostofa Aminur Rashid},
}

% ---------- Caption formatting ----------
\captionsetup{font=small,labelfont=bf,skip=4pt}

% ---------- Output directory for images ----------
\graphicspath{{./report_images/}}

\begin{document}
"""

latex_doc.append(latex_header)

# Generate Title Page
title_page_latex = r"""
% ============================================================
%  TITLE PAGE
% ============================================================
\begin{titlepage}
  \centering
  \vspace*{0.5cm}
  \includegraphics[width=1.5in]{report_images/image1.png}\\[0.6cm]
  {\Huge\bfseries\color{titleblue} Project Report}\\[0.4cm]
  {\large\bfseries on}\\[0.6cm]
  {\LARGE\bfseries\color{titleblue}
    RAINFALL, FOOD PRICES, AND EXTERNAL DEBT\\[0.2cm]
    IN BANGLADESH}\\[0.4cm]
  {\large\bfseries A PREDICTIVE AND CLUSTERING ANALYSIS}
  \vspace{1.0cm}
  \rule{0.8\textwidth}{1.2pt}
  \vspace{0.4cm}
  \begin{tabular}{ll}
    \textbf{Course Name:} & Big Data Analytics \\[4pt]
    \textbf{Course Code:} & MITE 431 \\
  \end{tabular}
  \vspace{1.0cm}
  \textbf{\large Submitted by:}\\[0.3cm]
  \begin{tabular}{ll}
    Md.\ Mamun Ur Rashed  & \quad ID: EMIT2506120, Session: 2024-25 \\[4pt]
    Mostofa Aminur Rashid & \quad ID: EMIT2506107, Session: 2024-25 \\
  \end{tabular}
  \vspace{1.0cm}
  \textbf{\large Submitted to:}\\[0.3cm]
  \begin{tabular}{l}
    Shah Mostafa Khaled, Ph.D \\
    Associate Professor, IIT \\[6pt]
    Mridha Md.\ Nafis Fuad \\
    Lecturer, IIT \\
  \end{tabular}
  \vfill
  \rule{0.8\textwidth}{1.2pt}\\[0.4cm]
  {\large\bfseries INSTITUTE OF INFORMATION TECHNOLOGY}\\
  {\large\bfseries UNIVERSITY OF DHAKA}
\end{titlepage}
"""

latex_doc.append(title_page_latex)

# Table builders
def build_table_latex(t_idx):
    rows = tables[t_idx]
    if t_idx == 3: # Summary of source datasets
        return r"""\begin{table}[H]
\centering
\caption{Summary of source datasets}
\label{tab:datasets}
\begin{tabularx}{\textwidth}{lXrrl}
\toprule
\textbf{Dataset} & \textbf{File} & \textbf{Rows} & \textbf{Cols} & \textbf{Granularity} \\
\midrule
Rainfall      & bgdrainfallsubnatfull.csv & 120,398 & 15 & Daily-ish decad, subnational \\
Food Prices   & wfp\_food\_prices\_bgd.csv  & 19,080  & 16 & Market-level, per observation \\
External Debt & externaldebt\_bgd.csv       & 2,642   & 6  & Annual, national \\
\bottomrule
\end{tabularx}
\end{table}"""
    elif t_idx == 4: # Commodity-to-category mapping
        return r"""\begin{table}[H]
\centering
\caption{Commodity-to-category mapping (excerpt)}
\label{tab:commodity}
\begin{tabularx}{\textwidth}{lX}
\toprule
\textbf{Category} & \textbf{Included Raw Commodity Names} \\
\midrule
Rice    & Rice (coarse), Rice (coarse, Guti Sharna), Rice (medium grain), Rice (Kajla), Rice (Nurjahan), Rice (Pyzam), Rice (BRRI-28/29/49), Rice (Gazi), and 3 more \\
Flour   & Wheat flour \\
Oil     & Oil (palm), Oil (mustard), Oil (soybean, fortified) \\
Lentils & Lentils (masur) \\
\bottomrule
\end{tabularx}
\end{table}"""
    elif t_idx == 5: # External debt indicators used and their definitions
        return r"""\begin{table}[H]
\centering
\caption{External debt indicators used and their definitions}
\label{tab:debtindicators}
\begin{tabularx}{\textwidth}{llX}
\toprule
\textbf{Column Name} & \textbf{World Bank Indicator} & \textbf{Description} \\
\midrule
debt\_stock\_total\_usd   & External debt stocks, total (DOD, current US\$)         & Total outstanding external debt \\
debt\_service\_total\_usd & Debt service on external debt, total (TDS, current US\$) & Annual repayment obligation \\
debt\_stock\_pct\_gni     & External debt stocks (\% of GNI)                         & Debt burden relative to national income \\
\bottomrule
\end{tabularx}
\end{table}"""
    elif t_idx == 6: # Null counts before and after interpolation
        return r"""\begin{table}[H]
\centering
\caption{Null counts before and after interpolation}
\label{tab:nullcounts}
\begin{tabular}{lrr}
\toprule
\textbf{Column} & \textbf{Nulls Before} & \textbf{Nulls After} \\
\midrule
rainfall\_mm / historic\_avg / anomaly & 0     & 0 \\
rice\_price\_usd\_per\_kg              & 1,409 & 0 \\
flour\_price\_usd\_per\_kg             & 1,393 & 0 \\
oil\_price\_usd\_per\_l               & 1,447 & 0 \\
lentils\_price\_usd\_per\_kg           & 1,432 & 0 \\
avg\_food\_price\_usd\_per\_kg         &   998 & 0 \\
debt\_stock\_total\_usd                &     0 & 0 \\
debt\_service\_total\_usd              &     0 & 0 \\
debt\_stock\_pct\_gni                  &     0 & 0 \\
\bottomrule
\end{tabular}
\end{table}"""
    elif t_idx == 7: # Descriptive statistics
        return r"""\begin{table}[H]
\centering
\caption{Descriptive statistics of merged dataset (post-cleaning)}
\label{tab:descriptive}
\setlength{\tabcolsep}{4pt}
\small
\begin{tabularx}{\textwidth}{Xrrrrrrrr}
\toprule
\textbf{Variable} & \textbf{Count} & \textbf{Mean} & \textbf{Std} & \textbf{Min} & \textbf{25\%} & \textbf{50\%} & \textbf{75\%} & \textbf{Max} \\
\midrule
Year                                & 2496 & 2011.500 & 7.502   & 1999    & 2005   & 2011.500 & 2018   & 2024    \\
Month                               & 2496 & 6.500    & 3.453    & 1       & 3.750  & 6.500    & 9.250  & 12      \\
Rainfall (mm)                       & 2496 & 229.034  & 258.493  & 2.167    & 15.209 & 152.170  & 364.633 & 2031.438 \\
Rainfall Historic Avg (mm)          & 2496 & 226.876  & 233.472  & 3.108    & 19.222 & 169.305  & 361.274 & 1092.248 \\
Rainfall Anomaly (\%)               & 2496 & 0.910    & 56.448   & $-$85.986 & $-$35.104 & $-$9.918 & 22.085 & 572.223 \\
Rice Price (USD/kg)                 & 2496 & 0.384   & 0.094   & 0.158   & 0.310  & 0.420   & 0.450  & 0.650   \\
Flour Price (USD/kg)                & 2496 & 0.402   & 0.078   & 0.261   & 0.351  & 0.390   & 0.430  & 0.687   \\
Oil Price (USD/L)                   & 2496 & 0.945   & 0.245   & 0.500   & 0.830  & 0.870   & 1.076  & 2.030   \\
Lentils Price (USD/kg)              & 2496 & 0.929   & 0.189   & 0.630   & 0.790  & 0.908   & 1.050  & 1.560   \\
Avg Food Price (USD/kg)             & 2496 & 0.629   & 0.217   & 0.158   & 0.563  & 0.635   & 0.771  & 1.560   \\
Total Debt Stock (USD)              & 2496 & 4.15e10  & 2.86e10  & 1.50e10  & 1.97e10 & 2.81e10  & 5.71e10 & 1.04e11 \\
Total Debt Service (USD)            & 2496 & 2.48e9   & 2.34e9   & 6.53e8   & 7.73e8  & 1.60e9   & 3.03e9  & 8.60e9  \\
Debt Stock (\% of GNI)              & 2496 & 22.599   & 4.462    & 14.972   & 19.126 & 21.789   & 26.582  & 31.130  \\
\bottomrule
\end{tabularx}
\end{table}"""
    elif t_idx == 8: # Model comparison rainfall -> individual commodity prices
        return r"""\begin{table}[H]
\centering
\caption{Model comparison --- Rainfall $\rightarrow$ individual commodity prices}
\label{tab:model1}
\begin{tabular}{llrrr}
\toprule
\textbf{Target} & \textbf{Model} & \textbf{Train R$^2$} & \textbf{Test R$^2$} & \textbf{Gap} \\
\midrule
Rice           & Linear Regression & 0.168 &  0.150 &  0.017 \\
Rice           & Decision Tree     & 0.133 &  0.072 &  0.061 \\
Rice           & Random Forest     & 0.152 &  0.110 &  0.042 \\
\midrule
Flour          & Linear Regression & 0.063 &  0.076 & $-$0.013 \\
Flour          & Decision Tree     & 0.093 &  0.033 &  0.060 \\
Flour          & Random Forest     & 0.097 &  0.053 &  0.044 \\
\midrule
Oil            & Linear Regression & 0.040 &  0.034 &  0.006 \\
Oil            & Decision Tree     & 0.056 &  0.011 &  0.045 \\
Oil            & Random Forest     & 0.072 &  0.033 &  0.040 \\
\midrule
Lentils        & Linear Regression & 0.021 &  0.032 & $-$0.011 \\
Lentils        & Decision Tree     & 0.048 & $-$0.034 & 0.082 \\
Lentils        & Random Forest     & 0.059 &  0.019 &  0.040 \\
\midrule
Avg Food Price & Linear Regression & 0.075 &  0.062 &  0.014 \\
Avg Food Price & Decision Tree     & 0.087 &  0.040 &  0.047 \\
Avg Food Price & Random Forest     & 0.098 &  0.052 &  0.046 \\
\bottomrule
\end{tabular}
\end{table}"""
    elif t_idx == 9: # Model comparison food prices -> debt indicators
        return r"""\begin{table}[H]
\centering
\caption{Model comparison --- Food prices $\rightarrow$ debt indicators}
\label{tab:model2}
\begin{tabular}{llrrr}
\toprule
\textbf{Target} & \textbf{Model} & \textbf{Train R$^2$} & \textbf{Test R$^2$} & \textbf{Gap} \\
\midrule
Debt Stock (Total USD) & Linear Regression & 0.460 & 0.485 & $-$0.025 \\
Debt Stock (Total USD) & Decision Tree     & 0.709 & 0.750 & $-$0.042 \\
Debt Stock (Total USD) & Random Forest     & \textbf{0.758} & \textbf{0.773} & \textbf{$-$0.015} \\
\midrule
Debt Stock (\% GNI)    & Linear Regression & 0.418 & 0.347 &  0.071 \\
Debt Stock (\% GNI)    & Decision Tree     & 0.643 & 0.599 &  0.045 \\
\bottomrule
\end{tabular}
\end{table}"""
    elif t_idx == 10: # K-Means cluster centers and risk label assignment
        return r"""\begin{table}[H]
\centering
\caption{K-Means cluster centers and risk label assignment}
\label{tab:clustcenters}
\setlength{\tabcolsep}{5pt}
\small
\begin{tabular}{lrrrrrr}
\toprule
\textbf{Cluster ID} & \textbf{Rainfall Anomaly (std)} & \textbf{Food Price (std)} & \textbf{Debt \% GNI (std)} & \textbf{Debt Service (std)} & \textbf{Composite Risk Score} & \textbf{Risk Label} \\
\midrule
2 & $-$0.344 & $-$1.867 &  1.249 & $-$0.753 & $-$1.027 & Low Risk      \\
3 &  0.177   & $-$0.100 &  1.110 & $-$0.723 &  0.110   & Moderate Risk \\
0 & $-$0.663 &  0.379   & $-$0.589 & $-$0.331 & 0.122  & High Risk     \\
1 &  0.869   &  0.652   & $-$0.719 &  1.290   & 0.354  & Severe Risk   \\
\bottomrule
\end{tabular}
\end{table}"""
    elif t_idx == 11: # Division-year risk classification counts by cluster
        return r"""\begin{table}[H]
\centering
\caption{Division-year risk classification counts by cluster}
\label{tab:riskdist}
\begin{tabular}{llrr}
\toprule
\textbf{Risk Level} & \textbf{Cluster ID} & \textbf{Count} & \textbf{Approx. Share} \\
\midrule
Low Risk      & 2 &  34 & 16.3\% \\
Moderate Risk & 3 &  40 & 19.2\% \\
High Risk     & 0 &  73 & 35.1\% \\
Severe Risk   & 1 &  61 & 29.3\% \\
Total         &   & \textbf{208} & \textbf{100\%} \\
\bottomrule
\end{tabular}
\end{table}"""
    elif t_idx == 12: # Interactive demo sample inputs and outputs
        return r"""\begin{table}[H]
\centering
\caption{Interactive demo sample inputs and outputs}
\label{tab:demodemo}
\begin{tabularx}{\textwidth}{lXX}
\toprule
\textbf{Panel} & \textbf{Sample Input} & \textbf{Output} \\
\midrule
Price Prediction    & Dhaka (BD30), rainfall=50mm, historic avg=200mm, month=4 & Rice: \$0.365/kg, Flour: \$0.390/kg, Oil: \$0.974/L, Lentils: \$0.932/kg, Avg: \$0.562/kg \\
Debt Prediction     & Rice=\$0.50, Flour=\$0.50, Oil=\$1.20, Lentils=\$1.00    & Predicted debt stock: \textasciitilde\$89.37 billion \\
Risk Classification & Rainfall anomaly=-30\%, Avg food price=\$0.90, Debt \%GNI=30\%, Debt service=\$8B & Severe Risk \\
\bottomrule
\end{tabularx}
\end{table}"""
    elif t_idx == 13: # Appendix A
        return r"""\begin{table}[H]
\centering
\caption{Appendix A: Bangladesh administrative divisions and PCODEs}
\label{tab:divisions}
\begin{tabular}{ll}
\toprule
\textbf{Division (English)} & \textbf{PCODE} \\
\midrule
Barishal   & BD10 \\
Chattogram & BD20 \\
Dhaka      & BD30 \\
Khulna     & BD40 \\
Mymensingh & BD45 \\
Rajshahi   & BD50 \\
Rangpur    & BD55 \\
Sylhet     & BD60 \\
\bottomrule
\end{tabular}
\end{table}"""
    elif t_idx == 14: # Appendix C
        return r"""\begin{table}[H]
\centering
\caption{Appendix C: Final merged dataset column dictionary}
\label{tab:schema}
\begin{tabularx}{\textwidth}{llX}
\toprule
\textbf{Column} & \textbf{Type} & \textbf{Unit/Description} \\
\midrule
pcode                          & String  & Division code \\
year                           & Integer & 1999--2024 \\
month                          & Integer & 1--12 \\
date                           & Date    & First of month \\
rainfall\_mm                   & Float   & Monthly rainfall total (mm) \\
rainfall\_historic\_avg\_mm    & Float   & Historic average rainfall for that month (mm) \\
rainfall\_anomaly\_pct         & Float   & \% deviation from historic average \\
rice\_price\_usd\_per\_kg      & Float   & Rice price, USD per kg \\
flour\_price\_usd\_per\_kg     & Float   & Wheat flour price, USD per kg \\
oil\_price\_usd\_per\_l        & Float   & Edible oil price, USD per liter \\
lentils\_price\_usd\_per\_kg   & Float   & Lentils price, USD per kg \\
avg\_food\_price\_usd\_per\_kg & Float   & Mean of available commodity prices \\
debt\_stock\_total\_usd        & Float   & National external debt stock, USD \\
debt\_service\_total\_usd      & Float   & National annual debt service, USD \\
debt\_stock\_pct\_gni          & Float   & External debt as \% of GNI \\
\bottomrule
\end{tabularx}
\end{table}"""
    return ''

# Let's run through paragraphs in document order
skip_until = -1
in_abstract = False

for idx, p in enumerate(paragraphs):
    if idx <= skip_until:
        continue
    
    txt = p['text']
    
    # 1. Skip cover page paragraphs
    if idx <= 21:
        continue
        
    # 2. Check if abstract start
    if txt == 'ABSTRACT':
        in_abstract = True
        latex_doc.append(r"""
\begin{mdframed}[backgroundcolor=gray!8,linecolor=titleblue,linewidth=1.5pt,
                 innertopmargin=10pt,innerbottommargin=10pt,
                 innerleftmargin=14pt,innerrightmargin=14pt]
\section*{\centering ABSTRACT}
\addcontentsline{toc}{section}{Abstract}
""")
        # Combine paragraphs 23 and 24 (the abstract text)
        abstract_text = paragraphs[23]['text'] + "\n\n" + paragraphs[24]['text']
        # Convert → to \rightarrow
        abstract_text = abstract_text.replace('→', '$\\rightarrow$')
        latex_doc.append(abstract_text)
        latex_doc.append("\n\\end{mdframed}\n\\newpage\n")
        
        # Add dynamic Table of Contents, Lists
        latex_doc.append(r"""
\tableofcontents
\newpage
\listoffigures
\newpage
\listoftables
\newpage
""")
        skip_until = 25 # Skip paragraph 25 (empty space) and abstract paragraphs
        in_abstract = False
        continue

    # Skip manual Table of Contents, List of Figures, List of Tables placeholders in the original DOCX
    # (since we generate them dynamically)
    if idx in range(26, 33): # covers Paragraph 26 to 32 (TOC, list of figures, list of tables)
        continue

    # Skip table captions when we find them, since the table builder handles captions
    if txt in table_captions:
        # We also need to skip the next table block
        t_idx = table_captions[txt]
        latex_doc.append(build_table_latex(t_idx))
        continue

    # 3. Check for Headings
    if txt in headings_map:
        tag, title = headings_map[txt]
        prefix_cmd = ""
        if tag.startswith("section"):
            prefix_cmd = "\n\\clearpage\n"
        latex_doc.append(f"{prefix_cmd}\\{tag}{{{title}}}\n")
        continue

    # 4. Check if code block
    if idx in code_blocks_map:
        start, end = code_blocks_map[idx]
        if 'override_code_blocks' in globals() and start in override_code_blocks:
            code_content = override_code_blocks[start].strip()
        else:
            # Reconstruct code block from paragraphs start to end
            code_lines = []
            for c_idx in range(start, end + 1):
                c_txt = paragraphs[c_idx]['text']
                # Clean up text from italic artifacts
                if c_idx == start:
                    if c_txt.startswith('Python') or c_txt.strip() == 'Python':
                        c_txt = c_txt.replace('Python', '', 1).strip()
                code_lines.append(c_txt)
            
            code_content = '\n'.join(code_lines).strip()
            # Clean escape chars
            code_content = code_content.replace('\\{', '{').replace('\\}', '}').replace('\\_', '_')
            code_content = code_content.replace('\\textbackslash{}', '\\').replace('\\textbackslash', '\\')
            code_content = code_content.replace('\\textquotesingle{}', "'").replace('\\textquotesingle', "'")
            code_content = code_content.replace('\\textgreater{}', '>').replace('\\textgreater', '>')
        
        # Write listing
        latex_doc.append(f"\n\\begin{{lstlisting}}[language=Python]\n{code_content}\n\\end{{lstlisting}}\n")
        skip_until = end
        continue

    # 5. Check if figure caption
    if txt in figure_captions:
        img_name, label = figure_captions[txt]
        caption_text = txt.split(':', 1)[1].strip() if ':' in txt else txt
        # Write figure
        # Let's adjust width specifically for some figures to fit them nicely
        width_str = '0.85\\textwidth'
        if img_name in ('image8.png', 'image9.png', 'image10.png'): # demo panels are small
            width_str = '0.74\\textwidth'
        elif img_name == 'image2.png': # pipeline diagram
            width_str = '0.80\\textwidth'
        
        latex_doc.append(f"""
\\begin{{figure}}[H]
  \\centering
  \\includegraphics[width={width_str}]{{{img_name}}}
  \\caption{{{caption_text}}}
  \\label{{{label}}}
\\end{{figure}}
""")
        continue

    # 6. Check if it's a list item (docx list paragraphs)
    if p['style'] == 'List Paragraph':
        # Let's wrap list items in itemize
        # We check if previous element was also List Paragraph; if not, open itemize
        prev_p = paragraphs[idx - 1] if idx > 0 else None
        next_p = paragraphs[idx + 1] if idx < len(paragraphs) - 1 else None
        
        prefix = ''
        suffix = ''
        if not prev_p or prev_p['style'] != 'List Paragraph':
            prefix = '\\begin{itemize}[leftmargin=2em]\n'
        if not next_p or next_p['style'] != 'List Paragraph':
            suffix = '\n\\end{itemize}'
            
        # Clean text
        item_text = txt
        # Convert → to \rightarrow
        item_text = item_text.replace('→', '$\\rightarrow$')
        # Clean quotes
        item_text = item_text.replace('’', "'").replace('‘', "'").replace('”', '"').replace('“', '"')
        
        latex_doc.append(f"{prefix}  \\item {item_text}{suffix}\n")
        continue

    # 7. Standard Paragraph
    # Clean text from quotes and math symbols
    cleaned_txt = txt
    cleaned_txt = cleaned_txt.replace('$', '\\$')
    cleaned_txt = cleaned_txt.replace('%', '\\%')
    cleaned_txt = cleaned_txt.replace('&', '\\&')
    cleaned_txt = cleaned_txt.replace('_', '\\_')
    cleaned_txt = cleaned_txt.replace('→', '$\\rightarrow$')
    cleaned_txt = cleaned_txt.replace('—', '---')
    cleaned_txt = cleaned_txt.replace('–', '--')
    cleaned_txt = cleaned_txt.replace('×', '$\\times$')
    # Restore LaTeX tags if they were escaped
    cleaned_txt = cleaned_txt.replace('\\$GNI\\$', '$GNI$')
    cleaned_txt = cleaned_txt.replace('\\$k\\$', '$k$')
    cleaned_txt = cleaned_txt.replace('\\$R^2\\$', '$R^2$')
    cleaned_txt = cleaned_txt.replace('\\$R\\^2\\$', '$R^2$')
    cleaned_txt = cleaned_txt.replace('\\$\\sim\\$', '$\\sim$')
    cleaned_txt = cleaned_txt.replace('\\$R\\^2 \\textbackslash{}approx 0.75--0.77\\$', '$R^2 \\approx 0.75$--$0.77$')
    cleaned_txt = cleaned_txt.replace('\\$R\\^2 \\textbackslash{}sim 0.15\\$', '$R^2 \\sim 0.15$')
    cleaned_txt = cleaned_txt.replace('\\$R\\^2 \\textbackslash{}approx 0.01\\$', '$R^2 \\approx 0.01$')
    cleaned_txt = cleaned_txt.replace('\\$R\\^2 \\textbackslash{}approx 0.53\\$', '$R^2 \\approx 0.53$')
    cleaned_txt = cleaned_txt.replace('\\$k \\textbackslash{}ge 2\\$', '$k \\ge 2$')
    
    # Format inline references [1], [2], [3], [4]
    cleaned_txt = cleaned_txt.replace('[1]', '~[1]')
    cleaned_txt = cleaned_txt.replace('[2]', '~[2]')
    cleaned_txt = cleaned_txt.replace('[3]', '~[3]')
    cleaned_txt = cleaned_txt.replace('[4]', '~[4]')
    
    latex_doc.append(f"\n{cleaned_txt}\n")

# Add Footer
latex_doc.append("\n\\end{document}\n")

# Write final report.tex with regex post-processing for table spacing
latex_str = ''.join(latex_doc)
latex_str = re.sub(
    r'\\begin{table}\[H\]\n\\centering\n',
    r'\\begin{table}[H]\n\\centering\n\\begin{spacing}{1.15}\n',
    latex_str
)
latex_str = re.sub(
    r'\\end{tabular(x)?}\n\\end{table}',
    r'\\end{tabular\1}\n\\end{spacing}\n\\end{table}',
    latex_str
)

with open(r'd:\github\-big_data_project\report.tex', 'w', encoding='utf-8') as f:
    f.write(latex_str)

print("LaTeX report.tex generated successfully.")
