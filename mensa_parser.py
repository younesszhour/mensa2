import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import re

# Konfiguration
MENSA_URL = "https://www.studierendenwerk-kassel.de/speiseplaene/zentralmensa-arnold-bode-strasse"
OUTPUT_DIR = "." # Bilder direkt ins Root oder Unterordner
FONT_PATH = "Futura.ttc" 
FONT_SIZE_HEADLINE = 30
FONT_SIZE_TEXT = 24
IMG_WIDTH = 600
IMG_HEIGHT = 800

DAYS_MAPPING = {
    "Montag": "montag.png",
    "Dienstag": "dienstag.png",
    "Mittwoch": "mittwoch.png",
    "Donnerstag": "donnerstag.png",
    "Freitag": "freitag.png",
    "Samstag": "samstag.png"
}

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except IOError:
        # Fallback auf Standard, falls Futura fehlt
        return ImageFont.load_default()

def create_image(day_name, dishes, filename):
    img = Image.new('L', (IMG_WIDTH, IMG_HEIGHT), 255) # Weißer Hintergrund
    draw = ImageDraw.Draw(img)
    
    font_head = get_font(FONT_SIZE_HEADLINE)
    font_text = get_font(FONT_SIZE_TEXT)

    # Header
    draw.text((20, 20), f"Mensa: {day_name}", font=font_head, fill=0)
    
    y_pos = 80
    if not dishes:
        draw.text((20, y_pos), "Keine Daten / Geschlossen", font=font_text, fill=0)
    else:
        for dish in dishes:
            # Kategorie fett simulieren (durch Großbuchstaben oder Einrückung)
            cat_text = f"[{dish['category']}]"
            draw.text((20, y_pos), cat_text, font=font_text, fill=0)
            y_pos += 30
            
            # Gerichtstext umbrechen
            full_text = dish['meal']
            if dish['price']:
                full_text += f" ({dish['price']})"
            
            # Sehr einfaches Word-Wrapping
            words = full_text.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                # Breite schätzen (ca 12px pro char bei size 24)
                if len(test_line) * 12 < (IMG_WIDTH - 40):
                    line = test_line
                else:
                    draw.text((40, y_pos), line, font=font_text, fill=0)
                    y_pos += 30
                    line = word + " "
            draw.text((40, y_pos), line, font=font_text, fill=0)
            y_pos += 45 
            
            if y_pos > IMG_HEIGHT - 50:
                break 

    img.save(filename)
    print(f"Erstellt: {filename}")

def main():
    print("Rufe Mensa-Daten ab...")
    try:
        response = requests.get(MENSA_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Fehler: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    week_data = {k: [] for k in DAYS_MAPPING.keys()}

    # Spezifische Logik für Studierendenwerk Kassel (Accordion Struktur)
    accordions = soup.select(".accordion__item")
    
    if not accordions:
        print("Warnung: Keine Daten gefunden. Layout geändert?")

    for item in accordions:
        btn = item.select_one(".accordion__button")
        if not btn: continue
        
        header_text = btn.get_text(strip=True) # z.B. "Montag 27.12."
        
        # Welcher Tag ist es?
        current_day = None
        for day in DAYS_MAPPING.keys():
            if day in header_text:
                current_day = day
                break
        
        if current_day:
            content = item.select_one(".accordion__content")
            if not content: continue
            
            # Zeilen finden
            rows = content.select(".speiseplan__offer")
            if not rows: rows = content.select("tr") # Fallback

            for row in rows:
                # Versuch Selektoren für Kassel
                cat_el = row.select_one(".speiseplan__offer-type")
                meal_el = row.select_one(".speiseplan__offer-description") 
                price_el = row.select_one(".speiseplan__offer-price")

                category = cat_el.get_text(strip=True) if cat_el else "Essen"
                meal = meal_el.get_text(strip=True) if meal_el else "Gericht"
                price = price_el.get_text(strip=True) if price_el else ""

                # Filter: Keine Salate, keine leeren Gerichte
                if "Salat" in category or "Salat" in meal:
                    continue
                
                # Bereinigung: Fussnoten in Klammern (1,2,3) entfernen
                meal_clean = re.sub(r'\s*\(\s*\d+(?:\s*,\s*\d+)*\s*\)', '', meal)

                week_data[current_day].append({
                    "category": category,
                    "meal": meal_clean,
                    "price": price
                })

    # Bilder erzeugen
    for day_name, filename in DAYS_MAPPING.items():
        create_image(day_name, week_data.get(day_name, []), filename)

if __name__ == "__main__":
    main()
