from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from slugify import slugify

db = SQLAlchemy()

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_name = db.Column(db.String(200), nullable=False)
    blog_description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="user")
    posts = db.relationship("Post", backref="author", lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    posts = db.relationship("Post", backref="category", lazy=True)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        db.session.add(self)
        db.session.commit()


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        db.session.add(self)
        db.session.commit()

tags_posts = db.Table(
    "tags_posts",
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    external_url = db.Column(db.String(500))
    is_page = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    # relationships
    page_views = db.relationship("PageView", backref="post", lazy=True)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.title)
        db.session.add(self)
        db.session.commit()


class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    referrer = db.Column(db.String(500))
    country = db.Column(db.String(2))
    device = db.Column(db.String(50))
    browser = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)

    # foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
