import os
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from decimal import Decimal
from tinydb import TinyDB, Query
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from random import randint
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from flask import flash
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16)
db = SQLAlchemy(app)
tdb = TinyDB("database.txt")
qdb = Query()

# Define a new Token table
class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    cart = db.Column(db.String, nullable=True)  # Add this line for cart

    def __repr__(self):
        return f'<User {self.name}>'


# Define a new OTP table
class OTPs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    otp = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# Function to generate a random token
def generate_token():
    return randint(100000, 999999)

def generate_otp():
    return randint(100000, 999999)

# Function to send the OTP to the user's email
def send_otp(user_email, otp):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = 'gabrielelufidodo@gmail.com'
    sender_password = 'eeinsljkveqthnur'

    subject = 'One-Time Password (OTP) for Login'
    message = f'Greetings,\n\nYour one-time password (OTP) for login is: {otp}\n\nPlease use this code to complete the login process. Do not share this code with anyone.\n\nBest regards,\nThe Login System'

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = user_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [user_email], msg.as_string())


# Function to send the token to the user's email
def send_token(user_email, token):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = 'gabrielelufidodo@gmail.com'
    sender_password = 'eeinsljkveqthnur'

    msg = MIMEText(f"Your unique IDENTIFICATION Token is: {token}, Keep it and never reveal it to anybody")
    msg['Subject'] = 'Login Token'
    msg['From'] = sender_email
    msg['To'] = user_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [user_email], msg.as_string())

# Your existing Products class definition
class Products(db.Model):
    pname = db.Column(db.String, nullable=False)
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    des = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    img = db.Column(db.String, nullable=False)
    cat = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Product {self.pname}>'

@app.route('/')
def index():
    shoes = Products.query.filter_by(cat="shoes").all()
    gadgets = Products.query.filter_by(cat="gadgets").all()
    clothes = Products.query.filter_by(cat="clothes").all()
    
    return render_template("index.html", shoes=shoes, gadgets=gadgets, clothes=clothes, Getuser=Getuser(session.get("email")))




@app.route('/category/<cat>')
def cat(cat):
    kat = cat
    pd = Products.query.filter_by(cat=cat).all()
    return render_template("category.html", pd=pd, cat=kat)



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")

        user_query = User.query.filter_by(email=email).first()
        if user_query and check_password_hash(user_query.password, password):
            # Check if there is an existing OTP record for the user
            otp_entry = OTPs.query.filter_by(email=email).first()

            if otp_entry:
                # If OTP record exists, update it with a new OTP
                otp_entry.otp = generate_otp()
                otp_entry.created_at = datetime.utcnow()
            else:
                # If no OTP record exists, create a new one
                otp_entry = OTPs(email=email, otp=generate_otp(), created_at=datetime.utcnow())

            # Save or update the OTP entry
            db.session.add(otp_entry)
            db.session.commit()

            # Send OTP to user's email
            send_otp(email, otp_entry.otp)

            session["email"] = email
            return redirect(url_for('otp_verification'))
        else:
            return render_template("login.html", mess="Incorrect email or password")

    return render_template("login.html")


