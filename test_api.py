import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app import app as flask_app
from database import db


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["WTF_CSRF_ENABLED"] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.drop_all()


# ─────────────────────────────────────────
# POSITIVE TEST CASES
# ─────────────────────────────────────────

def test_get_all_posts_empty(client):
    """GET /api/posts returns empty list when no posts exist"""
    response = client.get("/api/posts")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_post(client):
    """POST /api/posts creates a new post successfully"""
    response = client.post("/api/posts", json={
        "title": "Test Post",
        "content": "This is test content",
        "author": "testuser",
        "tags": "test",
        "category": "general"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Post created successfully"
    assert "id" in data


def test_get_all_posts_after_create(client):
    """GET /api/posts returns list with posts after creating one"""
    client.post("/api/posts", json={
        "title": "Test Post",
        "content": "This is test content",
        "author": "testuser",
        "tags": "test",
        "category": "general"
    })
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Post"


def test_get_single_post(client):
    """GET /api/posts/<id> returns a single post"""
    client.post("/api/posts", json={
        "title": "Single Post",
        "content": "Content here",
        "author": "testuser",
        "tags": "single",
        "category": "general"
    })
    response = client.get("/api/posts/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Single Post"


def test_update_post(client):
    """PUT /api/posts/<id> updates an existing post"""
    client.post("/api/posts", json={
        "title": "Old Title",
        "content": "Old content",
        "author": "testuser",
        "tags": "old",
        "category": "general"
    })
    response = client.put("/api/posts/1", json={
        "title": "New Title",
        "content": "New content"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Post updated successfully"


def test_delete_post(client):
    """DELETE /api/posts/<id> deletes a post"""
    client.post("/api/posts", json={
        "title": "To Delete",
        "content": "Delete me",
        "author": "testuser",
        "tags": "",
        "category": "general"
    })
    response = client.delete("/api/posts/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Post deleted successfully"


# ─────────────────────────────────────────
# NEGATIVE TEST CASES
# ─────────────────────────────────────────

def test_get_nonexistent_post(client):
    """GET /api/posts/<id> returns 404 if post does not exist"""
    response = client.get("/api/posts/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Post not found"


def test_create_post_missing_title(client):
    """POST /api/posts returns 400 if title is missing"""
    response = client.post("/api/posts", json={
        "content": "No title here",
        "author": "testuser",
        "category": "general"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_post_missing_content(client):
    """POST /api/posts returns 400 if content is missing"""
    response = client.post("/api/posts", json={
        "title": "No Content Post",
        "author": "testuser",
        "category": "general"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_post_missing_author(client):
    """POST /api/posts returns 400 if author is missing"""
    response = client.post("/api/posts", json={
        "title": "No Author Post",
        "content": "Some content",
        "category": "general"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_nonexistent_post(client):
    """PUT /api/posts/<id> returns 404 if post does not exist"""
    response = client.put("/api/posts/999", json={"title": "Ghost"})
    assert response.status_code == 404
    assert response.get_json()["error"] == "Post not found"


def test_delete_nonexistent_post(client):
    """DELETE /api/posts/<id> returns 404 if post does not exist"""
    response = client.delete("/api/posts/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Post not found"