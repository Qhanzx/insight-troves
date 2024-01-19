import datetime
import random
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('assets', 'img')  # Static folder for uploads
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # 16 MB limit for uploads

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
db = SQLAlchemy(app)


class Category(db.Model):
    __tablename__ = 'category'

    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String, nullable=False)
    CategoryDesc = db.Column(db.String, nullable=False)

    # Relationship with Posts table
    posts = db.relationship('Post', backref='category', lazy=True)

class Post(db.Model):
    __tablename__ = 'post'

    PostID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String, nullable=False)
    images = db.relationship('Image', backref='post', lazy=True)
    Description = db.Column(db.String, nullable=False)
    Content = db.Column(db.Text, nullable=False)
    CategoryID = db.Column(db.Integer, db.ForeignKey('category.CategoryID'), nullable=False)
    TagID = db.Column(db.Integer, db.ForeignKey('tag.TagID'), nullable=False) 
    DateCreated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    LastModified= db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    ReadTime = db.Column(db.Integer)  # Assuming ReadTime is in minutes

    # Relationships
    images = db.relationship('Image', backref='post', lazy='dynamic')
    #category = db.relationship('Category', backref='post')
    tag = db.relationship('Tag', backref='posts')

    def __repr__(self):
        return f'<Post {self.Title}>'

class Image(db.Model):
    __tablename__ = 'image'
    
    ImageID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('post.PostID'))
    ImagePath = db.Column(db.Text)
    Caption = db.Column(db.String(60))
    AltText = db.Column(db.String(60)) 
    
    # Relationship to the Post class (assuming you have a Post class defined)
    #post = db.relationship("Post", back_populates="images")
@app.route('/d/<int:image_id>')
def display_image(image_id):
    image = Image.query.get(image_id)  # Fetch the image data from the database
    if image:
        return render_template('image.html', image=image)
    else:
        return "Image not found", 404
    
class Tag(db.Model):
    __tablename__ = 'tag'
    
    TagID = db.Column(db.Integer, primary_key=True)
    TagName = db.Column(db.String(30))
    

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Upload function
'''def upload_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None'''

@app.route('/home')
def indexw():
    return render_template('data/create.html')

@app.route('/assets/img/<filename>')
def serve_image(filename):
    return send_from_directory('assets/img', filename)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        try:
            # Get form data
            category_id = request.form['category_id'] # Example category ID, you might want to get this from the form
            title = request.form['title']  # Ensure 'title' is the name attribute in your form
            description = request.form['description']  # Ensure 'description' is the name attribute in your form
            content = request.form['content']  # Ensure 'content' is the name attribute in your form
            read_time = int(request.form['read_time'])  # Ensure 'read_time' is the name attribute in your form
            tag_id = request.form['tag_id']
            # Create a new Post instance
            post = Post(Title=title, Description=description, Content=content,
                        DateCreated=datetime.datetime.utcnow(), LastModified=datetime.datetime.utcnow(),
                        ReadTime=read_time, CategoryID=category_id, TagID=tag_id)
            
            # Add the post instance to the session
            db.session.add(post)
            db.session.flush()  # Flush to get the PostID for the newly created post

            # Commit the session to save the post
            db.session.commit()

            # Handle image file if present
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Save only 'img/filename' in the database
                image_path = os.path.join('img', filename)

                caption = request.form.get('caption', 'Default Caption')
                alt_text = request.form.get('alt_text', 'Default Alt Text')

                image = Image(PostID=post.PostID, ImagePath=image_path, Caption=caption, AltText=alt_text)
                db.session.add(image)
                db.session.commit()

            flash('Post created successfully!', 'success')  # Flash a success message
            return redirect(url_for('post', post_id=post.PostID))  # Redirect to the new post page


        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "error")  # Display error message to the user
            return render_template('create.html')
    
        # Redirect to 'index' after successful POST request
        return redirect(url_for('index'))
                
            
    else:
        categories = Category.query.all()
        tags = Tag.query.all()
        # Render the create post form template if GET request
        return render_template('create.html', categories=categories, tags=tags)
            
        



@app.route('/<int:post_id>/edit/', methods=['GET', 'POST'])
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    images = Image.query.filter_by(PostID=post_id).all()  # Retrieve images associated with the post

    if request.method == 'POST':
        # Update post details
        post.CategoryID = request.form.get('category', 1)  # Assuming a category select field in your form
        post.Title = request.form['title']
        post.Description = request.form['description']
        post.Content = request.form['content']
        post.ReadTime = int(request.form['read_time'])

        # Handle image file if present
        file = request.files.get('image')  # Assuming an image file input in your form
        if file and allowed_file(file.filename):
            # If an image is uploaded, handle the image update
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # If an image already exists, update it; otherwise, create a new image record
            if images:
                image = images[0]  # Assuming one image per post; adjust if there are multiple
                image.ImagePath = filename
                image.Caption = request.form.get('caption', image.Caption)  # Get new caption if provided
                image.AltText = request.form.get('alt_text', image.AltText)  # Get new alt text if provided
            else:
                new_image = Image(PostID=post.PostID, ImagePath=filepath,
                                Caption=request.form.get('caption', 'Default Caption'),
                                AltText=request.form.get('alt_text', 'Default Alt Text'))
                db.session.add(new_image)

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the index page after the post is updated
        return redirect(url_for('index'))

    # Render the edit post form template if GET request
    return render_template('edit.html', post=post, images=images)

