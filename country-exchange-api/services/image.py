import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")
TEMP_PLOT = os.path.join(CACHE_DIR, "temp_plot.png")

def generate_summary_image(total: int, top5: list, timestamp: datetime):
    plt.figure(figsize=(10, 7))
    names = [c.name[:15] for c in top5]
    gdps = [c.estimated_gdp / 1e9 if c.estimated_gdp else 0 for c in top5]

    bars = plt.bar(names, gdps, color='#4CAF50')
    plt.title("Top 5 Countries by Estimated GDP (Billions USD)", fontsize=14, pad=20)
    plt.ylabel("GDP (B)")
    plt.xticks(rotation=45, ha='right')

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(gdps)*0.01,
                 f'{height:.1f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(TEMP_PLOT, dpi=200, bbox_inches='tight')  # ← FIXED
    plt.close()

    img = Image.open(TEMP_PLOT)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = small_font = ImageFont.load_default()

    draw.text((10, 10), f"Total Countries: {total}", fill="black", font=font)
    draw.text((10, 35), f"Refreshed: {timestamp.strftime('%Y-%m-%d %H:%M:%SZ')}", fill="gray", font=small_font)

    img.save(IMAGE_PATH)
    os.remove(TEMP_PLOT)  # ← Remove temp file