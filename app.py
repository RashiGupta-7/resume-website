# app.py
import os
import csv
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

# Try to import SendGrid — if it's not installed, keep working without it
SENDGRID_AVAILABLE = False
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except Exception:
    SENDGRID_AVAILABLE = False

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_in_production")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM = os.environ.get("SENDGRID_FROM", "no-reply@example.com")
SENDGRID_TO = os.environ.get("SENDGRID_TO", "rashigupta.work07@gmail.com")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please fill all fields.", "error")
        return redirect(url_for("index") + "#contact")

    # If SendGrid is installed and API key present, try to send email
    if SENDGRID_AVAILABLE and SENDGRID_API_KEY:
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            mail = Mail(
                from_email=SENDGRID_FROM,
                to_emails=SENDGRID_TO,
                subject=f"Portfolio contact from {name}",
                plain_text_content=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            )
            sg.send(mail)
            flash("Thanks — your message was sent. I will reply soon.", "success")
            return redirect(url_for("index") + "#contact")
        except Exception as e:
            # If email fails, fallback to saving locally
            print("SendGrid send error:", e)
            save_submission(name, email, message)
            flash("Message saved (email failed). I'll check it manually.", "warning")
            return redirect(url_for("index") + "#contact")

    # Fallback path: Save locally to submissions.csv
    save_submission(name, email, message)
    flash("Thanks — your message was recorded. (Email not configured.)", "success")
    return redirect(url_for("index") + "#contact")


def save_submission(name, email, message):
    """Append submissions to a local CSV file (useful for dev & fallback)."""
    fname = os.path.join(os.path.dirname(__file__), "submissions.csv")
    exists = os.path.exists(fname)
    with open(fname, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["name", "email", "message"])
        writer.writerow([name, email, message])


# Serve the resume PDF from project root (Flask static would also work)
@app.route("/Resume-Rashi_Gupta.pdf")
def resume():
    # send_from_directory or send_static_file can be used depending on location
    return app.send_static_file("../Resume-Rashi_Gupta.pdf")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