@app.route('/<int:post_id>/')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    images = Image.query.filter_by(PostID=post_id).all()
    #image = Image.query.get(image_id)  # Fetch the image data from the database

    # Fetch previous and next posts
    prev_post = Post.query.filter(Post.PostID < post_id).order_by(Post.PostID.desc()).first()
    next_post = Post.query.filter(Post.PostID > post_id).order_by(Post.PostID.asc()).first()

    return render_template('post.html', post=post, images=images, prev_post=prev_post, next_post=next_post)

@app.post('/<int:post_id>/delete/')
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    categories = Category.query.all()
    
    # Create a dictionary to hold categories and their posts
    category_posts = {}
    for category in categories:
        posts = Post.query.filter_by(CategoryID=category.CategoryID).all()
        random.shuffle(posts)
        
        # For each post, get the associated TagName and Image
        post_data = []
        for post in posts:
            tag = Tag.query.filter_by(TagID=post.TagID).first()  # Assuming TagID is associated with Post
            image = Image.query.filter_by(PostID=post.PostID).all()  # Assuming PostID is associated with Image
            
            post_data.append({
                'post': post,
                'tag': tag.TagName if tag else None,  # Get TagName or None if not found
                'image': image  # Get the associated Image
            })
        post_data = post_data[:9]
        category_posts[category] = post_data
    return render_template('index.html', category_posts=category_posts)
    #categories = Category.query.all()
    # Create a dictionary to hold categories and their posts
    #category_posts = {category: Post.query.filter_by(CategoryID=category.CategoryID).all() for category in categories}

    #return render_template('index.html', category_posts=category_posts)

'''@app.route('/categories')
def categories():
    categories = Category.query.all()  # Assuming you have a query to fetch all categories
    posts = Post.query.all()
    return render_template('categories.html', categories=categories, posts=posts)
'''


@app.route('/categories')
def categories():
    # Query to fetch categories
    categories = Category.query.all()
    
    # Data structure to hold categories and their related posts, tags, and images
    category_posts = {}

    for category in categories:
        # Fetch posts related to the category
        posts = Post.query.filter_by(CategoryID=category.CategoryID).all()
        
        # List to hold post data including related tags and images
        post_data = []
        count = 0
        for post in posts:
            if count < 9:
                # Fetch the associated tag and images for each post
                tag = Tag.query.filter_by(TagID=post.TagID).first()
                image = Image.query.filter_by(PostID=post.PostID).all()
                print(f"Post ID: {post.PostID}, Images: {image}")

                # Append post and its related data to the post_data list
                post_data.append({'post': post, 'tag': tag, 'image': image})
                count += 1
            else:
                break
        # Append category and its related posts to the category_data list
        #category_data.append({'category': category, 'posts': post_data})
        category_posts[category] = post_data
        title = 'Categories'
        #random.shuffle(category_posts)

         # Append category and its related posts to the category_posts dictionary
        #category_posts[category.CategoryName] = {'category': category.CategoryID, 'posts': post_data}

    # Render the categories.html template with the structured data
    return render_template('categories.html', category_posts=category_posts, title=title)

@app.route('/categories/<category_name>')
def category_posts(category_name):
    # Fetch the category by its name
    category = Category.query.filter_by(CategoryName=category_name).first()

    # Check if category exists
    if not category:
        # Handle the case where the category is not found
        return "Category not found", 404

    # Fetch posts related to the category
    posts = Post.query.filter_by(CategoryID=category.CategoryID).all()
    
    # List to hold post data including related tags and images
    post_data = []
    for post in posts:
        # Fetch the associated tag and images for each post
        tag = Tag.query.filter_by(TagID=post.TagID).first()
        images = Image.query.filter_by(PostID=post.PostID).all()

        # Append post and its related data to the post_data list
        post_data.append({'post': post, 'tag': tag, 'image': images})

    # Structure the data as expected by the categories.html template
    category_posts = {category_name: post_data}

    # Render the categories.html template with the structured data
    return render_template('categories.html', category_posts=category_posts)

#https://www.behance.net/gallery/173695679/Blog-Website-Landing-Page-Design?tracking_source=search_projects&l=35

