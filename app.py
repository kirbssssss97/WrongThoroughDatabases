from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # replace
app.config['MAIL_PASSWORD'] = 'your_app_password'     # replace
mail = Mail(app)

ADMIN_PASSWORD = "0000"

@app.route('/')
def index():
    first_time = session.get("dealer_name") is None
    return render_template('index.html', first_time=first_time)

@app.route('/submit', methods=['POST'])
def submit():
    vin = request.form['vin']
    km = request.form['km']
    email = request.form['email']
    phone = request.form['phone']
    notes = request.form['notes']
    dealer_name = session.get("dealer_name", "Unknown Dealer")

    # Save uploaded files
    uploaded_files = request.files.getlist("photos")
    photo_urls = []
    for file in uploaded_files:
        if file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
            file.save(filepath)
            photo_urls.append(filepath)

    # Send email
    msg = Message(subject=f"New Appraisal Submission from {dealer_name}",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=["your_email@gmail.com"])
    msg.body = f"""
    Dealer Name: {dealer_name}
    VIN: {vin}
    KM: {km}
    Email: {email}
    Phone: {phone}
    Notes: {notes}
    """
    for path in photo_urls:
        with app.open_resource(path) as fp:
            msg.attach(filename=os.path.basename(path), content_type="image/jpeg", data=fp.read())

    mail.send(msg)

    return redirect(url_for('thank_you'))

@app.route('/thankyou')
def thank_you():
    return render_template('thank_you.html')

@app.route('/set_dealer_name', methods=['POST'])
def set_dealer_name():
    name = request.form.get("dealer_name")
    session['dealer_name'] = name
    return ('', 204)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    password = request.form.get("admin_password")
    if password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return redirect(url_for('admin'))
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template("admin.html")

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def sw():
    return send_from_directory('static', 'service_worker.js')

if __name__ == '__main__':
    app.run(debug=True)
