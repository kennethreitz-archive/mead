from flask import Blueprint, render_template, redirect, url_for, request
from mead.models import Post, Category, Tag
from mead.utils import track_page_view

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from markdown2 import markdown
from slugify import slugify
from datetime import datetime
from mead.models import db, Post, Category, Tag

blog = Blueprint("blog", __name__)


@blog.route("/blog")
@track_page_view
def index():
    posts = (
        Post.query.filter_by(is_page=False)
        .order_by(Post.updated_at.desc() if Post.updated_at else Post.created_at.desc())
        .all()
    )
    return render_template("blog/index.html", posts=posts)

@blog.route("/categories")
@login_required
def list_categories():
    categories = Category.query.all()
    return render_template("blog/categories/list.html", categories=categories)

@blog.route("/category/<string:slug>")
def list_category_posts_by_slug(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = (
        Post.query.filter_by(category_id=category.id, is_page=False)
        .order_by(Post.created_at.desc())
        .all()
    )
    return render_template("blog/index.html", category=category, posts=posts)

@blog.route("/categories/new", methods=["GET", "POST"])
@login_required
def new_category():
    if request.method == "POST":
        name = request.form.get("name")

        if Category.query.filter_by(name=name).first():
            flash("Category already exists", "error")
            return redirect(url_for("blog.new_category"))

        category = Category(name=name)
        category.save()
        flash("Category created successfully", "success")
        return redirect(url_for("blog.list_categories"))

    return render_template("blog/categories/form.html")


@blog.route("/categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)

    if request.method == "POST":
        name = request.form.get("name")

        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash("Category name already taken", "error")
            return redirect(url_for("blog.edit_category", id=id))

        category.name = name
        category.slug = slugify(name)
        db.session.commit()
        flash("Category updated successfully", "success")
        return redirect(url_for("blog.list_categories"))

    return render_template("blog/categories/form.html", category=category)


@blog.route("/categories/<int:id>/delete")
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully", "success")
    return redirect(url_for("blog.list_categories"))


@blog.route("/tags")
@login_required
def list_tags():
    tags = Tag.query.all()
    return render_template("blog/tags/list.html", tags=tags)


@blog.route("/tags/new", methods=["GET", "POST"])
@login_required
def new_tag():
    if request.method == "POST":
        name = request.form.get("name")

        if Tag.query.filter_by(name=name).first():
            flash("Tag already exists", "error")
            return redirect(url_for("blog.new_tag"))

        tag = Tag(name=name)
        tag.save()
        flash("Tag created successfully", "success")
        return redirect(url_for("blog.list_tags"))

    return render_template("blog/tags/form.html")


@blog.route("/tags/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)

    if request.method == "POST":
        name = request.form.get("name")

        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash("Tag name already taken", "error")
            return redirect(url_for("blog.edit_tag", id=id))

        tag.name = name
        tag.slug = slugify(name)
        db.session.commit()
        flash("Tag updated successfully", "success")
        return redirect(url_for("blog.list_tags"))

    return render_template("blog/tags/form.html", tag=tag)


@blog.route("/tags/<int:id>/delete")
@login_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash("Tag deleted successfully", "success")
    return redirect(url_for("blog.list_tags"))


@blog.route("/posts")
@login_required
def list_posts():
    posts = Post.query.filter_by(is_page=False).order_by(Post.created_at.desc()).all()
    return render_template("blog/posts/list.html", posts=posts)


@blog.route("/posts/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_id = request.form.get("category_id")
        tag_ids = request.form.getlist("tags")
        external_url = request.form.get("external_url")
        is_page = bool(request.form.get("is_page"))

        post = Post(
            title=title,
            content=content,
            category_id=category_id or None,
            external_url=external_url,
            author_id=current_user.id,
            is_page=is_page,
        )

        if tag_ids:
            post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

        post.save()
        flash("Post created successfully", "success")

        if is_page:
            return redirect(url_for("blog.list_pages"))
        return redirect(url_for("blog.list_posts"))

    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template("blog/posts/form.html", categories=categories, tags=tags)


@blog.route("/posts/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        post.category_id = request.form.get("category_id") or None
        post.external_url = request.form.get("external_url")
        post.updated_at = datetime.utcnow()
        post.is_page = bool(request.form.get("is_page"))

        tag_ids = request.form.getlist("tags")
        if tag_ids:
            post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        else:
            post.tags = []

        post.save()
        flash("Post updated successfully", "success")

        if post.is_page:
            return redirect(url_for("blog.list_pages"))
        return redirect(url_for("blog.list_posts"))

    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template(
        "blog/posts/form.html", post=post, categories=categories, tags=tags
    )


@blog.route("/posts/<int:id>/delete")
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully", "success")
    return redirect(url_for("blog.list_posts"))

@blog.route("/pages")
@login_required
def list_pages():
    pages = Post.query.filter_by(is_page=True).order_by(Post.created_at.desc()).all()
    print(pages)
    return render_template("blog/pages.html", pages=pages, is_page=True)

@blog.route("/post/<slug>")
@track_page_view
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.external_url:
        return redirect(post.external_url)
    return render_template("blog/post.html", post=post)


