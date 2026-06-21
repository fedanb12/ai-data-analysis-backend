import pandas as pd
import numpy as np
from scipy import stats

def load_dataframe(file_path: str, file_name: str) -> pd.DataFrame:
    ext = file_name.split('.')[-1].lower()
    if ext == 'csv':
        return pd.read_csv(file_path)
    elif ext in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    elif ext == 'json':
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def get_full_stats(df: pd.DataFrame) -> dict:
    stats_result = {
        "rowCount": len(df),
        "columnCount": len(df.columns),
        "columns": {}
    }

    for col in df.columns:
        col_data = df[col]
        missing = int(col_data.isna().sum())
        unique = int(col_data.nunique())

        col_stats = {
            "missing": missing,
            "unique": unique,
        }

        if pd.api.types.is_numeric_dtype(col_data):
            clean = col_data.dropna()
            col_stats["type"] = "numeric"
            col_stats["min"] = float(clean.min())
            col_stats["max"] = float(clean.max())
            col_stats["average"] = float(clean.mean())
            col_stats["sum"] = float(clean.sum())
            col_stats["median"] = float(clean.median())
            col_stats["std"] = float(clean.std())
            col_stats["skewness"] = float(clean.skew())
            col_stats["kurtosis"] = float(clean.kurtosis())
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            col_stats["type"] = "date"
        else:
            col_stats["type"] = "categorical"
            freq = col_data.value_counts().head(5).to_dict()
            col_stats["topValues"] = {str(k): int(v) for k, v in freq.items()}

        stats_result["columns"][col] = col_stats

    return stats_result

def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report = {
        "duplicatesRemoved": 0,
        "missingFilled": 0,
        "whitespaceFixed": 0,
        "totalRows": len(df),
    }

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    report["duplicatesRemoved"] = before - len(df)

    # Fix whitespace
    for col in df.select_dtypes(include='object').columns:
        fixed = df[col].str.strip()
        report["whitespaceFixed"] += int((fixed != df[col]).sum())
        df[col] = fixed

    # Fill missing values
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')
            report["missingFilled"] += missing

    return df, report

def get_correlation_matrix(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return {}
    corr = numeric_df.corr().round(3)
    return corr.to_dict()

def get_outliers(df: pd.DataFrame) -> dict:
    result = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        clean = df[col].dropna()
        z_scores = np.abs(stats.zscore(clean))
        outlier_count = int((z_scores > 3).sum())
        if outlier_count > 0:
            result[col] = {
                "count": outlier_count,
                "percentage": round(outlier_count / len(clean) * 100, 2)
            }
    return result

def run_statistical_tests(df: pd.DataFrame, col1: str, col2: str) -> dict:
    if col1 not in df.columns or col2 not in df.columns:
        return {"error": "Column not found"}

    a = df[col1].dropna()
    b = df[col2].dropna()

    if not pd.api.types.is_numeric_dtype(a) or not pd.api.types.is_numeric_dtype(b):
        return {"error": "Both columns must be numeric"}

    t_stat, p_value = stats.ttest_ind(a, b)
    correlation, corr_p = stats.pearsonr(a[:min(len(a), len(b))], b[:min(len(a), len(b))])

    return {
        "t_test": {
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_value), 4),
            "significant": bool(p_value < 0.05)
        },
        "correlation": {
            "pearson_r": round(float(correlation), 4),
            "p_value": round(float(corr_p), 4),
            "significant": bool(corr_p < 0.05)
        }
    }