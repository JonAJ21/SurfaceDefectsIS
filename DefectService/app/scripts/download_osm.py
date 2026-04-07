import argparse
import requests
from pathlib import Path


def download_osm(region: str, output_dir: str = "/tmp"):
    
    # Список доступных регионов
    regions = {
        "moscow_oblast": "https://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf",
        "small": "https://download.geofabrik.de/europe/isle-of-man-latest.osm.pbf",
    }
    
    if region not in regions:
        print(f"Unknown region. Available: {list(regions.keys())}")
        return None
    
    url = regions[region]
    output_file = Path(output_dir) / f"{region}.osm.pbf"
    
    print(f"Downloading {region} from {url}")
    print(f"Output: {output_file}")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_file, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                percent = (downloaded / total_size) * 100
                print(f"\rProgress: {percent:.1f}%", end="")
    
    print(f"\nownloaded to {output_file}")
    return str(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download OSM data")
    parser.add_argument("--region", choices=["moscow", "spb", "moscow_oblast", "small"], 
                       help="Region to download")
    parser.add_argument("--output", "-o", default="/tmp", help="Output directory")
    
    args = parser.parse_args()
    download_osm(args.region, args.output)