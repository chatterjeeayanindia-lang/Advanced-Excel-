# 🧹 Data Cleaning Project — Python (Pandas)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange)
![Seaborn](https://img.shields.io/badge/Seaborn-Visualization-teal)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> A hands-on data cleaning project that identifies and fixes **13 real-world data quality issues** in a sales dataset using Python and Pandas — covering duplicates, missing values, inconsistent formats, outliers, junk placeholders, and more.

---

## 📁 Project Structure

```
data-cleaning-project/
│
├── dirty_sales_data.csv      # Raw dataset with all 13 issues injected
├── data_cleaning.py          # Full cleaning script (all 13 fixes)
├── clean_sales_data.csv      # Final cleaned output
├── cleaning_summary.png      # Before vs After visualisation chart
└── README.md                 # Project documentation
```

---

## 🗂️ Dataset Overview

| Column | Data Type | Description |
|---|---|---|
| `Order_ID` | String | Unique order identifier |
| `Customer_Name` | String | Name of the customer |
| `Region` | String | Geographic sales region |
| `Product` | String | Product name |
| `Status` | String | Order status |
| `Quantity` | Integer | Units ordered |
| `Unit_Price` | Float | Price per unit |
| `Customer_Rating` | Float | Customer rating (valid: 1–5) |
| `Sales_Rep` | String | Assigned sales representative |
| `Order_Date` | Date | Date order was placed |

---

## 🐛 13 Data Quality Issues — What Was Fixed

| # | Column(s) | Issue | Fix Applied |
|---|---|---|---|
| 1 | All | **Duplicate rows** (5 rows) | `drop_duplicates()` |
| 2 | Customer_Name, Region, Unit_Price, Customer_Rating, Sales_Rep | **Missing / NaN values** | `fillna()` with mode / median / 'Unknown' |
| 3 | Product, Status | **Inconsistent casing** ('laptop' vs 'Laptop') | `str.title()` |
| 4 | Customer_Name, Region, Sales_Rep | **Leading/trailing whitespace** | `str.strip()` |
| 5 | Order_Date | **Mixed date formats** (6 different formats) | `pd.to_datetime(dayfirst=True)` |
| 6 | Quantity | **Negative & zero values** | Boolean mask filter (keep > 0) |
| 7 | Unit_Price | **Currency symbols** ('$999.99' as string) | `str.replace('$','')` + `pd.to_numeric()` |
| 8 | Unit_Price | **Negative unit prices** | Filter rows where price < 0 |
| 9 | Unit_Price, Quantity | **Outliers** (99999, 9999) | IQR method (1.5 × IQR rule) |
| 10 | Customer_Rating | **Out-of-range values** (0, 6, 10, 99, -1) | Set invalid → NaN → fill with median |
| 11 | Order_ID | **Mixed formats & invalid IDs** ('ord1001', 'ORD_1001', 'N/A') | Regex extract + rebuild as `ORD-XXXX` |
| 12 | Customer_Name, Product, Status | **Junk placeholders** (N/A, NULL, none, TBD, ???) | `.isin()` → replace with NaN → impute |
| 13 | Region | **Abbreviations & inconsistent names** ('N' vs 'North', 'west' vs 'West') | Mapping dictionary |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/data-cleaning-project.git
cd data-cleaning-project
```

### 2. Install dependencies
```bash
pip install pandas numpy matplotlib seaborn
```

### 3. Run the cleaning script
```bash
python data_cleaning.py
```

Or open in **Jupyter Lab**:
```bash
jupyter lab
```

---

## 🔍 Key Cleaning Techniques Used

### Removing Duplicates
```python
df = df.drop_duplicates()
```

### Handling Missing Values
```python
df['Customer_Name'] = df['Customer_Name'].fillna('Unknown')
df['Region']        = df['Region'].fillna(df['Region'].mode()[0])
df['Customer_Rating'] = df['Customer_Rating'].fillna(df['Customer_Rating'].median())
```

### Fixing Mixed Date Formats
```python
df['Order_Date'] = pd.to_datetime(df['Order_Date'], dayfirst=True, errors='coerce')
```

### Stripping Currency Symbols
```python
df['Unit_Price'] = df['Unit_Price'].str.replace('$', '', regex=False)
df['Unit_Price'] = pd.to_numeric(df['Unit_Price'], errors='coerce')
```

### Detecting Outliers (IQR Method)
```python
Q1, Q3 = df['Unit_Price'].quantile(0.25), df['Unit_Price'].quantile(0.75)
IQR    = Q3 - Q1
df     = df[(df['Unit_Price'] >= Q1 - 1.5*IQR) & (df['Unit_Price'] <= Q3 + 1.5*IQR)]
```

### Standardizing Order IDs with Regex
```python
import re
def standardize_order_id(oid):
    nums = re.findall(r'\d+', str(oid))
    return f'ORD-{nums[0]}' if nums else np.nan

df['Order_ID'] = df['Order_ID'].apply(standardize_order_id)
```

### Fixing Region Names with Mapping
```python
region_map = {
    'N': 'North', 'south': 'South', 'EAST': 'East',
    'west': 'West', 'Cntrl': 'Central'
}
df['Region'] = df['Region'].map(lambda x: region_map.get(x, x))
```

---

## 📊 Results — Before vs After

| Metric | Before | After |
|---|---|---|
| Total Rows | 100 | 85 |
| Duplicate Rows | 5 | 0 |
| Missing Values | 30 | 0 |
| Invalid Ratings | 5 | 0 |
| Outliers | 4 | 0 |
| Region Variants | 10 | 5 (standardized) |
| Date Format Variants | 6 | 1 (datetime) |

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|---|---|
| **Python 3.12** | Core scripting language |
| **Pandas** | Data manipulation and cleaning |
| **NumPy** | Numerical operations and NaN handling |
| **Matplotlib** | Before vs After visualisation |
| **Seaborn** | Chart styling |
| **Jupyter Lab** | Interactive development |
| **Regex (`re`)** | Order ID standardization |

---

## 🚀 Future Improvements

- [ ] Add SQL equivalents for every cleaning step
- [ ] Add Power Query (Power BI) steps for each issue
- [ ] Build an automated data quality report (HTML output)
- [ ] Add unit tests using `pytest` to validate cleaning functions
- [ ] Extend to handle Excel files (`.xlsx`) with `openpyxl`

---

## 👤 Author

**Ayan**
- 📍 Data Analytics Student
- 🔗 [GitHub](https://github.com/chatterjeeayanindia-lang)
- 💼 [LinkedIn](linkedin.com/in/ayan-chatterjee-80240b214)

---

## 📄 License

This project is for educational and portfolio purposes.

---

> *"Dirty data is the norm, not the exception — cleaning it is the most important skill in data analytics."*
