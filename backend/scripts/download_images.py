import json
import urllib.request
import os
import sys

def download_images():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    products_file = os.path.join(base_dir, "data", "products.json")
    target_dir = os.path.join(os.path.dirname(base_dir), "frontend", "public", "images", "products")
    
    os.makedirs(target_dir, exist_ok=True)
    
    with open(products_file, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    updated_products = []
    
    for p in products:
        pid = p["product_id"]
        url = p.get("image_url", "")
        dest = os.path.join(target_dir, f"{pid}.jpg")
        print(f"Processing {pid}...")
        
        success = False
        if url.startswith("http"):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp, open(dest, "wb") as out_file:
                    out_file.write(resp.read())
                size = os.path.getsize(dest)
                print(f"  [OK] Saved {pid}.jpg ({size} bytes)")
                success = True
            except Exception as e:
                print(f"  [FAIL] Could not download from {url}: {e}")
        
        # If download failed, try fallback reliable Unsplash image for the category
        if not success or os.path.getsize(dest) == 0:
            fallback_urls = {
                "Shirts": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80",
                "T-Shirts": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
                "Pants": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=600&q=80",
                "Dresses": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=600&q=80",
                "Outerwear": "https://images.unsplash.com/photo-1544923246-77307dd654cb?auto=format&fit=crop&w=600&q=80",
                "Shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
            }
            fallback_url = fallback_urls.get(p.get("category", "Shirts"), "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80")
            try:
                req = urllib.request.Request(fallback_url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp, open(dest, "wb") as out_file:
                    out_file.write(resp.read())
                print(f"  [FALLBACK-OK] Saved fallback for {pid}.jpg")
                success = True
            except Exception as e2:
                print(f"  [CRITICAL-FAIL] {pid} fallback failed: {e2}")

        # Update product image_url to local path with fallback
        # e.g. /images/products/P002.jpg
        p["image_url"] = f"/images/products/{pid}.jpg"
        p["external_image_url"] = url
        updated_products.append(p)
        
    with open(products_file, "w", encoding="utf-8") as f:
        json.dump(updated_products, f, indent=2)
    print("\nSuccessfully updated products.json with local image paths!")

if __name__ == "__main__":
    download_images()

