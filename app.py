from flask import Flask, render_template, request, redirect, url_for, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "railway_booking_demo_secret_key"

trains = [
    {
        "number": "12631",
        "name": "Nellai Express",
        "from": "Chennai",
        "to": "Tirunelveli",
        "departure": "20:10",
        "arrival": "07:35",
        "fare": 450
    },
    {
        "number": "12633",
        "name": "Kanyakumari Express",
        "from": "Chennai",
        "to": "Tirunelveli",
        "departure": "17:15",
        "arrival": "05:30",
        "fare": 500
    },
    {
        "number": "12605",
        "name": "Pallavan Express",
        "from": "Chennai",
        "to": "Trichy",
        "departure": "13:00",
        "arrival": "19:00",
        "fare": 300
    }
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    from_station = request.form["from"].strip()
    to_station = request.form["to"].strip()
    journey_date = request.form["journey_date"]

    results = [
        train for train in trains
        if train["from"].lower() == from_station.lower()
        and train["to"].lower() == to_station.lower()
    ]

    return render_template(
        "search.html",
        trains=results,
        from_station=from_station,
        to_station=to_station,
        journey_date=journey_date
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        return "Invalid email or password!"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
        except:
            conn.close()
            return "Email already registered. Please use another email."

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/booking/<train_number>")
def booking(train_number):

    if "user_id" not in session:
        return redirect(url_for("login"))

    selected_train = next(
        (train for train in trains if train["number"] == train_number),
        None
    )

    if selected_train is None:
        return "Train not found", 404

    return render_template("booking.html", train=selected_train)


@app.route("/save-booking", methods=["POST"])
def save_booking():

    if "user_id" not in session:
        return redirect(url_for("login"))

    train_number = request.form.get("train_number")
    train_name = request.form.get("train_name")
    passenger_name = request.form.get("passenger_name")
    age = request.form.get("age")
    gender = request.form.get("gender")
    phone = request.form.get("phone")

    if not all([train_number, train_name, passenger_name, age, gender, phone]):
        return "Please fill in all passenger details."

    try:
        age = int(age)
        if age < 1 or age > 120:
            return "Please enter a valid age."
    except ValueError:
        return "Please enter a valid age."

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO bookings
        (train_number, train_name, passenger_name, age, gender, phone, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        train_number,
        train_name,
        passenger_name,
        age,
        gender,
        phone,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    return render_template(
        "confirmation.html",
        name=passenger_name,
        age=age,
        gender=gender,
        phone=phone,
        train_name=train_name,
        train_number=train_number
    )

@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    bookings = conn.execute(
        "SELECT * FROM bookings WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template("my_bookings.html", bookings=bookings)

@app.route("/cancel/<int:booking_id>")
def cancel_booking(booking_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM bookings WHERE id = ? AND user_id = ?",
        (booking_id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect(url_for("my_bookings"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
