# Kharisma Fitri Nurunnisa Siahaan - 140810200047
import cv2
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, flash, redirect, url_for

#sesuaikan dengan path
UPLOAD_FOLDER = '/Users/kharism/Downloads/img2sketch/static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def grayscale(img, g):
    try:
        match g:
            case "g0":
                grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            case "g1":
                grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                height, width = grayed.shape[:2]
                for i in range(height):
                    for j in range(width):
                        grayed[i, j] = int((int(img[i, j, 0]) + int(img[i, j, 1]) + int(img[i, j, 2])) / 3)
            case "g2":
                grayed = img[:, :, 1]  # Select the green channel (0 for red, 1 for green, 2 for blue)
    except Exception as e:
        flash(f"Grayscale conversion error: {str(e)}")
        return None
    return grayed

def gaussian_blur(img, gb):
    try:
        if gb % 2 == 0:  # Check if the kernel size is even
            gb += 1  # Increment the kernel size by 1 to make it odd
        blurred = cv2.GaussianBlur(img, (gb, gb), sigmaX=0, sigmaY=0)
    except Exception as e:
        flash(f"Gaussian blur error: {str(e)}")
        return None
    return blurred

def make_sketch(img, g, gb):
    grayed = grayscale(img, g)
    if grayed is None:
        return None

    inverted = cv2.bitwise_not(grayed)
    blurred = gaussian_blur(inverted, gb)
    if blurred is None:
        return None

    final_result = cv2.divide(grayed, 255 - blurred, scale=256)
    return final_result

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sketch', methods=['POST'])
def sketch():
    file = request.files['file']
    g = request.form['gray']
    gb = int(request.form['gb'])
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img = cv2.imread(UPLOAD_FOLDER + '/' + filename)
            sketch_img = make_sketch(img, g, gb)
            if sketch_img is None:
                flash("Sketch creation failed")
                return redirect(url_for('home'))
            
            sketch_img_name = filename.split('.')[0] + "_sketch.jpg"
            _ = cv2.imwrite(UPLOAD_FOLDER + '/' + sketch_img_name, sketch_img)
            return render_template('home.html', org_img_name=filename, sketch_img_name=sketch_img_name)
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    else:
        flash("Invalid file format")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)