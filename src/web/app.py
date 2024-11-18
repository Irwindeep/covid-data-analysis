from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import os

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

# Routes
@app.route('/')
def home():
    return render_template('home.html', title="Home")

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

@app.route('/classifier/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        flash("Data successfully uploaded to the dataset!")
        return redirect(url_for('home'))
    user_info = session.get('user_info', {})
    uploaded_file = session.get('uploaded_file', None)
    return render_template('analysis.html', title="Analysis", user_info=user_info, uploaded_file=uploaded_file)

@app.route('/data-analysis', methods=['GET', 'POST'])
def data_analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('data_analysis.html', title="Data Analysis")

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
    readme_path = './src/model/README.md'
    with open(readme_path, 'r') as file:
        readme_content = file.read()
    return render_template('model.html', title="Model", readme_content=readme_content)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
