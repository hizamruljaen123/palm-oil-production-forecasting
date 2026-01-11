import os
from pathlib import Path
from app import app

print("Testing UPLOAD_FOLDER configuration...")

upload_folder = app.config['UPLOAD_FOLDER']
print(f"Configured UPLOAD_FOLDER: {upload_folder}")

if os.path.exists(upload_folder):
    print("✅ Directory exists.")
    
    # Simulate the logic in the route
    files = []
    data_path = Path(upload_folder)
    print(f"\nListing files in {data_path}:")
    for file in data_path.glob("*.csv"):
        print(f" - Found: {file.name}")
        files.append(file.name)
        
    if len(files) > 0:
        print(f"\n✅ Successfully found {len(files)} CSV files.")
    else:
        print("\n⚠️ Directory exists but no CSV files found.")
else:
    print("❌ Directory does NOT exist.")
    print(f"Expected at: {os.path.abspath(upload_folder)}")
