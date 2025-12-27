from PIL import Image, ImageDraw, ImageFont
import os

# --- KONFIGURATION ---
OUTPUT_FILE = "test_output.png"
FONT_PATH = "Futura.ttc" 
IMG_WIDTH = 1448
IMG_HEIGHT = 1072

# TEXT GRÖSSEN
FONT_SIZE_HEADER_MAIN = 60
FONT_SIZE_LABEL = 35        
FONT_SIZE_TEXT = 52         
LINE_SPACING = 12           

# LAYOUT ABSTÄNDE
START_Y = 160
MIN_PADDING = 20    # Darf etwas enger zusammenrutschen, wenn nötig
BOTTOM_MARGIN = 90  # NEU: Mehr Luft zum unteren Rand (ca. 1.5 Zeilen)

# DUMMY DATEN (Lange Texte)
dummy_dishes = [
    { "meal": "Saftiges Rindergulasch mit frischen roten und grünen Paprikaschoten, dazu servieren wir handgeschabte Spätzle und einen kleinen gemischten Salat mit Joghurt-Dressing." },
    { "meal": "Große Portion vegane Lasagne mit Sojagranulat, frischem Spinat und Tomatensauce, überbacken mit veganem Käseersatz, dazu gibt es ein knuspriges Vollkornbrötchen." },
    { "meal": "Gebratenes Seelachsfilet in einer leichten Zitronen-Dill-Sauce auf buntem Pfannengemüse mit Wildreis und einer kleinen Portion Kräuterquark zum Dippen." }
]

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except IOError:
        return ImageFont.load_default()

def calculate_wrapped_lines(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        if width < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def create_test_image():
    img = Image.new('L', (IMG_WIDTH, IMG_HEIGHT), 255)
    draw = ImageDraw.Draw(img)
    
    font_main = get_font(FONT_SIZE_HEADER_MAIN)
    font_label = get_font(FONT_SIZE_LABEL)
    font_text = get_font(FONT_SIZE_TEXT)

    # --- HEADER ---
    draw.text((50, 40), "Zentralmensa", font=font_main, fill=0)
    draw.line((50, 120, IMG_WIDTH - 50, 120), fill=0, width=6)
    
    # --- BERECHNUNG ---
    dishes_to_draw = dummy_dishes[:3]
    block_heights = []
    wrapped_texts = [] 

    for dish in dishes_to_draw:
        # Label Höhe + 10px
        h = FONT_SIZE_LABEL + 10
        
        # Text Höhe
        lines = calculate_wrapped_lines(dish['meal'], font_text, IMG_WIDTH - 100)
        wrapped_texts.append(lines)
        
        text_h = len(lines) * FONT_SIZE_TEXT + (len(lines)-1) * LINE_SPACING
        h += text_h
        block_heights.append(h)

    total_content_height = sum(block_heights)
    
    # Verfügbare Höhe unter Berücksichtigung des neuen BOTTOM_MARGIN
    available_height = IMG_HEIGHT - START_Y - BOTTOM_MARGIN
    
    free_space = available_height - total_content_height
    
    # Dynamischer Abstand
    if len(dishes_to_draw) > 1:
        dynamic_gap = free_space / (len(dishes_to_draw) - 1)
        dynamic_gap = max(MIN_PADDING, dynamic_gap)
    else:
        dynamic_gap = MIN_PADDING

    if free_space < 0:
        print(f"WARNUNG: Text ist zu lang! Überhang: {abs(int(free_space))}px")

    # --- ZEICHNEN ---
    current_y = START_Y
    
    for i, dish in enumerate(dishes_to_draw):
        # Label "Essen X"
        label = f"Essen {i+1}"
        draw.text((50, current_y), label, font=font_label, fill=0)
        current_y += (FONT_SIZE_LABEL + 10)
        
        # Text
        lines = wrapped_texts[i]
        for line in lines:
            draw.text((50, current_y), line, font=font_text, fill=0)
            current_y += (FONT_SIZE_TEXT + LINE_SPACING)
        
        # Abstand
        if i < len(dishes_to_draw) - 1:
            current_y += dynamic_gap

    img.save(OUTPUT_FILE)
    print(f"Bild erstellt: {OUTPUT_FILE}")
    print(f"Unten frei: {IMG_HEIGHT - current_y}px (Soll: {BOTTOM_MARGIN}px)")

if __name__ == "__main__":
    create_test_image()
