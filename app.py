from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "blog.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Automatically create the database and posts table
# when the application starts.
init_db()


@app.route("/")
def home():
    conn = get_db()

    posts = conn.execute("""
        SELECT * FROM posts
        WHERE status = 'published'
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template("index.html", posts=posts)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = get_db()

        conn.execute("""
            INSERT INTO posts (title, content, status, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            title,
            content,
            "draft",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("my_posts"))

    return render_template("create.html")


@app.route("/my-posts")
def my_posts():
    conn = get_db()

    posts = conn.execute("""
        SELECT * FROM posts
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template("my_posts.html", posts=posts)


@app.route("/post/<int:post_id>")
def view_post(post_id):
    conn = get_db()

    post = conn.execute("""
        SELECT * FROM posts
        WHERE id = ?
    """, (post_id,)).fetchone()

    conn.close()

    if post is None:
        return "Post not found", 404

    return render_template("post.html", post=post)


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit(post_id):
    conn = get_db()

    post = conn.execute("""
        SELECT * FROM posts
        WHERE id = ?
    """, (post_id,)).fetchone()

    if post is None:
        conn.close()
        return "Post not found", 404

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn.execute("""
            UPDATE posts
            SET title = ?, content = ?
            WHERE id = ?
        """, (title, content, post_id))

        conn.commit()
        conn.close()

        return redirect(url_for("my_posts"))

    conn.close()

    return render_template("edit.html", post=post)


@app.route("/publish/<int:post_id>")
def publish(post_id):
    conn = get_db()

    conn.execute("""
        UPDATE posts
        SET status = 'published'
        WHERE id = ?
    """, (post_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("my_posts"))


@app.route("/delete/<int:post_id>")
def delete(post_id):
    conn = get_db()

    conn.execute("""
        DELETE FROM posts
        WHERE id = ?
    """, (post_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("my_posts"))


if __name__ == "__main__":
    app.run(debug=True)