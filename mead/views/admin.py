from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from mead.models import db, Post, Category, Tag, PageView
from mead.utils import save_image, markdown_to_html

admin = Blueprint("admin", __name__)


@admin.route("/admin")
@login_required
def dashboard():
    if current_user.role != "admin":
        return redirect(url_for("main.home"))

    posts = Post.query.all()
    categories = Category.query.all()
    tags = Tag.query.all()

    total_views = PageView.query.filter_by(is_admin=False).count()
    unique_visitors = (
        PageView.query.filter_by(is_admin=False).distinct(PageView.ip_address).count()
    )

    return render_template(
        "admin/dashboard.html",
        posts=posts,
        categories=categories,
        tags=tags,
        total_views=total_views,
        unique_visitors=unique_visitors,
    )
