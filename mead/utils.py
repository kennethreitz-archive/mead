import functools
from flask import request, current_app
from flask_login import current_user
import user_agents
import markdown2
from werkzeug.utils import secure_filename
import os
from mead.models import db, PageView, Post


def track_page_view(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            ua_string = request.user_agent.string
            user_agent = user_agents.parse(ua_string)

            post_id = None
            if "slug" in kwargs:
                post = Post.query.filter_by(slug=kwargs["slug"]).first()
                if post:
                    post_id = post.id
                    
            if post_id:
                page_view = PageView(
                    url=request.path,
                    ip_address=request.remote_addr,
                    user_agent=ua_string,
                    referrer=request.referrer,
                    device=user_agent.device.family,
                    browser=user_agent.browser.family,
                    is_admin=current_user.is_authenticated and current_user.role == "admin",
                    post_id=post_id,
                )
                db.session.add(page_view)
                db.session.commit()

        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        return filename
    return None


def markdown_to_html(content):
    extras = {
        "tables": None,
        "code-friendly": None,
        "fenced-code-blocks": None,
        "toc": None,
    }
    return markdown2.markdown(content, extras=extras)
