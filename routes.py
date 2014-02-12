from flask import *
import MySQLdb
import config
from flask import request, url_for, jsonify
import os
from werkzeug import secure_filename
import urllib
from functools import wraps
import json
from time import gmtime, strftime
import datetime
# from flask_bootstrap import Bootstrap
# from flask_appconfig import AppConfig
app =  Flask(__name__)
app.config.from_object('config')
app.secret_key = 'dfmm234xdsfdfssf2133edssdgfqwewqewr'


def login_required(test):
	@wraps(test)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return test(*args,**kwargs)
		else:
			flash('you need to login first')
			return redirect(url_for('login'))
	return wrap

#---------------------------- login page --------------------------
@app.route('/',methods=["GET","POST"])
@app.route('/index',methods=["GET","POST"])
@app.route('/login',methods=["GET","POST"])
def index():
	error=None
	if 'logged_in' in session:
		return redirect(url_for('dashboard'))
	if request.method == 'POST'	:
		db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		try:
			cursor.execute('select * from User where user_name = %s AND password = %s',[request.form['user_name'],request.form['user_password']])
			result=cursor.fetchall()
			db.close()
			#flash(result)
			#return redirect(url_for('index'))
			if(result is not None):
				session['logged_in']=True
				session['user_name']=request.form['user_name']
				session['user_email']=result[0]['user_email']
				return redirect(url_for('dashboard'))
			else:
				flash('User / Password is incorrect')
				return render_template('index.html' , error=error)

		except (MySQLdb.Error, MySQLdb.Warning) as e:
			flash('User / Password is incorrect'+str(e))
			return render_template('index.html' , error=error)
	return render_template('index.html' , error=error)



#-------------------------Register page------------------------
@app.route('/register',methods=["GET","POST"])
def register():
	error=None

	if request.method == 'POST'	:
		try:
			db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
			cursor = db.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('''INSERT into User (user_name,password,user_email)
            	values (%s,%s,%s)''',(request.form['user_name'],request.form['user_password_new'],request.form['user_email']))
			db.commit()
			db.close()
			flash("You have registered Successfully.You may now login!")	
			return redirect(url_for('index'))
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			flash("There was an error during registration " +str(e))	
		return render_template('register.html' , error=error,message="hi")

	return render_template('register.html' , error=error)


#------------------------ Dashboard --------------------

@app.route('/dashboard')
def dashboard():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('select count(*) from POST where user_name = %s',[session['user_name']])
	result=cursor.fetchall()
	return render_template('dashboard.html',post_count=result[0]['count(*)'])


#-------------------logout--------------------

@app.route('/logout')
def logout():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	session.pop('logged_in',None)
	flash('You have logged out Successfully!')
	return redirect(url_for('index'))


#---------------------Recent posts-----------------
@app.route('/recent_posts',methods=["GET","POST"])
@app.route('/recent_posts')
def recent_posts():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	flag=None
	if request.method == 'POST'	:
		if request.form['description'] == 'recent_posts_by_all':
			flag=True
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	if flag is None	:
		cursor.execute('select post_id,likes,date_time, image_path, tags, description,user_name from POST where user_name = %s ORDER BY date_time DESC LIMIT 10',[session['user_name']])
	else:
		cursor.execute('select post_id,likes,date_time, image_path, tags, description,user_name from POST ORDER BY date_time DESC LIMIT 10')

	rows={}
	rows['table'] = cursor.fetchall()
	if len(rows['table']) is 0:
		return "<br><br><div class='alert alert-info'><center>Nothing Found</center></div>"
	recent_posts = []
	for row in range(len(rows['table'])):
		likes={}
		cursor.execute('select * from USER_LIKES where post_id = %s AND user_name= %s',[rows['table'][row]['post_id'],session['user_name']])
		likes['table']=cursor.fetchall()
		liked=True
		print 'might be',len(likes['table'])
		if len(likes['table']) <= 0:

			liked=False
		recent_posts.append(dict(post_id=rows['table'][row]['post_id'],image_path=rows['table'][row]['image_path'],
			description=rows['table'][row]['description'],
			date_time=rows['table'][row]['date_time'],
			tags=rows['table'][row]['tags']
			,user_name=rows['table'][row]['user_name'],likes=rows['table'][row]['likes'],liked=liked))
	db.close()
	return render_template('recent_posts.html',posts=recent_posts)

