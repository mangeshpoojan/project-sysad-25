import time

import mysql.connector
from flask import (
    Flask,
    Response,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_bcrypt import Bcrypt
from supabase import Client, create_client

import logic

app = Flask(__name__)
app.secret_key = "supersecretkey"  # temp
bcrypt = Bcrypt(app)

SUPABASE_URL = "https://tfuweyqhbyyczjikzlvt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRmdXdleXFoYnl5Y3pqaWt6bHZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMDI2MjEsImV4cCI6MjA3NzU3ODYyMX0.pOb40g3g4rrIUqQ7RTK4f2qAPR2pbujMr3fhrWSYR-o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

connection = mysql.connector.connect(
    host="10.130.150.6", user="admin", password="adminiswhimsical", database="SL", port=3306
)

cursor = connection.cursor()


@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        res = supabase.table("users").select("*").eq("username", username).execute()
        if res.data:
            user = res.data[0]
            hash = user["password_hash"]
            if bcrypt.check_password_hash(hash, password):
                session["user"] = username
                return redirect(url_for("home"))
            else:
                return render_template("login.html", error="Invalid password")
        else:
            return render_template("login.html", error="User not found")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        Paraphrase = "0xsahil"
        username = request.form.get("username")
        password = request.form.get("password")
        paraphrase = request.form.get("paraphrase")

        print(username, password, paraphrase)
        if paraphrase == Paraphrase:
            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            existing = supabase.table("users").select("*").eq("username", username).execute()
            if existing.data:
                return render_template("register.html", error="Username already exists")

            response = (
                supabase.table("users").insert({"username": username, "password_hash": hashed}).execute()
            )
            print("Insert response:", response)

            return redirect(url_for("login"))
        return render_template("register.html")
    return render_template("register.html")


@app.route("/home")
def home():
    #check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("home.html")


@app.route("/internet_disable", methods=["GET", "POST"])
def internet_disable():
    if "user" not in session:
        return redirect(url_for("login"))

    selected_lab = None
    machine_numbers = []

    if request.method == "POST":
        selected_lab = request.form.get("lab", "").strip()
        raw_machines = request.form.get("machines", "").strip()

        machine_numbers = []
        for num in raw_machines.split():
            if num.isdigit():
                machine_numbers.append(int(num))

    return render_template(
        "internet_disable.html",
        selected_lab=selected_lab,
        machine_numbers=machine_numbers,
    )


@app.route("/internet_enable", methods=["GET", "POST"])
def internet_enable():
    if "user" not in session:
        return redirect(url_for("login"))

    selected_lab = None
    machine_numbers = []

    if request.method == "POST":
        selected_lab = request.form.get("lab", "").strip()
        raw_machines = request.form.get("machines", "").strip()

        machine_numbers = []
        for num in raw_machines.split():
            if num.isdigit():
                machine_numbers.append(int(num))
        print("Selected Lab:", selected_lab)
        print("Machine Numbers:", machine_numbers)

    return render_template(
        "internet_enable.html",
        selected_lab=selected_lab,
        machine_numbers=machine_numbers,
    )


@app.route("/free_space", methods=["GET", "POST"])
def free_space():
    if "user" not in session:
        return redirect(url_for("login"))

    query = """
        SELECT m.*
        FROM machine_storage_log m
        JOIN (
            SELECT lab, machine_number, MAX(record_time) AS latest_time
            FROM machine_storage_log
            GROUP BY lab, machine_number
        ) x
        ON m.lab = x.lab
        AND m.machine_number = x.machine_number
        AND m.record_time = x.latest_time;
        """
    cursor.execute(query)

    data_list = cursor.fetchall()
    return render_template("free_space.html", free_space=data_list)


@app.route("/check_submit")
def check_submit():
    if "user" not in session:
        return redirect(url_for("login"))

    return "check_submit"


@app.route("/feedback")
def feedback():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("feedback.html")


@app.route("/feedback/previous", methods=["GET", "POST"])
def previous():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        response = supabase.table("feedback").select("*").order("created_at", desc=True).execute()
        feedback_list = response.data
        print("Fetched feedback data:", feedback_list[0])

    except Exception as e:
        print(f"Error fetching feedback data from Supabase: {e}")
        feedback_list = []
    return render_template("previous_feedback.html", data=feedback_list)


@app.route("/feedback/previous/update_resolve/<int:id>", methods=["GET"])
def update_resolve(id):
    if "user" not in session:
        return redirect(url_for("login"))

    response = supabase.table("feedback").update({"progress": "resolved"}).eq("id", id).execute()
    response = supabase.table("feedback").select("*").order("created_at", desc=True).execute()
    feedback_list = response.data
    return render_template("previous_feedback.html", data=feedback_list)


@app.route("/feedback/previous/resolved", methods=["GET", "POST"])
def resolved():
    if "user" not in session:
        return redirect(url_for("login"))

    response = supabase.table("feedback").select("*").eq("progress", "resolved").execute()
    feedback_list = response.data
    print(feedback_list[0])
    return render_template("resolved.html", data=feedback_list)


@app.route("/feedback/previous/unresolved", methods=["GET", "POST"])
def unresolved():
    if "user" not in session:
        return redirect(url_for("login"))

    response = supabase.table("feedback").select("*").eq("progress", "unresolved").execute()
    feedback_list = response.data
    print(feedback_list[0])
    return render_template("unresolved.html", data=feedback_list)


@app.route("/feedback/submit", methods=["GET", "POST"])
def submit():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        lab = request.form.get("lab", "").strip()
        computer_number = int(request.form.get("computer_number", "").strip())
        issue = request.form.get("issue", "").strip()
        text = request.form.get("issue_details", "").strip()
        print(lab, computer_number, issue, text)

        try:
            response = supabase.table("feedback").insert(
                {
                    "lab": lab,
                    "computer_number": computer_number,
                    "issue": issue,
                    "issue_details": text,
                    "progress": "unresolved",
                }
            ).execute()
        except:
            return redirect(url_for("feedback"))

    return redirect(url_for("feedback"))


@app.route("/free_space_analytics", methods=["GET", "POST"])
def analytics():
    if "user" not in session:
        return redirect(url_for("login"))
    bar_data_list = logic.get_latest_machine_data(cursor)
    logic.generate_disk_space_chart(bar_data_list, app.static_folder)
    logic.generate_disk_space_percentage_chart(bar_data_list, app.static_folder)
    logic.generate_disk_space_pie_chart(cursor, app.static_folder)

    current_time = int(time.time())
    return render_template("free_space_analytics.html", timestamp=current_time)


@app.route("/system_on_analytics", methods=["GET", "POST"])
def free_space_analytics():
    if "user" not in session:
        return redirect(url_for("login"))

    uptime_query = """
        SELECT m.lab, m.machine_number, m.weeks, m.days, m.hours
        FROM machine_uptimes_log m
        JOIN (
            SELECT lab, machine_number, MAX(record_time) AS latest_time
            FROM machine_uptimes_log
            GROUP BY lab, machine_number
        ) x
        ON m.lab = x.lab
        AND m.machine_number = x.machine_number
        AND m.record_time = x.latest_time;
    """
    cursor.execute(uptime_query)
    uptime_rows = cursor.fetchall()
    # print("hellllllllllllllllllll",uptime_rows)
    logic.generate_uptime_histogram(uptime_rows, app.static_folder)

    current_time = int(time.time())
    return render_template("system_on_analytics.html", timestamp=current_time)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
