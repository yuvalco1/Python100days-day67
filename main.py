from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

ckeditor = CKEditor()


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor.init_app(app)
Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost).order_by(BlogPost.id))
    blog_posts = result.scalars().all()
    posts = []
    for post in blog_posts:
        posts.append(post.__dict__)
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


class new_post(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle')
    author = StringField('Your Name')
    img_url = StringField('Blog Image URL', validators=[URL()])
    body = CKEditorField('Blog content')
    submit = SubmitField('Submit Post')


@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    form = new_post()
    if form.validate_on_submit():
        to_add_post = BlogPost(title = form.title.data,
                            subtitle = form.subtitle.data,
                            author = form.author.data,
                            img_url = form.img_url.data,
                            body = form.body.data,
                            date = date.today().strftime("%B %d, %Y"))
        db.session.add(to_add_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = new_post()
    if form.validate_on_submit():
        requested_post.title = form.title.data
        requested_post.subtitle = form.subtitle.data
        requested_post.author = form.author.data
        requested_post.img_url = form.img_url.data
        requested_post.body = form.body.data
        requested_post.date = date.today().strftime("%B %d, %Y")
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = requested_post.title
        form.subtitle.data = requested_post.subtitle
        form.author.data = requested_post.author
        form.img_url.data = requested_post.img_url
        form.body.data = requested_post.body
    return render_template("make-post.html", form=form, is_edit=True)

# delete_post() to remove a blog post from the database

@app.route("/del-post/<int:post_id>", methods=["GET", "POST"])
def del_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
