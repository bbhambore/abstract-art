from flask import Flask, render_template, flash, session, request, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import io
import base64
import PIL.Image
from flask_ckeditor import CKEditor

from PIL import Image
import io

import yaml
import os

app = Flask(__name__)
Bootstrap(app)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)

CKEditor(app)

@app.route('/')
def index():
    if session:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM ((SELECT * FROM question where user_id = " + str(session['userId']) + \
        ") as q NATURAL JOIN (SELECT * FROM image) as i)"
        resultValue = cur.execute(query)
        if resultValue > 0:
            results = cur.fetchall()
            cur.close()
            for result in results:
                img = base64.b64encode(result["image_blob"]).decode("utf-8")
                result["image_blob"] = img
            return render_template('index.html', results = results)
        cur.close()
        return render_template('index.html', results = None)
    else:
        return redirect('/login')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/blogs/<int:id>/')
def blogs(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if resultValue > 0:
        blog = cur.fetchone()
        return render_template('blogs.html', blog = blog)
    return 'Blog not found'

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            userDetails = request.form
            print(userDetails['last_name'])
            if userDetails['password'] != userDetails['confirm_password']:
                flash('Passwords do not match! Try again.', 'danger')
                return render_template('register.html')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO login (password, user_type, first_name, last_name, email)" \
            "VALUES(%s, %s, %s, %s, %s)", (generate_password_hash(userDetails['password']), \
            userDetails['user_type'], userDetails['first_name'], userDetails['last_name'], userDetails['email']))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        except:
            flash('User could not be registered', 'danger')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        userDetails = request.form
        email = userDetails['email']
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM login WHERE email = %s", ([email]))
        if resultValue > 0:
            user = cur.fetchone()
            print(user)
            if check_password_hash(user['password'], userDetails['password']):
                session['login'] = True
                session['firstName'] = user['first_name']
                session['lastName'] = user['last_name']
                session['userId'] = user['user_id']
                print(session)
                flash('Welcome ' + session['firstName'] + '! You have been successfully logged in', 'success')
            else:
                cur.close()
                flash('Password do not match', 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')

@app.route('/write-blog/', methods = ['GET', 'POST'])
def write_blog():
    if session:
        if request.method == "POST":
            blogpost = request.form
            title = blogpost['title']
            body = blogpost['body']
            author = session['firstName'] + ' ' + session['lastName']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO blog (title, body, author) VALUES (%s, %s, %s)", (title, body, author))
            mysql.connection.commit()
            cur.close()
            flash("Successfully posted new blog", 'success')
            return redirect('/')
        return render_template('write-blog.html')
    else:
        return redirect('/login')

@app.route('/my-blogs/', methods = ['GET'])
def my_blogs():
    if session:
        author = session['firstName'] + ' ' + session['lastName']
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * FROM blog WHERE author = %s", [author])
        if result_value > 0:
            my_blogs = cur.fetchall()
            return render_template('my-blogs.html', my_blogs = my_blogs)
        else:
            return render_template('my-blogs.html', my_blogs = None)
    else:
        return redirect('/login')

@app.route('/edit-blog/<int:id>/', methods = ['GET', 'POST'])
def edit_blog(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cur.execute("UPDATE blog SET title = %s, body = %s WHERE blog_id = %s", (title, body, id))
        mysql.connection.commit()
        cur.close()
        flash('Blog updated successfully', 'success')
        return redirect('/blogs/{}'.format(id))
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog = cur.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        return render_template('edit-blog.html', blog_form = blog_form)

@app.route('/delete-blog/<int:id>/')
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    mysql.connection.commit()
    flash('Your blog has been deleted', 'success')
    return redirect('/my-blogs')

@app.route('/logout/')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect('/login')

# ************ New code *************

@app.route('/upload/')

def upload():
    insertBLOB("Terrain", "D:/PGDBA/sem-1/fundamentals-of-database-systems/project/abstract-art/images/img_5terre.jpg","nature")
    insertBLOB("Forest", "D:/PGDBA/sem-1/fundamentals-of-database-systems/project/abstract-art/images/img_forest.jpg","nature")
    insertBLOB("Lights", "D:/PGDBA/sem-1/fundamentals-of-database-systems/project/abstract-art/images/img_lights.jpg","lights")
    insertBLOB("Mountains", "D:/PGDBA/sem-1/fundamentals-of-database-systems/project/abstract-art/images/img_mountains.jpg","nature")
    return render_template('login.html')
    # insertBLOB("Bharath", "D:/PGDBA/courses/udemy/flog/joker.jfif")
    # return render_template('login.html')

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def insertBLOB(name, photo, category):
    print("Inserting BLOB into python_employee table")
    try:
        cur = mysql.connection.cursor();
        # sql_insert_blob_query = "INSERT INTO python_employee(name, photo) VALUES (%s,%s)"
        sql_insert_blob_query = "INSERT INTO image(image_blob, image_catg, image_name) VALUES (%s,%s,%s)"
        empPicture = convertToBinaryData(photo)

        # Convert data into tuple format
        insert_blob_tuple = (empPicture, category, name)
        result = cur.execute(sql_insert_blob_query, insert_blob_tuple)
        mysql.connection.commit()
        print("Image inserted successfully as a BLOB into python_employee table", result)

    except mysql.connection.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        # if (mysql.connection.is_connected()):
            cur.close()
            # connection.close()
            print("MySQL connection is closed")


@app.route('/read/')
# ***************** Start of read *************
def read():
    # images.append(readBLOB("Bharath", "D:/PGDBA/courses/udemy/flog/img3.jfif"))
    img = readBLOB(6, "D:/PGDBA/courses/udemy/flog/image.png")
    print(type(img))
    return render_template('images.html', image = img)

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    print(type(data))
    img = Image.open(data)
    print (img.size)
    # image = Image.frombytes('RGBA', (128,128), data, 'raw')
    # print(type(image))
    with open(filename, 'wb') as file:
        file.write(image.decode('base64'))

# def readBLOB(emp_id, photo):
#     print("Reading BLOB data from python_employee table")
#
#     try:
#         image = []
#         cur = mysql.connection.cursor()
#         sql_fetch_blob_query = "SELECT photo from python_employee where name = %s"
#         cur.execute(sql_fetch_blob_query, (emp_id,))
#         record = cur.fetchone()
#         # for row in record:
#         blob = row['photo']
#         image = blob.decode('base64')
#             # file = row[3]
#             # print("Storing employee image and bio-data on disk /n")
#         write_file(image, photo)
#
#     except mysql.connection.Error as error:
#         print("Failed to read BLOB data from MySQL table {}".format(error))
#
#     finally:
#         # if (connection.is_connected()):
#             cur.close()
#             # connection.close()
#             print("MySQL connection is closed")
#             return image

def readBLOB(emp_id, photo):
    print("Reading BLOB data from python_employee table")

    try:
        cursor = mysql.connection.cursor()
        sql_fetch_blob_query = "SELECT photo from python_employee where id = %s"

        cursor.execute(sql_fetch_blob_query, (emp_id,))
        record = cursor.fetchall()
        print(record)
        for row in record:
            # print("Id = ", row[0], )
            # print("Name = ", row[1])
            image = row['photo']
            print(type(row['photo']))
            # file = row[3]
            print("**********************")
            print(type(image))
            print("Storing employee image and bio-data on disk /n")
            # img = image.decode('base64')
            img = base64.b64decode(image)
            print(img)
            img1 = io.BytesIO(img)
            print(img1)
            img2 = PIL.Image.open(img1)
            print(img2)
            img2.show()
        return img2
            # write_file(image, photo)
            # write_file(file, bioData)

    except mysql.connection.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

    finally:
        # if (connection.is_connected()):
            cursor.close()
            # connection.close()
            print("MySQL connection is closed")



# **************** End ******************

if __name__ == '__main__':
    app.run(debug = True)
