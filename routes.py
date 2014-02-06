from flask import *
import MySQLdb
import config

# from flask_bootstrap import Bootstrap
# from flask_appconfig import AppConfig
app =  Flask(__name__)
app.config.from_object('config')
app.secret_key = 'dfmm234xdsfdfssf2133edssdgfqwewqewr'


@app.route('/',methods=["GET","POST"])
@app.route('/index',methods=["GET","POST"])
def index():
	error=None
	if request.method == 'POST'	:
		if request.form['user_name'] != 'admin' or request.form['user_password'] !='admin' :
			error="Invalid User or Password"
		else :
			session['logged_in']=True
			return redirect(url_for('dashboard'))
	return render_template('index.html' , error=error)

@app.route('/register',methods=["GET","POST"])
def register():
	error=None
	if session['logged_in'] == True	:
			return redirect(url_for('dashboard'))

	return render_template('register.html' , error=error)

@app.route('/dashboard')
def dashboard():
	if(session['logged_in']==True) :
		return render_template('dashboard.html')
	else :
		return	redirect(url_for('/'))

def create_tables():
	db = MySQLdb.connect(user=config.DB_USERNAME, passwd=config.DB_PASSWORD, db=config.DB_NAME)
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('Insert into Info values("abc")')
	db.commit()
	db.close()


@app.route('/logout')
def logout():
	session['logged_in']=None
	return redirect(url_for('index'))
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0', port=8080)
