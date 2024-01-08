from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('post.html')



#https://www.behance.net/gallery/173695679/Blog-Website-Landing-Page-Design?tracking_source=search_projects&l=35