#----------------------Popular posts--------------------
@app.route('/popular_posts',methods=["GET","POST"])
@app.route('/popular_posts')
def popular_posts():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	flag=None
	if request.method == 'POST'	:
		if request.form['description'] == 'popular_posts_by_all':
			flag=True
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	if flag is None	:
		cursor.execute('select post_id,likes,date_time, image_path, tags, description,user_name from POST where user_name = %s ORDER BY likes DESC , date_time DESC  LIMIT 10',[session['user_name']])
	else:
		cursor.execute('select post_id,likes,date_time, image_path, tags, description,user_name from POST ORDER BY likes DESC ,date_time DESC    LIMIT 10')

	rows={}
	rows['table'] = cursor.fetchall()
	if len(rows['table']) is 0:
		return "<br><br><div class='alert alert-info'><center>Nothing Found</center></div>"
	recent_posts = []
	for row in range(len(rows['table'])):
		likes={}
		cursor.execute('select * from USER_LIKES where post_id = %s AND user_name= %s',[rows['table'][row]['post_id'],session['user_name']])
		likes['table']=cursor.fetchall()
		liked=True
		print 'might be',len(likes['table'])
		if len(likes['table']) <= 0:

			liked=False
		recent_posts.append(dict(post_id=rows['table'][row]['post_id'],image_path=rows['table'][row]['image_path'],
			description=rows['table'][row]['description'],
			date_time=rows['table'][row]['date_time'],
			tags=rows['table'][row]['tags']
			,user_name=rows['table'][row]['user_name'],likes=rows['table'][row]['likes'],liked=liked))
	db.close()
	return render_template('recent_posts.html',posts=recent_posts)


#------------------------Tags--------------------------
@app.route('/get_posts_by_tag',methods=["GET","POST"])
def get_posts_by_tag(tag=None):
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("select * from POST WHERE tags LIKE '%"+tag+"%' ORDER BY date_time DESC")
	rows={}
	rows['table'] = cursor.fetchall()
	if len(rows['table']) is 0:
		return "<br><br><div class='alert alert-info'><center>Nothing Found</center></div>"
	recent_posts = []
	for row in range(len(rows['table'])):
		likes={}
		cursor.execute('select * from USER_LIKES where post_id = %s AND user_name= %s',[rows['table'][row]['post_id'],session['user_name']])
		likes['table']=cursor.fetchall()
		liked=True
		print 'might be',len(likes['table'])
		if len(likes['table']) <= 0:
			liked=False
		recent_posts.append(dict(post_id=rows['table'][row]['post_id'],image_path=rows['table'][row]['image_path'],
			description=rows['table'][row]['description'],
			date_time=rows['table'][row]['date_time'],
			tags=rows['table'][row]['tags']
			,user_name=rows['table'][row]['user_name'],likes=rows['table'][row]['likes'],liked=liked))
	db.close()
	return recent_posts
	

#------------------ Post You May Like -----------------
@app.route('/get_posts_you_may_like',methods=["GET","POST"])
def get_posts_you_may_like():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("SELECT tags FROM POST WHERE post_id IN (SELECT post_id FROM USER_LIKES WHERE user_name = %s) ",[session['user_name']])
	liked_tags={}
	liked_tags['table']=cursor.fetchall()
	liked_posts={}	
	recent_posts=[]
	if len(liked_tags['table']) is 0:
		return "<br><br><div class='alert alert-info'><center>No Interests Found. Do some activities and come to this section later.</center></div>"
	splitted_str=[]
	for row in range(len(liked_tags['table'])):
		splitted_str=liked_tags['table'][row]['tags'].split(",")
		for tag in splitted_str:
			if(tag in liked_posts):
				liked_posts[tag] += 1
			else:
				liked_posts[tag] = 1
	sorted(liked_posts, key=lambda i: int(liked_posts[i]))
	posts=[]
	for tag in liked_posts.keys() :
		posts=get_posts_by_tag(tag)
		for post in posts:
			if post not in recent_posts:
				recent_posts.append(post)
	return render_template('recent_posts.html',posts=recent_posts)

#-------------Post an Image---------------

@app.route('/post_image',methods=["GET","POST"])
def post_image():
	if request.method == 'POST'	:
		#flash(request.form['tags'])
		try:
			db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
			cursor = db.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('''INSERT into POST (user_name,tags,description,image_path,date_time)
            	values (%s,%s,%s,%s,%s)''',(session['user_name'],request.form['tags'],request.form['description'],request.form['image_path'], datetime.datetime.now()))
			db.commit()
			db.close()
			return "Your Post Is Successful!"
		except Exception as e:
			print str(e)
			return request.form['description']+str(e)
