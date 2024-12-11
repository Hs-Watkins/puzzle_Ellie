from flask import Flask, render_template, request, redirect, url_for, send_file
from bs4 import BeautifulSoup
import requests
import os
import random
from PIL import Image

app = Flask(__name__)

# Configurations
ENABLE_PACKAGE_CHECK = True  # Toggle the package/code check
ACCESS_CODE = "1234"         # Code to bypass the package check
PUZZLE_FOLDER = "static/puzzle_images"
DEFAULT_IMAGE = "static/uploads/default_image.png"
UPS_TRACKING_URL = "https://www.ups.com/track?HTMLVersion=5.0&loc=en_US&Requester=UPSHome&WBPM_lid=homepage%2Fct1.html_pnl_trk&track.x=Track&trackNums=1ZW086A80435946022/trackdetails"

def check_package_status():
    """Checks the UPS tracking URL to determine if the package has been delivered."""
    try:
        response = requests.get(UPS_TRACKING_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Look for "Delivered" status text on the page
        status_element = soup.find("span", string="Delivered")
        if status_element:
            return True
        return False
    except Exception as e:
        print(f"Error checking package status: {e}")
        return False

@app.route("/", methods=["GET", "POST"])
def welcome():
    """Welcome page logic."""
    if not ENABLE_PACKAGE_CHECK or check_package_status():
        return redirect(url_for("puzzle"))
    
    if request.method == "POST":
        entered_code = request.form.get("access_code")
        if entered_code == ACCESS_CODE:
            return redirect(url_for("puzzle"))
        else:
            return render_template("welcome.html", error="Invalid code. Please try again.")
    
    return render_template("welcome.html", error=None)

@app.route("/puzzle", methods=["GET"])
def puzzle():
    """Puzzle page logic."""
    create_puzzle(DEFAULT_IMAGE)
    puzzle_pieces = [f"/static/puzzle_images/{piece}" for piece in os.listdir(PUZZLE_FOLDER)]
    random.shuffle(puzzle_pieces)
    return render_template("index.html", puzzle_pieces=puzzle_pieces)

@app.route("/download", methods=["GET"])
def download_image():
    """Serves the original image for download."""
    return send_file(DEFAULT_IMAGE, as_attachment=True)

def create_puzzle(image_path):
    """Slices the default image into pieces for the puzzle."""
    img = Image.open(image_path)
    width, height = img.size

    cols, rows = 5, 4  # Puzzle grid dimensions
    piece_width = width // cols
    piece_height = height // rows

    if not os.path.exists(PUZZLE_FOLDER):
        os.makedirs(PUZZLE_FOLDER)

    # Clear the puzzle folder
    for file in os.listdir(PUZZLE_FOLDER):
        os.remove(os.path.join(PUZZLE_FOLDER, file))

    for row in range(rows):
        for col in range(cols):
            left = col * piece_width
            upper = row * piece_height
            right = left + piece_width
            lower = upper + piece_height
            piece = img.crop((left, upper, right, lower))
            piece.save(f"{PUZZLE_FOLDER}/piece_{row}_{col}.png")

# Run the app with gunicorn compatibility
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
