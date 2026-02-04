#!/usr/bin/env python3
"""
Optimiert das Profilbild für die Bewerbungsunterlagen
"""
from PIL import Image
import os

# Pfade
input_image = "images/_S3A4489_3.jpeg"
output_image = "images/profilbild.jpg"

# Bild laden
img = Image.open(input_image)
print(f"Original: {img.size} - {img.format}")

# Auf quadratisches Format zuschneiden (Gesicht zentriert)
width, height = img.size
# Nimm den kürzeren Wert als Basis für den Zuschnitt
size = min(width, height)

# Zentrierter Zuschnitt
left = (width - size) // 2
top = (height - size) // 2
right = left + size
bottom = top + size

img_cropped = img.crop((left, top, right, bottom))
print(f"Zugeschnitten: {img_cropped.size}")

# Auf optimale Größe skalieren (400x400 für gute Qualität)
img_resized = img_cropped.resize((400, 400), Image.Resampling.LANCZOS)
print(f"Skaliert: {img_resized.size}")

# Speichern mit guter Qualität
img_resized.save(output_image, "JPEG", quality=95, optimize=True)
print(f"✅ Optimiertes Bild gespeichert: {output_image}")

# Dateigröße ausgeben
size_kb = os.path.getsize(output_image) / 1024
print(f"Dateigröße: {size_kb:.1f} KB")
