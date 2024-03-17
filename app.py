#creating environment - python -m venv env
#Activate it:   .\env\Scripts\activate
from flask_mysqldb import MySQL

import yaml
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = os.urandom(16)



UPLOAD_FOLDER = 'static/assets/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)

@app.route('/')
def index():
    category_filter = request.args.get('category')
    cur = mysql.connection.cursor()
    

    query_posts = """
        SELECT p.id, p.title, c.name AS category_name, p.added_by, p.body, p.image, p.created_at
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
    """
    if category_filter:
        query_posts += " WHERE c.id = %s"
        cur.execute(query_posts, [category_filter])
    else:
        cur.execute(query_posts)
    posts_tuples = cur.fetchall()
    
    #print(posts_tuples)

    
    posts = [
        {'id': post[0], 'title': post[1], 'category_name': post[2], 'added_by': post[3], 'body': post[4] ,'image': post[5] ,'created_at': post[6] }
        for post in posts_tuples
    ]

 
    cur.execute("SELECT id, name FROM categories")
    categories_tuples = cur.fetchall()
    categories = [{'id': cat[0], 'name': cat[1]} for cat in categories_tuples]

    cur.close()
    return render_template('index.html', posts=posts, categories=categories)



@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post_detail(id):
    cur = mysql.connection.cursor()

    cur.execute("SELECT title, body, added_by, id FROM posts WHERE id = %s", [id])
    post_tuple = cur.fetchone()
    
    post = {'title': post_tuple[0], 'body': post_tuple[1], 'added_by': post_tuple[2] ,'id': post_tuple[3]  }  if post_tuple else None

   
    cur.execute("SELECT body, added_by, created_at, id FROM comments WHERE post_id = %s ORDER BY created_at DESC", [id])
    comments_tuples = cur.fetchall()
    #
    comments = [{'body': comment[0], 'added_by': comment[1], 'created_at': comment[2], 'id': comment[3] } for comment in comments_tuples]

   
    if request.method == 'POST':
        comment_body = request.form['comment']
        added_by = request.form.get('username', 'Anonymous')
        cur.execute("INSERT INTO comments (post_id, body, added_by) VALUES (%s, %s, %s)", (id, comment_body, added_by))
        mysql.connection.commit()
       
        return redirect(url_for('post_detail', id=id))

    cur.close()
    return render_template('post.html', post=post, comments=comments)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
  
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()
    cur.close()

    if request.method == 'POST':
   
        file = request.files.get('file')
        if file and allowed_file(file.filename):
         
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

         
            title = request.form['title']
            body = request.form['body']
            category_id = request.form['category']
            added_by = 'Tawanda Dadirai'

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO posts (title, body, category_id, added_by, image) VALUES (%s, %s, %s, %s, %s)",
                        (title, body, category_id, added_by, filename))
            mysql.connection.commit()
            cur.close()

            flash('Post added successfully!', 'success')
            return redirect(url_for('index'))
        else:
          
            flash('An error occurred with the file upload', 'error')

   
        return render_template('addpost.html', categories=categories)
    else:
    
        return render_template('addpost.html', categories=categories)




@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        
        title = request.form['title']
        body = request.form['body']
        category_id = request.form['category']

        try:
           
            update_query = "UPDATE posts SET title = %s, body = %s, category_id = %s WHERE id = %s"
            cur.execute(update_query, (title, body, category_id, id))
            mysql.connection.commit()
            flash('Post updated successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'An error occurred while updating the post: {e}', 'error')
        finally:
            cur.close()
        return redirect(url_for('edit_post', id=id))
    else:
        
        try:
            cur.execute("SELECT title, body, category_id FROM posts WHERE id = %s", (id,))
            post = cur.fetchone()
            if post:
                post = {'title': post[0], 'body': post[1], 'category_id': post[2], 'id': id}
            else:
                flash('Post not found', 'error')
                return redirect(url_for('index'))

            cur.execute("SELECT id, name FROM categories")
            categories = [{'id': cat[0], 'name': cat[1]} for cat in cur.fetchall()]
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            categories = []  
        finally:
            cur.close()
        return render_template('edit_post.html', post=post, categories=categories)




@app.route('/delete_post/<int:id>', methods=['GET'])
def delete_post(id):
    cur = mysql.connection.cursor()
    
   
    cur.execute("DELETE FROM comments WHERE post_id = %s", [id])
    
  
    cur.execute("DELETE FROM posts WHERE id = %s", [id])
    
    mysql.connection.commit()
    flash('Post and corresponding comments deleted successfully!', 'success')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
