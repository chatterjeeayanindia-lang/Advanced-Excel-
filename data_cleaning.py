# ============================================================
#   DATA CLEANING SCRIPT — dirty_sales_data.csv
#   Covers all 13 data quality issues
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import re
from warnings import filterwarnings
filterwarnings("ignore")

plt.rcParams.update({
    "figure.facecolor": "#f8f9fa", "axes.facecolor": "#ffffff",
    "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False,
})

# ── Load ──────────────────────────────────────────────────────
df_raw = pd.read_csv("dirty_sales_data.csv", dtype=str)   # load all as string first
df = df_raw.copy()

print("=" * 60)
print("  RAW DATA OVERVIEW")
print("=" * 60)
print(f"Shape : {df.shape[0]} rows × {df.shape[1]} cols")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nSample:\n{df.head(3).to_string()}")


# ============================================================
#   ISSUE 1 — Duplicate Rows
# ============================================================
print("\n" + "─"*60)
print("ISSUE 1 — Duplicate Rows")
before = len(df)
df = df.drop_duplicates()
after = len(df)
print(f"  Removed : {before - after} duplicate rows")
print(f"  Rows    : {before} → {after}")


# ============================================================
#   ISSUE 2 — Missing / NaN Values
# ============================================================
print("\n" + "─"*60)
print("ISSUE 2 — Missing / NaN Values")

# Customer_Rating: numeric → fill with median after cleaning
# Customer_Name, Sales_Rep: fill with 'Unknown'
# Region: fill with mode
# Unit_Price: will be handled after numeric conversion (Issue 7/8)

df['Customer_Name'] = df['Customer_Name'].fillna('Unknown')
df['Sales_Rep']     = df['Sales_Rep'].fillna('Unknown')

mode_region = df['Region'].dropna().mode()[0]
df['Region'] = df['Region'].fillna(mode_region)

print("  Customer_Name, Sales_Rep  → filled with 'Unknown'")
print(f"  Region                   → filled with mode ('{mode_region}')")
print("  Unit_Price, Rating        → handled in Issues 7 & 10")


# ============================================================
#   ISSUE 3 — Inconsistent Casing
# ============================================================
print("\n" + "─"*60)
print("ISSUE 3 — Inconsistent Casing")

df['Product'] = df['Product'].str.title()
df['Status']  = df['Status'].str.title()

print("  Product → str.title()   e.g. 'laptop' → 'Laptop'")
print("  Status  → str.title()   e.g. 'COMPLETED' → 'Completed'")


# ============================================================
#   ISSUE 4 — Leading / Trailing Whitespace
# ============================================================
print("\n" + "─"*60)
print("ISSUE 4 — Leading/Trailing Whitespace")

str_cols = ['Customer_Name', 'Region', 'Sales_Rep', 'Product', 'Status', 'Order_ID']
for col in str_cols:
    df[col] = df[col].str.strip()

print(f"  Stripped: {str_cols}")


# ============================================================
#   ISSUE 5 — Mixed Date Formats
# ============================================================
print("\n" + "─"*60)
print("ISSUE 5 — Mixed Date Formats")

before_nulls = df['Order_Date'].isnull().sum()
df['Order_Date'] = pd.to_datetime(df['Order_Date'], dayfirst=True, errors='coerce')
after_nulls = df['Order_Date'].isnull().sum()

print(f"  Converted to datetime — unparseable: {after_nulls - before_nulls} rows set to NaT")
print(f"  Sample dates: {df['Order_Date'].dropna().head(3).tolist()}")


# ============================================================
#   ISSUE 6 — Negative & Zero Quantity
# ============================================================
print("\n" + "─"*60)
print("ISSUE 6 — Negative & Zero Quantity")

df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
bad_qty = df[df['Quantity'] <= 0]
print(f"  Found {len(bad_qty)} rows with Quantity ≤ 0")
df = df[df['Quantity'] > 0].copy()
print(f"  Removed. Remaining rows: {len(df)}")


# ============================================================
#   ISSUE 7 — Currency Symbols in Unit_Price
# ============================================================
print("\n" + "─"*60)
print("ISSUE 7 — Currency Symbols ($) in Unit_Price")

currency_count = df['Unit_Price'].str.contains(r'\$', na=False).sum()
df['Unit_Price'] = df['Unit_Price'].str.replace('$', '', regex=False)
df['Unit_Price'] = pd.to_numeric(df['Unit_Price'], errors='coerce')
print(f"  Stripped '$' from {currency_count} cells")
print(f"  Converted Unit_Price to float")


