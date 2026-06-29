import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "scraped"
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Downloading BrightData/Booking.com-Listings from Hugging Face...")
try:
    from datasets import load_dataset

    ds = load_dataset("BrightData/Booking.com-Listings", split="train", trust_remote_code=True)
    print(f"Dataset loaded: {len(ds)} rows")

    df = ds.to_pandas()
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string())

    output_path = DATA_DIR / "brightdata_booking_listings.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")
    print(f"Shape: {df.shape}")

except Exception as e:
    print(f"Error loading from HuggingFace: {e}")
    print("\nTrying direct CSV download...")

    import requests
    url = "https://huggingface.co/datasets/BrightData/Booking.com-Listings/resolve/main/booking_listings.csv"
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
        output_path = DATA_DIR / "brightdata_booking_listings.csv"
        df.to_csv(output_path, index=False)
        print(f"Downloaded and saved: {output_path}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e2:
        print(f"Direct download also failed: {e2}")
