from flask import Blueprint, render_template, request, redirect, url_for, current_app
from mead.models import db, Settings, User
from werkzeug.security import generate_password_hash

setup = Blueprint("setup", __name__)


@setup.route("/setup", methods=["GET", "POST"])
def setup_blog():
    """
    When the blog is launched the first time, we need to set it up !
    """
    if Settings.query.first() is not None:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        try:
            settings = Settings(
                blog_name=request.form["blog_name"],
                blog_description=request.form["blog_description"],
            )

            admin = User(
                username=request.form["admin_username"],
                email=request.form["admin_email"],
                password=generate_password_hash(request.form["admin_password"]),
                role="admin",
            )

            db.session.add(settings)
            db.session.add(admin)
            db.session.commit()

            return redirect(url_for("index"))
        except Exception as e:
            print(f"Setup error: {e}")
            db.session.rollback()
            return "Error creating blog settings", 500

    return render_template("admin/setup.html")