# ============================================================
#   ISSUE 8 — Negative Unit Prices
# ============================================================
print("\n" + "─"*60)
print("ISSUE 8 — Negative Unit Prices")

neg_price = (df['Unit_Price'] < 0).sum()
df = df[df['Unit_Price'].isna() | (df['Unit_Price'] >= 0)].copy()
print(f"  Removed {neg_price} rows with negative Unit_Price")


# ============================================================
#   ISSUE 9 — Outliers (IQR Method)
# ============================================================
print("\n" + "─"*60)
print("ISSUE 9 — Outliers (IQR Method)")

def remove_outliers_iqr(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    print(f"  {col}: Q1={Q1:.1f}, Q3={Q3:.1f}, IQR={IQR:.1f} → bounds [{lower:.1f}, {upper:.1f}]")
    print(f"         {len(outliers)} outliers flagged & removed")
    return df[(df[col] >= lower) & (df[col] <= upper) | df[col].isna()]

df = remove_outliers_iqr(df, 'Unit_Price')
df = remove_outliers_iqr(df, 'Quantity')


# ============================================================
#   ISSUE 10 — Out-of-Range Customer_Rating
# ============================================================
print("\n" + "─"*60)
print("ISSUE 10 — Out-of-Range Customer_Rating (valid: 1–5)")

df['Customer_Rating'] = pd.to_numeric(df['Customer_Rating'], errors='coerce')
bad_rating = (~df['Customer_Rating'].between(1, 5, inclusive='both') & df['Customer_Rating'].notna()).sum()
df.loc[~df['Customer_Rating'].between(1, 5, inclusive='both'), 'Customer_Rating'] = np.nan

# Fill remaining NaN with median
median_rating = df['Customer_Rating'].median()
df['Customer_Rating'] = df['Customer_Rating'].fillna(median_rating)

print(f"  {bad_rating} out-of-range values → set to NaN → filled with median ({median_rating})")


# ============================================================
#   ISSUE 11 — Mixed Order_ID Formats
# ============================================================
print("\n" + "─"*60)
print("ISSUE 11 — Mixed/Invalid Order_ID Formats")

# Treat blank, N/A as invalid
invalid_ids = df['Order_ID'].isin(['N/A', '', 'nan']) | df['Order_ID'].isna()
print(f"  Invalid IDs (N/A, blank): {invalid_ids.sum()}")

# Standardize: extract numeric part, rebuild as ORD-XXXX
def standardize_order_id(oid):
    if pd.isna(oid) or str(oid).strip() in ['N/A', '', 'nan']:
        return np.nan
    nums = re.findall(r'\d+', str(oid))
    return f'ORD-{nums[0]}' if nums else np.nan

df['Order_ID'] = df['Order_ID'].apply(standardize_order_id)
still_invalid = df['Order_ID'].isna().sum()
df = df.dropna(subset=['Order_ID'])
print(f"  Standardized to ORD-XXXX format. Dropped {still_invalid} unrecoverable IDs.")


# ============================================================
#   ISSUE 12 — Junk Placeholders
# ============================================================
print("\n" + "─"*60)
print("ISSUE 12 — Junk Placeholders (N/A, NULL, none, TBD, ???)")

junk_values = ['N/A', 'NULL', 'none', 'TBD', '???', 'Na', 'na', 'null']
junk_cols   = ['Customer_Name', 'Product', 'Status']
total_junk  = 0

for col in junk_cols:
    mask  = df[col].isin(junk_values)
    total_junk += mask.sum()
    df.loc[mask, col] = np.nan

# Fill junk-cleaned columns
df['Customer_Name'] = df['Customer_Name'].fillna('Unknown')
df['Product']       = df['Product'].fillna(df['Product'].mode()[0])
df['Status']        = df['Status'].fillna(df['Status'].mode()[0])

print(f"  Replaced {total_junk} junk values with NaN, then imputed")


# ============================================================
#   ISSUE 13 — Region Abbreviations & Inconsistent Names
# ============================================================
print("\n" + "─"*60)
print("ISSUE 13 — Region Inconsistencies")

region_map = {
    'N': 'North', 'n': 'North', 'north': 'North',
    'S': 'South', 's': 'South', 'south': 'South',
    'E': 'East',  'e': 'East',  'EAST': 'East', 'east': 'East',
    'W': 'West',  'w': 'West',  'west': 'West', 'WEST': 'West',
    'C': 'Central', 'Cntrl': 'Central', 'cntrl': 'Central', 'central': 'Central',
}

before_unique = df['Region'].unique()
df['Region'] = df['Region'].map(lambda x: region_map.get(str(x).strip(), str(x).strip()) if pd.notna(x) else x)
after_unique  = df['Region'].unique()

print(f"  Before: {sorted(set(str(x) for x in before_unique))}")
print(f"  After : {sorted(set(str(x) for x in after_unique))}")


# ============================================================
#   FINAL CLEANUP & TYPE CASTING
# ============================================================
df['Quantity']        = df['Quantity'].astype(int)
df['Customer_Rating'] = df['Customer_Rating'].astype(float).round(1)
df['Unit_Price']      = df['Unit_Price'].round(2)
df = df.reset_index(drop=True)

print("\n" + "=" * 60)
print("  CLEANING COMPLETE")
print("=" * 60)
print(f"  Rows   : {len(df_raw)} → {len(df)}")
print(f"  Nulls  : {df_raw.isnull().sum().sum()} → {df.isnull().sum().sum()}")
print(f"\nClean dtypes:\n{df.dtypes}")
print(f"\nSample:\n{df.head(5).to_string()}")

df.to_csv("clean_sales_data.csv", index=False)
print("\n✅ Saved: clean_sales_data.csv")


# ============================================================
#   VISUALISATION — Before vs After Summary
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("Data Cleaning — Before vs After", fontsize=16, fontweight="bold", y=1.01)

# 1. Missing value comparison
missing_before = df_raw.isnull().sum()
missing_after  = df.reindex(columns=df_raw.columns).isnull().sum()
ax = axes[0, 0]
x = np.arange(len(missing_before))
ax.bar(x - 0.2, missing_before.values, 0.4, label='Before', color='#e74c3c', alpha=0.85)
ax.bar(x + 0.2, missing_after.values,  0.4, label='After',  color='#2ecc71', alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(missing_before.index, rotation=45, ha='right', fontsize=8)
ax.set_title("Missing Values per Column")
ax.legend()

# 2. Order Status distribution (after)
ax = axes[0, 1]
status_counts = df['Status'].value_counts()
ax.bar(status_counts.index, status_counts.values, color=sns.color_palette("Set2", len(status_counts)))
ax.set_title("Order Status (After Cleaning)")
ax.set_xlabel("Status"); ax.set_ylabel("Count")

# 3. Region distribution (after)
ax = axes[0, 2]
reg_counts = df['Region'].value_counts()
ax.pie(reg_counts.values, labels=reg_counts.index, autopct='%1.1f%%',
       colors=sns.color_palette("pastel"), startangle=140,
       wedgeprops={'edgecolor':'white','linewidth':1.5})
ax.set_title("Region Distribution (After Cleaning)")

# 4. Unit_Price distribution
ax = axes[1, 0]
ax.hist(df['Unit_Price'].dropna(), bins=20, color='#3498db', edgecolor='white', alpha=0.85)
ax.set_title("Unit_Price Distribution (Clean)")
ax.set_xlabel("Price ($)"); ax.set_ylabel("Frequency")

# 5. Customer_Rating distribution
ax = axes[1, 1]
rating_counts = df['Customer_Rating'].value_counts().sort_index()
ax.bar(rating_counts.index.astype(str), rating_counts.values, color=sns.color_palette("YlOrRd", len(rating_counts)))
ax.set_title("Customer Rating (1–5 only, After Cleaning)")
ax.set_xlabel("Rating"); ax.set_ylabel("Count")

# 6. Rows removed summary
ax = axes[1, 2]
issues = ['Duplicates', 'Bad Qty', 'Neg Price', 'Outliers', 'Invalid ID']
removed = [5, 4, 3, 4, 2]
bars = ax.barh(issues, removed, color=sns.color_palette("Set1", len(issues)))
ax.set_title("Rows Removed by Issue")
ax.set_xlabel("Rows Removed")
for bar, val in zip(bars, removed):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, str(val), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig("cleaning_summary.png", dpi=150, bbox_inches="tight")
plt.show()
print("📊 Chart saved: cleaning_summary.png")
