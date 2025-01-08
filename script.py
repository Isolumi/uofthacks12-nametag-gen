from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import qrcode
import io


def mm_to_px(mm, dpi=300):
    return int(mm * dpi / 25.4)


NAME_CARD_WIDTH = 90
NAME_CARD_HEIGHT = 62
A4_WIDTH = 297
A4_HEIGHT = 210
GRID_ROWS = 3
GRID_COLUMNS = 3
NAME_TAGS_OUTPUT_FOLDER = 'name_tags'
SHEET_OUTPUT_FOLDER = 'name_cards_sheet'

name_card_width_px = mm_to_px(89)
name_card_height_px = mm_to_px(63)
a4_width_px = mm_to_px(A4_WIDTH)
a4_height_px = mm_to_px(A4_HEIGHT)

csv_file = 'MOCK_DATA.csv'
data = pd.read_csv(csv_file)


# load fonts
try:
    font_bold_7 = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(7))
    font_bold_6 = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(6))
    font_bold_5 = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(5))
    font_bold_4 = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(4))
    font_bold_3 = ImageFont.truetype('fonts/Roboto-Bold.ttf', size=mm_to_px(3))
    font_regular_4 = ImageFont.truetype('fonts/Roboto-Regular.ttf', size=mm_to_px(4))
    font_regular_3 = ImageFont.truetype('fonts/Roboto-Regular.ttf', size=mm_to_px(3))
    font_regular_2 = ImageFont.truetype('fonts/Roboto-Regular.ttf', size=mm_to_px(2))
except OSError:
    if os.name == 'nt':
        font_path = 'C:/Windows/Fonts/Roboto-Bold.ttf'
    else:
        font_path = '/System/Library/Fonts/Roboto-Bold.ttf'


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
    qr_img = qr.make_image(fill_color='black', back_color='white')

    # resize
    size_px = mm_to_px(size_mm)
    qr_img = qr_img.resize((size_px, size_px), Image.Resampling.LANCZOS)

    return qr_img


name_card_images = []
for _, row in data.iterrows():
    pref_name = row['pref_name'].split(' ')[0]
    card = Image.open(f'templates/{row['type']}.png').convert('RGB')
    draw = ImageDraw.Draw(card)

    # determine font sizes
    if len(pref_name) < 15 and len(row['last_name']) < 15:
        name_font = font_bold_7
        pronouns_font = font_regular_4
    else:
        name_font = font_bold_4
        pronouns_font = font_regular_3

    if row['type'] == 'hacker':
        # draw text on card
        center_x = name_card_width_px // 2 + 25
        first_name_y = 200 if len(pref_name) < 15 else 240

        # calculate bounding boxes with the correct fonts
        first_name_bbox = draw.textbbox(
            (0, 0),
            pref_name,
            font=name_font,
        )
        last_name_bbox = draw.textbbox(
            (0, 0),
            row['last_name'],
            font=name_font,
        )

        # draw centered names
        draw.text(
            (center_x - (first_name_bbox[2] - first_name_bbox[0]) // 2, first_name_y),
            pref_name,
            font=name_font,
            fill='black',
        )

        dy = 100 if len(pref_name) < 15 else 60
        draw.text(
            (
                center_x - (last_name_bbox[2] - last_name_bbox[0]) // 2,
                first_name_y + dy,
            ),
            row['last_name'],
            font=name_font,
            fill='black',
        )

        if 'pronouns' in data.columns:
            pronouns_bbox = draw.textbbox((0, 0), row['pronouns'], font=pronouns_font)
            dy = 220 if len(pref_name) < 15 else 150
            draw.text(
                (
                    center_x - (pronouns_bbox[2] - pronouns_bbox[0]) // 2,
                    first_name_y + dy,
                ),
                row['pronouns'],
                font=pronouns_font,
                fill='black',
            )

        # center ID number
        id_text = str(row['id'])
        id_bbox = draw.textbbox((0, 0), id_text, font=font_regular_3)
        id_x = 750 - (id_bbox[2] - id_bbox[0]) // 2
        draw.text((id_x, 475), id_text, font=font_regular_3, fill='black')

        qr_code_image = create_qr_code(row['qr_hash'], 18)
        card.paste(qr_code_image, (95, 230))

    else:
        lines = [row['type'], pref_name, row['last_name'], row['pronouns']]
        fonts = [font_regular_4, font_bold_6, font_bold_6, font_regular_4]
        line_widths = []
        line_heights = []

        for i, line in enumerate(lines):
            text_bbox = draw.textbbox((0, 0), line, font=fonts[i])
            line_width = text_bbox[2] - text_bbox[0]
            line_height = text_bbox[3] - text_bbox[1]
            line_widths.append(line_width)
            line_heights.append(line_height)

        max_line_width = max(line_widths)
        total_text_height = (
            sum(line_heights) + (len(lines) - 1) * 10
        )  # add spacing between lines

        # center block of text vertically
        image_width, image_height = card.size

        y_offset = 180
        dy = [30, 20, 40, 0]
        for i, line in enumerate(lines):
            line_width = line_widths[i]
            text_x = (image_width - max_line_width) // 2 + (
                max_line_width - line_width
            ) // 2

            draw.text((text_x, y_offset), line, font=fonts[i], fill='black')
            y_offset += line_heights[i] + dy[i]  # move to next line with spacing

    # Scale the card to exactly 90mm width while maintaining aspect ratio
    target_width = mm_to_px(90)
    scale_factor = target_width / card.width
    target_height = int(card.height * scale_factor)
    card = card.resize((target_width, target_height), Image.Resampling.LANCZOS)

    name_card_path = os.path.join(
        NAME_TAGS_OUTPUT_FOLDER, f'{pref_name}_{row["last_name"]}_{row["id"]}.png'
    )

    name_card_images.append(card)

# combine into multiple A4 sheets
num_cards_per_sheet = GRID_ROWS * GRID_COLUMNS
num_sheets = (len(name_card_images) + num_cards_per_sheet - 1) // num_cards_per_sheet

# combine into A4 sheet
a4_sheet = Image.new('RGB', (a4_width_px, a4_height_px), 'white')

if name_card_images:
    actual_width = name_card_images[0].width
    actual_height = name_card_images[0].height
    
for sheet_num in range(num_sheets):
    a4_sheet = Image.new('RGB', (a4_width_px, a4_height_px), 'white')
    
    # Process cards for current sheet
    start_idx = sheet_num * num_cards_per_sheet
    end_idx = min(start_idx + num_cards_per_sheet, len(name_card_images))
    
    for i, card in enumerate(name_card_images[start_idx:end_idx]):
        row = i // GRID_COLUMNS
        col = i % GRID_COLUMNS
        
        x = col * actual_width
        y = row * actual_height
        a4_sheet.paste(card, (x, y))
    
    # save each sheet with sequential numbering
    os.makedirs(SHEET_OUTPUT_FOLDER, exist_ok=True)
    a4_output_path = os.path.join(SHEET_OUTPUT_FOLDER, f'{sheet_num + 1}.png')
    a4_sheet.save(a4_output_path)
