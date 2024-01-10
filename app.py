from flask import Flask, render_template

app = Flask(__name__)


@app.route('/home')
def indexw():
    return render_template('index.html')

@app.route('/')
def index():
    categories = [
        {'name': 'Category 1', 'description': 'Description 1', 'image': 'dark.jpg'},
        {'name': 'Category 2', 'description': 'Description 2', 'image': 'light.jpg'},
        {'name': 'Category 3', 'description': 'Description 3', 'image': 'dark.jpg'},
        {'name': 'Category 4', 'description': 'Description 4', 'image': 'light.jpg'},
        {'name': 'Category 5', 'description': 'Description 5', 'image': 'img5.jpg'},
        {'name': 'Category 6', 'description': 'Description 6', 'image': 'img6.jpg'}
    ]
    return render_template('index.html', categories=categories)

#https://www.behance.net/gallery/173695679/Blog-Website-Landing-Page-Design?tracking_source=search_projects&l=35