#------------------Like a photo  ----------------

@app.route('/like_post',methods=["GET","POST"])
def like_post():
	if request.method == 'POST'	:
		try:
			db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
			cursor = db.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('update POST SET likes = likes + 1 WHERE post_id= %s ',[request.form['post_id']])
			cursor.execute('Insert into USER_LIKES (post_id,user_name) values(%s,%s)',(request.form['post_id'],session['user_name']))
			db.commit()
			db.close()
			return "Your Post Is Successful!"
		except Exception as e:
			print str(e)
			return request.form['description']+str(e)

#------------------Photos --------------------------
@app.route("/photos")
def photos():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	return render_template('photos.html')

#--------------uploader -------------------
def save_file(data_file, file_name):
	#global dump
	try:
		location = os.getcwd() + "/uploads"
		with open(file_name, 'wb') as location:
			shutil.copyfileobj(data_file, location)
	except:
		return "error"

    #del dump
	return 



#-------------------- get uploaded files ----------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER,
                               filename)


@app.route('/+upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        # we are expected to return a list of dicts with infos about the already available files:
        file_infos = []
        for file_name in list_files():
            file_url = url_for('download', file_name=file_name)
            file_size = os.stat(file_name).st_size
            file_infos.append(dict(name=file_name,
                                   size=file_size,
                                   url=file_url))
        return jsonify(files=file_infos)

    if request.method == 'POST':
        # we are expected to save the uploaded file and return some infos about it:
        #                              vvvvvvvvv   this is the name for input type=file
        data_file = request.files.get('data_file')
        file_name = data_file.filename
        #saved_file=save_file(data_file, file_name)
        if data_file :
        	filename = secure_filename(data_file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        data_file.save(os.path.join(config.UPLOAD_FOLDER, filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        #return redirect()
        #file_size = get_file_size(file_name)
        file_url = url_for('uploaded_file',
                                filename=filename)
        # providing the thumbnail url is optional
        thumbnail_url = url_for('uploaded_file',
                                filename=filename)
        file_size = os.stat(os.path.join(config.UPLOAD_FOLDER, filename)).st_size
        return jsonify(name=file_name,
                       size=file_size,
                       url=file_url,
                       thumbnail=thumbnail_url)

#--------------------------uploader ends --------------------------


#--------------------helper functions--------------------
@app.template_filter('get_date')
def get_date(date):
	f = '%Y-%m-%d %H:%M:%S.%f'
	correct_date=datetime.datetime.strptime(date, f)
	new_f='%Y-%m-%d'
	return correct_date.strftime(new_f)

@app.template_filter('get_time')
def get_time(time):
	f = '%Y-%m-%d %H:%M:%S.%f'
	correct_date=datetime.datetime.strptime(time, f)
	new_f='%H:%M:%S'
	return correct_date.strftime(new_f)
@app.template_filter('tags')
def get_tags(tags):
	print tags
	tag_split=tags.split(',')
	tag_html=''
	for tag in tag_split:
		tag_html+='<a href="'+tag+'">'+tag+'</a>'
	return str(tag_html)

app.jinja_env.filters['get_date'] = get_date
app.jinja_env.filters['get_time'] = get_time
app.jinja_env.filters['get_tags'] = get_tags
#------------------------- Configurations ------------------------

@app.route('/configure_user_table')
def create_user_table():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('Create Table User(user_email varchar(50) ,user_name varchar(50),password varchar(100),PRIMARY KEY(user_name,user_email))')
	cursor.execute('Insert into User values("admin@admin.com","admin","admin")')
	cursor.execute('Insert into User values("demo@demo.com","demo","demo")')
	db.commit()
	db.close()
	return "done"

@app.route('/configure_post_table')
def create_post_table():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	try:
		cursor.execute('DROP TABLE POST');
		db.commit()
	except:
		print 'table not found'
	cursor.execute('Create Table POST(post_id int NOT NULL AUTO_INCREMENT ,user_name varchar(50),description Text,tags varchar(500),image_path varchar(100),date_time varchar(50),likes int DEFAULT 0,location varchar(50),PRIMARY KEY(post_id,user_name,image_path))')
	db.commit()
	db.close()
	return "done"

@app.route('/configure_user_likes_table')
def configure_user_likes_table():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('Create Table USER_LIKES(id int NOT NULL AUTO_INCREMENT ,user_name varchar(50),post_id int, PRIMARY KEY(id))')
	db.commit()
	db.close()
	return "done"
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=8080)