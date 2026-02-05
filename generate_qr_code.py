#!/usr/bin/env python3
"""
QR-Code Generator für Bewerbungsunterlagen
Generiert QR-Code aus Website-URL für Integration ins Anschreiben

Autor: Marcus Moser
Datum: 05.02.2026
"""

import qrcode
from pathlib import Path
from PIL import Image


def generate_qr_code(url: str, output_path: Path, size_cm: float = 2.5, dpi: int = 300) -> Path:
    """
    Generiert einen QR-Code aus einer URL mit exakter Größe.
    
    Args:
        url: Die URL, die im QR-Code kodiert werden soll
        output_path: Pfad für die Ausgabedatei
        size_cm: Gewünschte Größe in Zentimetern (Standard: 2.5cm)
        dpi: Auflösung in DPI (Standard: 300 für Druckqualität)
    
    Returns:
        Path: Pfad zur erstellten QR-Code-Datei
    """
    # Berechne Pixel-Größe: 1 inch = 2.54 cm
    # size_px = (size_cm / 2.54) * dpi
    size_px = int((size_cm / 2.54) * dpi)
    
    # QR-Code erstellen
    qr = qrcode.QRCode(
        version=1,  # Automatische Größenanpassung
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% Fehlerkorrektur
        box_size=10,  # Größe jedes "Boxes" im QR-Code
        border=2,  # Rand um den QR-Code (mindestens 4 für Standards)
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Bild erstellen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Auf exakte Größe skalieren
    img = img.resize((size_px, size_px), Image.Resampling.LANCZOS)
    
    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, dpi=(dpi, dpi))
    
    print(f"✅ QR-Code erstellt: {output_path}")
    print(f"   URL: {url}")
    print(f"   Größe: {size_cm}cm x {size_cm}cm ({size_px}px x {size_px}px @ {dpi}dpi)")
    
    return output_path


def main():
    """Standalone-Ausführung für Tests"""
    from data.persoenliche_daten import PERSOENLICHE_DATEN
    
    # Website-URL aus persönlichen Daten
    website_url = PERSOENLICHE_DATEN.get('website', '')
    
    if not website_url:
        print("❌ Fehler: Keine Website-URL in persoenliche_daten.py gefunden!")
        return
    
    # Output-Pfad
    output_path = Path(__file__).parent / 'images' / 'qr_code.png'
    
    # QR-Code generieren
    generate_qr_code(website_url, output_path, size_cm=2.5)
    print(f"\n💡 QR-Code kann nun in Bewerbungen verwendet werden.")


if __name__ == '__main__':
    main()
