from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from user import User  # Ensure user.py has User class with authentication logic
import pandas as pd  # Assuming data display uses a pandas DataFrame

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management and flash messages

# Set up the LoginManager for managing user sessions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect unauthorized users to the login page

# Dummy dataset for the data display (replace with actual data loading)
data = pd.DataFrame({"Example Column": ["Data 1", "Data 2", "Data 3"]})

@login_manager.user_loader
def load_user(username):
    return User(username) if username in User.users else None

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # Placeholder code for file upload, replace with actual implementation
    if request.method == 'POST':
        # Process file upload here
        flash("File uploaded successfully!")
    return render_template('upload.html')

@app.route('/data')
@login_required
def data_display():
    # Render data display with dummy data for this example
    return render_template('data.html', data=data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
