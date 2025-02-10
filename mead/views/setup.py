from flask import Blueprint, render_template, request, redirect, url_for, current_app
from mead.models import db, Settings, User, Post
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
            db.session.add(settings)

            admin = User(
                username=request.form["admin_username"],
                email=request.form["admin_email"],
                password=generate_password_hash(request.form["admin_password"]),
                role="admin",
            )
            db.session.add(admin)
            db.session.commit()

            # create default page content (Now and Projects)
            # for more info about Now page -> https://now.page/
            static_pages = [
                {
                    "title": "Now",
                    "content":"""Describe what you are doing actually to keep
                    your readers updated. For more info visit  https://now.page/
                    """,
                    "is_page":True
                },
                {
                    "title": "Projects",
                    "content": "Talk about your projects here",
                    "is_page":True
                }
            ]

            for page in static_pages:
                pages = Post(
                    title=page.get("title"),
                    slug=page.get("title").lower(),
                    content=page.get("content"),
                    is_page=page.get("is_page"),
                    author_id=admin.id
                )
                db.session.add(pages)
                db.session.commit()

            return redirect(url_for("blog.index"))
        except Exception as e:
            print(f"Setup error: {e}")
            db.session.rollback()
            return "Error creating blog settings", 500

    return render_template("admin/setup.html")
