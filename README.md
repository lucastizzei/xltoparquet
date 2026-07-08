# Excel to Parquet Converter

## 📌 Purpose
Converts monthly ZyLAB Excel exports into an optimized Parquet dataset.

## Features
- Preserves identifiers as strings
- Converts structured fields to categories
- Removes unnecessary columns
- Standardizes dates
- Uses ZSTD compression
- Produces reusable analytical datasets

## Future enhancements I would put in Issues
>High priority
Add file size reporting
Add duplicate ID detection
Add required column validation
Add logging

>Nice to have
Convert any Excel file passed as argument
GUI drag-and-drop interface
Batch folder processing
Automatic benchmarking (Excel size vs Parquet size)

## 🚀 How to Run This Project

### ⚠️IMPORTANT: 0. Open the Project Folder in VS Code

### 1. Activate virtual environment
Windows:
    .venv\Scripts\activate
Linux/Mac:
    source .venv/bin/activate

### 2. Install dependencies
pip install -r requirements.txt

### 3. Run the main script
python src/main.py

# QUICK ACTIONS (coperino pasterino)
## Everytime:
.venv\Scripts\activate          #Should run automaticallwhen Project folder is openned (.vscode\settings.json)
python src\main.py              #Copy paste to run the code

## First time run:
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt    # if any present

## When new package is added:
⚠️ CHECH VENV (.venv\Scripts\activate)
python -m pip install <package_name>
python -m pip freeze > requirements.txt

## 📝 Author
Lucas Tizzei Vidotto
