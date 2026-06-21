import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = '') -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    data = df.groupby(x_col)[y_col].mean().sort_values(ascending=False).head(20)
    ax.bar(data.index.astype(str), data.values, color='#4f46e5')
    ax.set_title(title or f'{y_col} by {x_col}', fontsize=14, fontweight='bold')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig_to_base64(fig)

def line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = '') -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    sorted_df = df.sort_values(x_col)
    ax.plot(
        sorted_df[x_col].astype(str),
        sorted_df[y_col],
        color='#4f46e5',
        linewidth=2,
        marker='o',
        markersize=4
    )
    ax.set_title(title or f'{y_col} over {x_col}', fontsize=14, fontweight='bold')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig_to_base64(fig)

def scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = '') -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(df[x_col], df[y_col], color='#4f46e5', alpha=0.6, s=30)
    ax.set_title(title or f'{x_col} vs {y_col}', fontsize=14, fontweight='bold')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    plt.tight_layout()
    return fig_to_base64(fig)

def histogram(df: pd.DataFrame, col: str, title: str = '') -> str:
    if not pd.api.types.is_numeric_dtype(df[col]):
        raise ValueError(f"Column '{col}' is not numeric. Histogram requires a numeric column.")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df[col].dropna(), bins=30, color='#4f46e5', edgecolor='white')
    ax.set_title(title or f'Distribution of {col}', fontsize=14, fontweight='bold')
    ax.set_xlabel(col)
    ax.set_ylabel('Frequency')
    plt.tight_layout()
    return fig_to_base64(fig)

def pie_chart(df: pd.DataFrame, col: str, title: str = '') -> str:
    fig, ax = plt.subplots(figsize=(8, 8))
    counts = df[col].value_counts().head(8)
    colors = ['#4f46e5', '#059669', '#d97706', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#14b8a6']
    ax.pie(
        counts.values,
        labels=counts.index.astype(str),
        autopct='%1.1f%%',
        colors=colors[:len(counts)],
        startangle=90
    )
    ax.set_title(title or f'Distribution of {col}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig_to_base64(fig)

def correlation_heatmap(df: pd.DataFrame) -> str:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return None

    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(im)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr.columns)

    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f'{corr.values[i, j]:.2f}',
                   ha='center', va='center', fontsize=8,
                   color='white' if abs(corr.values[i, j]) > 0.5 else 'black')

    ax.set_title('Correlation Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig_to_base64(fig)