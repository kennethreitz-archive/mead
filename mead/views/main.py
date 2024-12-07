from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from mead.models import db, Settings, Post, PageView, User

main = Blueprint("main", __name__)


@main.route("/")
def home():
    settings = Settings.query.first()
    if settings is None:
        return render_template("admin/welcome.html")

    recent_posts = (
        Post.query.filter_by(is_page=False)
        .order_by(Post.created_at.desc())
        .limit(3)
        .all()
    )

    try:
        popular_posts = (
            Post.query.join(Post.page_views)
            .filter(Post.is_page == False)
            .filter(PageView.is_admin == False)
            .group_by(Post.id)
            .order_by(db.func.count(PageView.id).desc())
            .limit(5)
            .all()
        )
    except Exception:
        popular_posts = []

    return render_template(
        "main/home.html",
        settings=settings,
        recent_posts=recent_posts,
        popular_posts=popular_posts,
    )


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))

        flash("Invalid username or password", "error")

    return render_template("main/login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("main.home"))
