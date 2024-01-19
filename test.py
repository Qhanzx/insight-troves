import datetime
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Category(db.Model):
    __tablename__ = 'categories'

    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String, nullable=False)

    # Relationship with Posts table
    posts = db.relationship('Post', backref='category', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'

    PostID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String, nullable=False)
    Description = db.Column(db.String, nullable=False)
    Content = db.Column(db.Text, nullable=False)
    CategoryID = db.Column(db.Integer, db.ForeignKey('categories.CategoryID'), nullable=False)
    CategoryID = db.Column(db.Integer, db.ForeignKey('categories.CategoryID'), nullable=False)
    DateCreated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    LastModified= db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    ReadTime = db.Column(db.Integer)  # Assuming ReadTime is in minutes

    def __repr__(self):
        return f'<Post {self.Title}>'

class Image(db.Model):
    __tablename__ = 'Image'
    
    ImageID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('Post.PostID'))
    ImagePath = db.Column(db.Text)
    Caption = db.Column(db.String(60))
    AltText = db.Column(db.String(60))
    
    # Relationship to the Post class (assuming you have a Post class defined)
    post = db.relationship("Post", back_populates="images")

class Tag(db.Model):
    __tablename__ = 'Tag'
    
    TagID = db.Column(db.Integer, primary_key=True)
    TagName = db.Column(db.String(30))
    
@app.route('/home')
def indexw():
    return render_template('data/create.html')

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        category = 1
        #module = request.form['module']
        topic  = request.form['topic']
        content = request.form['content']
        read_time = int(request.form['read_time'])

        post = Post(CategoryID=category, Title=topic, Content=content, ReadTime=read_time)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:post_id>/edit/', methods=['GET', 'POST'])
def edit(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        category = 1
        #module = request.form['module']
        topic = request.form['topic']
        content = request.form['content']
        read_time = int(request.form['read_time'])

        post.CategoryID=category 
        post.Title=topic 
        post.Content=content
        post.ReadTime=read_time


        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:post_id>/')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.post('/<int:post_id>/delete/')
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    categories = Category.query.all()
    posts = Post.query.all()
    '''categories = [
        {'name': 'Category 1', 'description': 'Description 1', 'image': 'dark.jpg'},
        {'name': 'Category 2', 'description': 'Description 2', 'image': 'light.jpg'},
        {'name': 'Category 3', 'description': 'Description 3', 'image': 'dark.jpg'},
        {'name': 'Category 4', 'description': 'Description 4', 'image': 'light.jpg'},
        {'name': 'Category 5', 'description': 'Description 5', 'image': 'img5.jpg'},
        {'name': 'Category 6', 'description': 'Description 6', 'image': 'img6.jpg'}
    ]'''
    return render_template('index.html', categories=categories, posts=posts)

#https://www.behance.net/gallery/173695679/Blog-Website-Landing-Page-Design?tracking_source=search_projects&l=35

