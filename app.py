import os
import csv
from flask import Flask, render_template, request, redirect, url_for, flash
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET", "change_this")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM = os.environ.get("SENDGRID_FROM", "no-reply@example.com")
SENDGRID_TO = os.environ.get("SENDGRID_TO", "rashigupta.work07@gmail.com")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not email or not message:
        flash("Please fill all fields.", "error")
        return redirect(url_for("index") + "#contact")

    if SENDGRID_API_KEY:
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            email_obj = Mail(
                from_email=SENDGRID_FROM,
                to_emails=SENDGRID_TO,
                subject=f"Portfolio Contact — {name}",
                plain_text_content=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            )
            sg.send(email_obj)
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for("index") + "#contact")
        except Exception as e:
            print("SendGrid error:", e)
            save_submission(name, email, message)
            flash("Could not send email; saved locally.", "warning")
            return redirect(url_for("index") + "#contact")
    else:
        save_submission(name, email, message)
        flash("Email service not configured — saved locally.", "warning")
        return redirect(url_for("index") + "#contact")


def save_submission(name, email, message):
    file_path = "submissions.csv"
    exists = os.path.exists(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["name", "email", "message"])
        writer.writerow([name, email, message])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
