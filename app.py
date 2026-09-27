from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "blog.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE DATABASE ----------------

def create_database():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    conn = get_db_connection()

    posts = conn.execute("""
        SELECT * FROM posts
        WHERE status = 'published'
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template("index.html", posts=posts)


# ---------------- CREATE POST ----------------

@app.route("/create", methods=["GET", "POST"])
def create_post():

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO posts (title, content, status)
            VALUES (?, ?, 'draft')
        """, (title, content))

        conn.commit()
        conn.close()

        return redirect(url_for("my_posts"))

    return render_template("create.html")


# ---------------- MY POSTS ----------------

@app.route("/my-posts")
def my_posts():

    conn = get_db_connection()

    posts = conn.execute("""
        SELECT * FROM posts
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template("my_posts.html", posts=posts)


# ---------------- VIEW POST ----------------

@app.route("/post/<int:post_id>")
def view_post(post_id):

    conn = get_db_connection()

    post = conn.execute("""
        SELECT * FROM posts
        WHERE id = ?
    """, (post_id,)).fetchone()

    conn.close()

    if post is None:
        return "Post not found", 404

    return render_template("post.html", post=post)


# ---------------- EDIT POST ----------------

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):

    conn = get_db_connection()

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

        return redirect(url_for("view_post", post_id=post_id))

    conn.close()

    return render_template("edit.html", post=post)


# ---------------- PUBLISH POST ----------------

@app.route("/publish/<int:post_id>")
def publish_post(post_id):

    conn = get_db_connection()

    conn.execute("""
        UPDATE posts
        SET status = 'published'
        WHERE id = ?
    """, (post_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("my_posts"))


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)