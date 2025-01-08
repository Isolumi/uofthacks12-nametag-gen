from PIL import Image, ImageDraw, ImageFont

# Load your PNG image
image_path = "templates/blank.png"  # Replace with your PNG file path
image = Image.open(image_path)

# Create a drawing context
draw = ImageDraw.Draw(image)

# Define the text and font
lines = ["Line 1", "A longer line of text", "Short"]  # Your lines of text
font_path = "fonts/Roboto-Bold.ttf"  # Replace with the path to your .ttf font file
font_size = 40  # Adjust font size as needed
try:
    font = ImageFont.truetype(font_path, font_size)
except Exception as e:
    pass

# Calculate the width of each line and find the widest line
line_widths = []
line_heights = []

for line in lines:
    text_bbox = draw.textbbox((0, 0), line, font=font)
    line_width = text_bbox[2] - text_bbox[0]
    line_height = text_bbox[3] - text_bbox[1]
    line_widths.append(line_width)
    line_heights.append(line_height)

max_line_width = max(line_widths)
total_text_height = sum(line_heights) + (len(lines) - 1) * 10  # Add spacing between lines

# Center the block of text vertically
image_width, image_height = image.size
start_y = (image_height - total_text_height) // 2

# Draw each line, centered horizontally with respect to the widest line
y_offset = start_y
for i, line in enumerate(lines):
    line_width = line_widths[i]
    text_x = (image_width - max_line_width) // 2 + (max_line_width - line_width) // 2
    draw.text((text_x, y_offset), line, font=font, fill="black")  # Adjust fill color as needed
    y_offset += line_heights[i] + 10  # Move to the next line with spacing

# Save the image
output_path = "output_image.png"  # Replace with your desired output path
image.save(output_path)

print(f"Image saved at {output_path}")
