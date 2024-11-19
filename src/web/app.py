from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import os, markdown, sys
from tensorflow.keras.models import load_model # type: ignore
import pandas as pd
import numpy as np
from PIL import Image
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../classifier"
    )
)
from preprocessing import Preprocessor # type: ignore

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

MODEL = load_model(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../classifier/best_model.keras"
    )
)

print(MODEL.summary())
print(type(MODEL))

ALLOWED_EXTENSIONS = {'mp4', 'avi'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def home():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(base_dir, '../../README.md')
    with open(readme_path, 'r') as file:
        readme_content = file.read()

    readme_html = markdown.markdown(readme_content)
    return render_template('home.html', title="Home", readme_content=readme_html)

@app.route('/add_user/<username>/<password>')
def add_user(username, password):
    from werkzeug.security import generate_password_hash
    with app.app_context():
        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return f"User {username} already exists."

        # Add the new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return f"User {username} added successfully."

@app.route('/classifier/upload', methods=['GET', 'POST'])
def classifier_upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
            session['uploaded_file'] = uploaded_file.filename
            return redirect(url_for('user_info'))
    return render_template('classifier_upload.html', title="Classifier")

@app.route('/classifier/user-info', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        user_data = {
            'name': request.form['name'],
            'age': request.form['age'],
            'gender': request.form['gender'],
            'room_temp': request.form['room_temp'],
            'mobile': request.form['mobile'],
            'email': request.form['email']
        }
        session['user_info'] = user_data
        return redirect(url_for('analysis'))
    return render_template('user_info.html', title="User Info")

@app.route('/users')
def get_users():
    with app.app_context():
        users = User.query.all()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return {'users': user_list}

@app.route('/classifier/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        flash("Data successfully uploaded to the dataset!")
        return redirect(url_for('home'))
    uploaded_file = session.get('uploaded_file', None)
    uploaded_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join("static/uploads", uploaded_file)
    )

    person_id = 10000
    data = {
        'person_id': person_id,
        'image_path': uploaded_file,
        'room_temp': 30,
        'min_temp': 30,
        'max_temp': 30,
        'view': "Chest"
    }

    preprocessor = Preprocessor(data)

    hr_image, feats = preprocessor.preprocess()

    hr_image = np.array(hr_image)
    feats = pd.DataFrame(feats).drop(columns='lbp_hist').iloc[0].values

    prediction = MODEL.predict([np.array([hr_image]), np.array([feats])])
    result = "You seem to be Healthy😊" if prediction>=0.5 else "Model Analysis Suggests you to be Unhealthy😔"

    return render_template('analysis.html', title="Analysis", analysis_result=result, user_info=user_info, uploaded_file=uploaded_file)

@app.route('/data-analysis', methods=['GET', 'POST'])
def data_analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(base_dir, '../../data/README.md')
    with open(readme_path, 'r') as file:
        readme_content = file.read()

    readme_html = markdown.markdown(readme_content)
    return render_template('data_analysis.html', title="Data Analysis", readme_content=readme_html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('data_analysis'))
        flash("Invalid username or password.")
    return render_template('login.html', title="Login")

@app.route('/model')
def model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(base_dir, '../classifier/README.md')
    with open(readme_path, 'r') as file:
        readme_content = file.read()

    readme_html = markdown.markdown(readme_content)
    return render_template('model.html', title="Model", readme_content=readme_html)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
