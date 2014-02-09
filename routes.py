from flask import *
import MySQLdb
import config
from flask import request, url_for, jsonify
import os
from werkzeug import secure_filename
import urllib
from functools import wraps
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


@app.route('/dashboard')
def dashboard():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	return render_template('dashboard.html')


@app.route('/configure_tables')
def create_tables():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('Create Table User(user_email varchar(50) ,user_name varchar(50),password varchar(100),PRIMARY KEY(user_name,user_email))')
	cursor.execute('Insert into User values("admin@admin.com","admin","admin")')
	cursor.execute('Insert into User values("demo@demo.com","demo","demo")')
	db.commit()
	db.close()
	return "done"


@app.route('/logout')
def logout():
	if 'logged_in' not in session:
		flash('you need to login first')
		return redirect(url_for('index'))
	session.pop('logged_in',None)
	flash('You have logged out Successfully!')
	return redirect(url_for('index'))


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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER,
                               filename)

@login_required
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

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=8080)