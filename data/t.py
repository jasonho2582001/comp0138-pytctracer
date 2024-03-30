import pandas as pd
import numpy as np
chartify_analysis_path = "analysis/chartify/function/chartify_predictions_results.csv"
pyopenssl_analysis_path = "analysis/pyopenssl/function/pyopenssl_predictions_results.csv"
arrow_analysis_path = "analysis/arrow/function/arrow_predictions_results.csv"
kedro_analysis_path = "analysis/kedro/function/kedro_predictions_results.csv"

kedro_class_level_analysis_path = "analysis/kedro/class/kedro_class_predictions_results.csv"
arrow_class_level_analysis_path = "analysis/arrow/class/arrow_predictions_class_results.csv"
pyopenssl_class_level_analysis_path = "analysis/pyopenssl/class/pyopenssl_predictions_class_results.csv"
chartify_class_level_analysis_path = "analysis/chartify/class/chartify_predictions_class_results.csv"

# Load the CSV files into DataFrames
df1 = pd.read_csv(kedro_class_level_analysis_path)
df2 = pd.read_csv(arrow_class_level_analysis_path)
df3 = pd.read_csv(pyopenssl_class_level_analysis_path)
df4 = pd.read_csv(chartify_class_level_analysis_path)

df1 = df1.replace({'-': 0})
df2 = df2.replace({'-': 0})
df3 = df3.replace({'-': 0})
df4 = df4.replace({'-': 0})
# Identify numeric columns
numeric_columns = df1.select_dtypes(include=np.number).columns.tolist()

# Convert the numeric columns in the DataFrames to numeric, replacing non-numeric values with NaN
for column in numeric_columns:
    df1[column] = pd.to_numeric(df1[column], errors='coerce')
    df2[column] = pd.to_numeric(df2[column], errors='coerce')
    df3[column] = pd.to_numeric(df3[column], errors='coerce')
    df4[column] = pd.to_numeric(df4[column], errors='coerce')

for df in [df1, df2, df3, df4]:
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].round(3)

# Ensure that all DataFrames have the same structure
assert df1.columns.equals(df2.columns) and df1.columns.equals(df3.columns) and df1.columns.equals(df4.columns)

# Add the numeric columns in the DataFrames together and divide by the number of CSV files
df_avg = df1.copy()
for column in numeric_columns:
    df_avg[column] = ((df1[column] + df2[column] + df3[column] + df4[column]) / 4).round(1)

# Save the resulting DataFrame to a new CSV file
df_avg.to_csv('average_class.csv', index=False)