import zipfile
import pandas as pd
import requests
from pathlib import Path
import xml.etree.ElementTree as ET

RAW_DIR = Path("data/raw")
CLEANED_DIR = Path("data/cleaned")

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url, path):
    response = requests.get(url)
    with open(path, "wb") as f:
        f.write(response.content)
        print(f"Downloaded {path}")


def parse_osm(path):
    tree = ET.parse(path)
    root = tree.getroot()
    nodes = []
    for node in root.findall("node"):
        nodes.append(
            {
                "id": node.attrib.get("id"),
                "lat": node.attrib.get("lat"),
                "lon": node.attrib.get("lon"),
            }
        )
    df = pd.DataFrame(nodes)
    return df


def exctract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Extracted: {zip_path} to {extract_to}")


def load_and_clean_csv(file_path):
    df = pd.read_csv(file_path)
    df.dropna(how="all", inplace=True)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


def main():
    # Project Gutenberg
    gutenberg_url = "https://www.gutenberg.org/cache/epub/84/pg84.txt"
    gutenberg_path = RAW_DIR / "frankstein.txt"
    download_file(gutenberg_url, gutenberg_path)
    with open(gutenberg_path, "r", encoding="utf-8") as f:
        text = f.read()
    with open(CLEANED_DIR / "frankstein_cleaned.txt", "w", encoding="utf-8") as f:
        f.write(text.strip())
        print("Saved cleand Gutenberg project")

    # Kaggle datasets
    kaggle_url = "https://www.kaggle.com/api/v1/datasets/download/jayaantanaath/student-habits-vs-academic-performance"
    zip_path = RAW_DIR / "archive.zip"
    zip_dir = RAW_DIR / "extracted"
    download_file(kaggle_url, zip_path)
    exctract_zip(zip_path, zip_dir)
    csv_file = list(zip_dir.glob("*.csv"))
    if not csv_file:
        raise FileNotFoundError("No CSV files found in the extracted directory")
    csv_file = csv_file[0]
    kaggle_df = load_and_clean_csv(csv_file)
    kaggle_df.to_parquet(CLEANED_DIR / "student_habits_performance.parquet")
    print("Saved cleaned Kaggle dataset")

    # Open Street Map data
    osm_url = "https://api.openstreetmap.org/api/0.6/map?bbox=11.54,48.14,11.543,48.145"
    osm_path = RAW_DIR / "munich.osm"
    download_file(osm_url, osm_path)
    osem_df = parse_osm(osm_path)
    osem_df.to_parquet(CLEANED_DIR / "osem_nodes.parquet")
    print("Saved parsed OSM node data")


if __name__ == "__main__":
    main()
