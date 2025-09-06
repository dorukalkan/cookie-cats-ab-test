from PIL import Image

# Open images
img1 = Image.open(
    "reports/figures/3.3_dist_of_game_rounds_by_version_log.png"
)  # 833 x 548
img2 = Image.open(
    "reports/figures/4.3_retention_rates_by_version_95_ci.png"
)  # 984 x 584
img3 = Image.open(
    "reports/figures/4.4_player_count_game_rounds_dist_log.png"
)  # 856 x 548
img4 = Image.open("reports/figures/5_power_vs_mde_at_current_n.png")  # 984 x 584

# Get individual image sizes
w1, h1 = img1.size
w2, h2 = img2.size
w3, h3 = img3.size
w4, h4 = img4.size

# Determine cell dimensions by finding maximum width/height per column/row
col1_width = max(w1, w3)  # left column max width
col2_width = max(w2, w4)  # right column max width
row1_height = max(h1, h2)  # top row max height
row2_height = max(h3, h4)  # bottom row max height

# Overall canvas size
canvas_width = col1_width + col2_width
canvas_height = row1_height + row2_height

# Create a new blank image with white background
combined_image = Image.new("RGB", (canvas_width, canvas_height), color="white")

# Calculate top-left positions for each image to center them in their respective cells
# Top-left cell (for img1)
pos1_x = (col1_width - w1) // 2
pos1_y = (row1_height - h1) // 2

# Top-right cell (for img2)
pos2_x = col1_width + (col2_width - w2) // 2
pos2_y = (row1_height - h2) // 2

# Bottom-left cell (for img3)
pos3_x = (col1_width - w3) // 2
pos3_y = row1_height + (row2_height - h3) // 2

# Bottom-right cell (for img4)
pos4_x = col1_width + (col2_width - w4) // 2
pos4_y = row1_height + (row2_height - h4) // 2

# Paste images onto the canvas at calculated positions
combined_image.paste(img1, (pos1_x, pos1_y))
combined_image.paste(img2, (pos2_x, pos2_y))
combined_image.paste(img3, (pos3_x, pos3_y))
combined_image.paste(img4, (pos4_x, pos4_y))

# Save the combined image
combined_image.save("reports/figures/plots_grid.png")
combined_image.show()
