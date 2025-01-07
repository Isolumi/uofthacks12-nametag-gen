from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import qrcode
import io

# consts
NAME_CARD_WIDTH = 89
NAME_CARD_HEIGHT = 63
A4_WIDTH = 297
A4_HEIGHT = 210
DPI = 300
GRID_ROWS = 3
GRID_COLUMNS = 3

OUTPUT_FOLDER = 'name_tags'
TEMPLATE_PATH = 'templates/blank_template.png'


def mm_to_px(mm, dpi=DPI):
    return int(mm * dpi / 25.4)


name_card_width_px = mm_to_px(89)
name_card_height_px = mm_to_px(63)
a4_width_px = mm_to_px(A4_WIDTH)
a4_height_px = mm_to_px(A4_HEIGHT)

csv_file = 'MOCK_DATA_SINGLE.csv'
data = pd.read_csv(csv_file)

try:
    font_large = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(7))
    font_large_small = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(5))
    font_small = ImageFont.truetype('fonts/Roboto-Regular.ttf', size=mm_to_px(4))
    font_id = ImageFont.truetype('fonts/Roboto-Regular.ttf', size=mm_to_px(3))
except OSError:
    if os.name == 'nt':
        pass
    else:
        font_path = '/System/Library/Fonts/Roboto-Bold.ttf'
        font_large = ImageFont.truetype(font_path, size=mm_to_px(8))
        font_large_small = ImageFont.truetype(font_path, size=mm_to_px(5))
        font_small = ImageFont.truetype(font_path, size=mm_to_px(4))


def create_qr_code(data, size_mm):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # resize
    size_px = mm_to_px(size_mm)
    qr_img = qr_img.resize((size_px, size_px), Image.Resampling.LANCZOS)
    
    return qr_img


name_card_images = []
# iterate over rows in csv
for _, row in data.iterrows():
    card = Image.open(f'templates/{row['type']}.png').convert('RGB')
    draw = ImageDraw.Draw(card)

    # draw text on card
    first_name_bbox = draw.textbbox((0, 0), row['first_name'], font=font_large)
    last_name_bbox = draw.textbbox((0, 0), row['last_name'], font=font_large)

    # If either name is too wide (e.g., more than 300px), use smaller font
    name_width_threshold = 300
    if (first_name_bbox[2] - first_name_bbox[0] > name_width_threshold or 
        last_name_bbox[2] - last_name_bbox[0] > name_width_threshold):
        font_to_use = font_large_small
        # Recalculate bboxes with new font
        first_name_bbox = draw.textbbox((0, 0), row['first_name'], font=font_to_use)
        last_name_bbox = draw.textbbox((0, 0), row['last_name'], font=font_to_use)
    else:
        font_to_use = font_large

    center_x = name_card_width_px // 2 + 25
    first_name_y = 200
    draw.text(
        (center_x - (first_name_bbox[2] - first_name_bbox[0]) // 2, first_name_y),
        row['first_name'],
        font=font_to_use,
        fill='black',
    )
    draw.text(
        (center_x - (last_name_bbox[2] - last_name_bbox[0]) // 2, first_name_y + 100),
        row['last_name'],
        font=font_to_use,
        fill='black',
    )

    if 'pronouns' in data.columns:
        pronouns_bbox = draw.textbbox((0, 0), row['pronouns'], font=font_small)
        draw.text(
            (center_x - (pronouns_bbox[2] - pronouns_bbox[0]) // 2, first_name_y + 220),
            row['pronouns'],
            font=font_small,
            fill='black',
        )
    
    # center ID number
    id_text = str(row['id'])
    id_bbox = draw.textbbox((0, 0), id_text, font=font_id)
    id_x = 750 - (id_bbox[2] - id_bbox[0]) // 2
    draw.text((id_x, 475), id_text, font=font_id, fill='black')

    qr_code_image = create_qr_code(row['qr_hash'], 18)
    card.paste(qr_code_image, (85, 230))

    name_card_path = os.path.join(
        OUTPUT_FOLDER, f'{row['first_name']}_{row['last_name']}.png'
    )

    # create output folder if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    card.save(name_card_path)
    name_card_images.append(card)


# combine into A4 sheet
a4_sheet = Image.new('RGB', (a4_width_px, a4_height_px), 'white')
x_offset = (a4_width_px - GRID_COLUMNS * name_card_width_px) // (GRID_COLUMNS + 1)
y_offset = (a4_height_px - GRID_ROWS * name_card_height_px) // (GRID_ROWS + 1)

for i, card in enumerate(name_card_images):
    row = i // GRID_COLUMNS
    col = i % GRID_COLUMNS
    if row >= GRID_ROWS:
        break

    x = x_offset + col * (name_card_width_px + x_offset)
    y = y_offset + row * (name_card_height_px + y_offset)
    a4_sheet.paste(card, (x, y))

# Save the final sheet
a4_output_path = os.path.join(OUTPUT_FOLDER, 'name_cards_sheet.png')
a4_sheet.save(a4_output_path)