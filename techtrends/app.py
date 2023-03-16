from distutils.debug import DEBUG
import logging
import sqlite3
from urllib import response

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    global connection_count 
    connection_count += 1
    
    return connection

def db_close(connection):
    connection.close()
    # global connection_count 
    # connection_count -= 1

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    db_close(connection)
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    db_close(connection)
    return render_template('index.html', posts=posts)

@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT Count() FROM posts').fetchone()[0]
    db_close(connection)

    global connection_count

    response = app.response_class(
        response=json.dumps({"db_connection_count": connection_count, "post_count": posts}),
        status=200,
        mimetype='application/json'
    )
    return response


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Article wit id ' + str(post_id) + ' does not exits.')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article \"' + post['title'] + '\" retrieved!')    
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info('Acticle \"' + title + '\" created!')

            return redirect(url_for('index'))

    return render_template('create.html')



# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s, %(message)s', datefmt='%m/%d/%Y, %H:%M:%S', level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
