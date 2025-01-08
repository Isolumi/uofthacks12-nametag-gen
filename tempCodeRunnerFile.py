# combine into A4 sheet
a4_sheet = Image.new("RGB", (a4_width_px, a4_height_px), "white")

for i, card in enumerate(name_card_images):
    row = i // GRID_COLUMNS
    col = i % GRID_COLUMNS
    if row >= GRID_ROWS:
        break

    x = col * name_card_width_px
    y = row * name_card_height_px
    a4_sheet.paste(card, (x, y))

# save the final sheet
os.makedirs(SHEET_OUTPUT_FOLDER, exist_ok=True)
a4_output_path = os.path.join(SHEET_OUTPUT_FOLDER, "name_cards_sheet.png")
a4_sheet.save(a4_output_path)