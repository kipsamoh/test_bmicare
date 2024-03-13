from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bmi_database.db'
db = SQLAlchemy(app)

# Define BMIRecord model
class BMIRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    recommendation = db.Column(db.String(200), nullable=False)

# Define Admin Blueprint
admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

# Admin login route
@admin_blueprint.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'adminpassword':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', message='Invalid credentials. Please try again.')
    return render_template('admin/login.html')

# Admin dashboard route
@admin_blueprint.route('/dashboard')
def admin_dashboard():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        # Query all BMI records
        bmi_records = BMIRecord.query.all()
        return render_template('admin/dashboard.html', bmi_records=bmi_records)
    else:
        return redirect(url_for('admin.admin_login'))

# BMI calculator Blueprint
bmi_calculator_blueprint = Blueprint('bmi_calculator', __name__)

# BMI calculator route
@bmi_calculator_blueprint.route('/')
def index():
    return render_template('index.html')

# Calculate BMI route
@bmi_calculator_blueprint.route('/calculate_bmi', methods=['POST'])
def calculate_bmi():
    height = float(request.form['height'])
    weight = float(request.form['weight'])
    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        recommendation = "You are underweight. You should consider gaining some weight."
    elif bmi >= 18.5 and bmi < 24.9:
        recommendation = "Your weight is normal. Keep up the good work!"
    elif bmi >= 25 and bmi < 29.9:
        recommendation = "You are overweight. You should consider losing some weight."
    else:
        recommendation = "You are obese. It's important to prioritize weight loss for your health."

    # Create BMIRecord object and save to database
    new_record = BMIRecord(height=height, weight=weight, bmi=bmi, recommendation=recommendation)
    db.session.add(new_record)
    db.session.commit()

    return render_template('result.html', bmi=bmi, recommendation=recommendation)

# Register Blueprints
app.register_blueprint(bmi_calculator_blueprint)
app.register_blueprint(admin_blueprint)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

