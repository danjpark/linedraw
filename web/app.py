from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import uuid
import linedraw

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    img = request.files.get('image')
    if not img:
        return redirect(url_for('index'))
    filename = str(uuid.uuid4()) + os.path.splitext(img.filename)[1]
    in_path = os.path.join(UPLOAD_FOLDER, filename)
    img.save(in_path)

    hatch_size = int(request.form.get('hatch_size', 16))
    contour_simplify = int(request.form.get('contour_simplify', 2))
    draw_hatch = 'draw_hatch' in request.form
    draw_contours = 'draw_contours' in request.form
    no_cv = 'no_cv' in request.form

    out_svg = os.path.join(OUTPUT_FOLDER, filename + '.svg')
    lines, steps = linedraw.sketch_steps(
        in_path,
        output_path=out_svg,
        draw_contours_opt=draw_contours,
        draw_hatch_opt=draw_hatch,
        hatch_size_opt=hatch_size,
        contour_simplify_opt=contour_simplify,
        no_cv_opt=no_cv,
    )

    step_paths = {}
    for name, image in steps.items():
        p = os.path.join(OUTPUT_FOLDER, filename + f'_{name}.png')
        image.save(p)
        step_paths[name] = os.path.basename(p)

    return render_template('result.html', steps=step_paths, svg=os.path.basename(out_svg))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)