@app.route("/otp_verification", methods=["POST", "GET"])
def otp_verification():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        entered_otp = request.form.get("otp")
        stored_otp_data = OTPs.query.filter_by(email=session['email']).first()

        if not stored_otp_data:
            flash("No OTP found for this user. Please request a new one.", "danger")
            return render_template("otp_verification.html")

        stored_otp = stored_otp_data.otp

        if entered_otp == str(stored_otp):
            # OTP is valid, continue with the login process
            # ...

            # Clear the OTP from the database
            db.session.delete(stored_otp_data)
            db.session.commit()

            flash("OTP verified successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Incorrect OTP. Please try again.", "danger")
            return render_template("otp_verification.html")

    # This block will execute for GET requests or unexpected cases
    return render_template("otp_verification.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["pass"]
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        name = request.form["name"]

        quer = User.query.filter_by(email=email).first()
        if not quer:
            # Save user in the User table
            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            # Generate and save token for the user
            token = generate_token()
            token_entry = Tokens(email=email, token=token)
            db.session.add(token_entry)
            db.session.commit()

            # Send the token to the user's email
            send_token(email, token)

            # Redirect to login page
            return redirect(url_for('login'))

    return render_template("signup.html")



@app.route('/create')
def createacct():
    return render_template("signup.html")

@app.route('/cart')
def cart():
    if not session.get("email"):
        return redirect("/login")
    else:
        user = User.query.filter_by(email=session["email"]).first()

        if user and hasattr(user, "cart") and user.cart:
            items = user.cart.split(",") if user.cart else []

            # Compute total price of items in the cart
            total_price = sum(Decimal(re.sub(r'[^\d.]', '', Getcarddata(item).price())) for item in items)

            return render_template("cart.html", items=items, total_price=total_price, Getcarddata=Getcarddata)
        else:
            # Handle the case when the user or user's cart is not found
            flash("User or user's cart not found.", "danger")
            return render_template("cart.html")

    return render_template("cart.html")
    return render_template("cart.html")



@app.route('/logout')
def logout():
    session["email"] = None
    return redirect('/')

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        q = request.form["q"]
        spd = Products.query.filter_by(pname=q).all()
        if spd:
            return render_template("search.html", pd=spd, q=q)
        else:
            return render_template("search.html", mess="No results found", q=q)
    return render_template("search.html")

@app.route('/api/<id>', methods=["GET"])
def api(id):
    apn = Getcarddata(id).pname()
    ades = Getcarddata(id).des()
    aimg = Getcarddata(id).img()
    aprice = Getcarddata(id).price()
    acat = Getcarddata(id).cat()
    return jsonify({"pname": apn, "des": ades, "img": aimg, "price": aprice, "category": acat})

@app.route('/addtocart/<id>')
def addtocart(id):
    if 'email' not in session:
        return redirect("/login")

    email = session['email']
    user = User.query.filter_by(email=email).first()

    if user:
        if not hasattr(user, 'cart') or user.cart is None:
            user.cart = str(id)
        else:
            items = user.cart.split(',') if user.cart else []
            items.append(str(id))
            user.cart = ','.join(items)

        db.session.commit()
        flash("Product added to cart successfully!", "success")
        return redirect('/cart')
    else:
        flash(f"User with email {email} not found.", "danger")

    return redirect("/cart")






@app.route('/rfromcart/<id>')
def rfromcart(id):
    if not session.get("email"):
        return redirect("/login")
    else:
        user = User.query.filter_by(email=session["email"]).first()
        if user and hasattr(user, 'cart') and user.cart:
            items = user.cart.split(',')
            if str(id) in items:
                items.remove(str(id))
                user.cart = ','.join(items)
                db.session.commit()
                flash("Product removed from cart successfully!", "success")
            else:
                flash("Product not found in the cart.", "danger")

            return redirect('/cart')

    return redirect("/cart")


class Getcarddata:
    def __init__(self, id):
        self.id = id
        self.pd = Products.query.filter_by(id=self.id).first()

    def pname(self):
        return self.pd.pname if self.pd else None

    def des(self):
        return self.pd.des if self.pd else None

    def img(self):
        return self.pd.img if self.pd else None

    def cat(self):
        return self.pd.cat if self.pd else None

    def price(self):
        return self.pd.price if self.pd else None

class Getuser:
    def __init__(self, email):
        self.email = email
        self.user = User.query.filter_by(email=email).first() if email else None

    def get_name(self):
        return self.user.name if self.user else None


@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        # Handle form submission
        flash("Form submitted successfully!", "success")
        
    
    else:
        # Render the template for GET requests
        return render_template('success.html')
    return redirect('/index')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        token = request.form.get('token')

        # Check if the email and token are valid
        token_entry = Tokens.query.filter_by(email=email, token=token).first()

        if token_entry:
            # If the token is valid, redirect to the new password page
            return redirect(url_for('new_password', email=email))

        flash('Invalid email or token. Please try again.', 'danger')
    
    return render_template('reset_password.html')


# ...

@app.route('/new_password/<email>', methods=['GET', 'POST'])
def new_password(email):
    if request.method == 'POST':
        # Handle the form submission to update the password
        new_password = request.form.get('new_pass')

        # Update the password in the User table
        user = User.query.filter_by(email=email).first()

        if user:
            # Hash the new password
            #hashed_password = generate_password_hash(new_password)
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')


            if hashed_password:
                user.password = hashed_password
                db.session.commit()

                # Optionally, you can also delete the used token entry
                db.session.delete(Tokens.query.filter_by(email=email).first())
                db.session.commit()

                flash('Password updated successfully!', 'success')
                return redirect(url_for('login'))

            flash('Failed to hash the password. Please try again.', 'danger')

    return render_template('new_password.html', email=email)


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)