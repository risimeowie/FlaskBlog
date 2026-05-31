from flask import Blueprint, jsonify, request
from database import db
from models import Post
import time
import re

api = Blueprint("api", __name__, url_prefix="/api")


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


def post_to_dict(post):
    return {
        "id": post.id,
        "title": post.title,
        "tags": post.tags,
        "content": post.content,
        "author": post.author,
        "views": post.views,
        "time_stamp": post.time_stamp,
        "last_edit_time_stamp": post.last_edit_time_stamp,
        "category": post.category,
        "url_id": post.url_id,
        "abstract": post.abstract,
    }


# ── GET ALL POSTS ─────────────────────────────────────────────────────
@api.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    return jsonify([post_to_dict(p) for p in posts]), 200


# ── GET SINGLE POST ───────────────────────────────────────────────────
@api.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post_to_dict(post)), 200


# ── CREATE POST ───────────────────────────────────────────────────────
@api.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    author = data.get("author", "").strip()
    if not author:
        return jsonify({"error": "author is required"}), 400

    now = int(time.time())
    url_id = slugify(title) + "-" + str(now)

    post = Post(
        title=title,
        tags=data.get("tags", ""),
        content=content,
        banner=b"",
        author=author,
        views=0,
        time_stamp=now,
        last_edit_time_stamp=now,
        category=data.get("category", "general"),
        url_id=url_id,
        abstract=data.get("abstract", ""),
    )

    db.session.add(post)
    db.session.commit()
    return jsonify({"message": "Post created successfully", "id": post.id}), 201


# ── UPDATE POST ───────────────────────────────────────────────────────
@api.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    post.title = data.get("title", post.title)
    post.tags = data.get("tags", post.tags)
    post.content = data.get("content", post.content)
    post.author = data.get("author", post.author)
    post.category = data.get("category", post.category)
    post.abstract = data.get("abstract", post.abstract)
    post.last_edit_time_stamp = int(time.time())

    db.session.commit()
    return jsonify({"message": "Post updated successfully"}), 200


# ── DELETE POST ───────────────────────────────────────────────────────
@api.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"}), 200