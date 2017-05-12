from flask import Flask, render_template, request, redirect, url_for, make_response, session,flash
import sqlite3, re, datetime
app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?12'
#global value
date = ""

@app.route('/')
def home():
	return render_template('bt_home.html')
	
@app.route('/signout')
def signout():
	global date
	date = ""
	session.pop('log_in', None)
	flash("You were logged out!!")
	return redirect(url_for('home'))

@app.route('/login')
def login():
	return render_template('bt_login.html')
	
@app.route('/reLogin')
def reLogin(err):
	return render_template('bt_reLogin.html',err)
	
@app.route('/login_check',methods = ['POST', 'GET'])
def login_check():
	if request.method == 'POST':
		con = sqlite3.connect('bugTracker_sample.db')
		id = request.form['id']
		paswd = request.form['paswd']
         
#         with sql.connect("database") as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM users WHERE id = ? and paswd = ?",(id,paswd) )
		row = cur.fetchone()
		if(row):
			now = datetime.datetime.now()
			global date
			date = str(now.strftime("%d-%m-%Y"))
			print date
			session['log_in'] = str(row[1])
			return render_template('bt_mainPage.html',user = str(row[1]))
		else:
			flash("Username or Password is Incorrect")
			return render_template('bt_Login.html')
	
@app.route('/register')
def register():
	return render_template('bt_register.html')
	
@app.route('/reRegister')
def reRegister(iderr,nmerr,perr):
	return render_template('bt_reRegister.html',iderr,nmerr,perr)
	
@app.route('/register_check',methods = ['POST', 'GET'])
def register_check():
	if request.method == 'POST':
		con = sqlite3.connect('bugTracker_sample.db')
		flag = 0
		perr = ''
		nmerr = ''
		iderr = ''
		try:
			id = request.form['id']
			uname = request.form['uName']
			paswd = request.form['paswd']
			cpaswd = request.form['cPaswd']
			
			if(id == '' or id > 5 or id.isdigit() == False):
				flag = 1
				iderr = "* Fill in the Unique ID field" 
				
			if(uname == ''):
				flag = 1
				nmerr = "* Fill in the User Name field"
			elif len(uname) >= 10 :
				flag = 1
				nmerr = "* User Name cannot exceed 10 characters"
			elif (uname.isalnum() != True) and (uname[0].isalpha() != True):
				flag = 1
				nmerr = "* User name is case sensitive and should begin with an alphabet, and can contain numbers and alphabets only"
				
			if(paswd == ''):
				flag = 1
				perr = "* Fill in the password field"
			elif(paswd != cpaswd):
				flag = 1
				perr = "* Passwords are not matching"
			elif(len(paswd) <= 4):
				flag = 1
				perr = "* Password should be at least 5 characters long"
			elif(len(paswd) > 12):
				flag = 1
				perr = "* Password can not exceed 12 characters"
			elif(paswd.isalnum() != True):
				flag = 1
				perr = "* Password can contain only alphabets and numbers"
			
         
#         with sql.connect("database") as con:
			if(flag != 1):
				cur = con.cursor()
				cur.execute("INSERT INTO users (id,uname,paswd) VALUES (?,?,?)",(id,uname,paswd) )
            
				con.commit()
				msg = "Record successfully added"
			else:
				flag = 2
				return render_template("bt_reRegister.html",iderr = iderr, nmerr = nmerr, perr = perr)
				
		except:
			con.rollback()
			flag = 1
			msg = "Error in Registration"
      
		finally:
			if(flag != 2):
				return render_template("bt_register_result.html",msg = msg,flag = flag)
				con.close()
			
@app.route('/mainPage/<user>')
def mainPage(user):
	return render_template('bt_mainPage.html',user = user)
			
@app.route('/submit/<user>')
def submit(user):
	return render_template('bt_submit.html',user = user)
	
@app.route('/submit/submit_check/<user>', methods = ['POST', 'GET'])
def submit_check(user):
	if request.method == 'POST':
		con = sqlite3.connect('bugTracker_sample.db')
		flag = 0
		nmerr = ''
		verr = ''
		berr = ''
		derr = ''

		try:
			pdtNm = request.form['pdtNm']
			pdtVer = request.form['pdtVer']
			bug = request.form['bug']
			des = request.form['def']
			severe = request.form['severe']
			status = request.form['status']
			#print pdtNm, pdtVer, bug, des, str(severe), str(status)
			
			if pdtNm == '' or len(pdtNm)>50:
				flag = 1
				nmerr = "** Fill in a valid product-name"
			#print pdtNm, pdtVer, bug, des, str(severe), str(status), flag
			p = re.compile('[0-9][.][0-9]')
			m = p.match(pdtVer)
			if(m.group() != pdtVer):
				flag = 1
				verr = "** Fill in a valid product-version"
			#print pdtNm, pdtVer, bug, des, str(severe), str(status), flag
			p = re.compile('([\w]+)')
			m = p.match(bug)
			if(m.group() != bug or len(bug)>50):
				flag = 1
				berr = "** Fill in a valid unique bug-name"
			print pdtNm, pdtVer, bug, des, str(severe), str(status), flag
			if(len(des) == 0 or len(des) > 500):
				flag = 1
				derr = "** Fill in with a precise and brief description of the bug"
			print pdtNm, pdtVer, bug, des, str(severe), str(status), flag, date, user
			
#         with sql.connect("database") as con:
			if (flag == 0):
				cur = con.cursor()
				cur.execute("INSERT INTO bugs (pdtNm, pdtVer, bug, des, severe, status, date, chgUser) VALUES (?,?,?,?,?,?,?,?)",(pdtNm, pdtVer, bug, des, str(severe), str(status), date, user) )
				print pdtNm, pdtVer, bug, des, str(severe), str(status)
				con.commit()
				msg = "Record successfully added"
				
			elif(flag == 1):
				return render_template('bt_reSubmit.html',user = user,nmerr = nmerr,verr = verr,berr = berr,derr = derr)
		except:
			con.rollback()
			flag = 1
			msg = "Error in entries, give a uniue name for Bug. You can view the already available bugs list in the View option"
      
		finally:
			return render_template("bt_submitResult.html",user = user, msg = msg, flag = flag)
			con.close()
			
@app.route('/reSubmit/<user>')
def reSubmit(user,nmerr,verr,berr,derr):
	return render_template('bt_reRegister.html',user = user,nmerr = nmerr,verr = verr,berr = berr,derr = derr)
	
@app.route('/viewAll/<user>')
def viewAll(user):
	con = sqlite3.connect('bugTracker_sample.db')
	cur = con.cursor()
	cur.execute("SELECT * FROM bugs")
	rows = cur.fetchall()
	msg = ""
	return render_template('bt_viewAll.html',user = user, rows = rows, msg = msg)

@app.route('/view/<user>', methods = ['POST','GET'])
def view(user):
	if request.method == 'POST':
		con = sqlite3.connect('bugTracker_sample.db')
		findBug = request.form['findBug']
		findPdt = request.form['findPdt']
         
#         with sql.connect("database") as con:
		cur = con.cursor()
		if(findBug):
			cur.execute("SELECT * FROM bugs WHERE bug = ?",(findBug,) )
		elif(findPdt):
			cur.execute("SELECT * FROM bugs WHERE pdtNm = ?",(findPdt,) )
		rows = cur.fetchall()
		if(rows):
			msg = ""
			return render_template('bt_viewAll.html',user = user, rows = rows, msg = msg)
		else:
			msg = "No entries found"
			return render_template('bt_viewAll.html',user = user, rows = rows, msg = msg)

@app.route('/edit/edit_check/<user>', methods = ['POST','GET'])
def edit_check(user):
	flag = 0
	if request.method == 'POST':
		con = sqlite3.connect('bugTracker_sample.db')
		bug = request.form['bug']
		status = request.form['status']
		         
#       with sql.connect("database") as con:
		cur = con.cursor()
		try:
			cur.execute("UPDATE bugs SET status = ? WHERE bug = ?", (severe, status, bug) )
			msg = "Successfully Updated"
		except:
			flag = 1
			msg = "Error in Updation"
		finally:
			return render_template('bt_submitResult.html',msg = msg, user = user, flag = flag)	
			
@app.route('/edit/<user>')
def edit(user):
	return render_template('bt_edit.html',user = user)

if __name__ == '__main__':
	app.run(debug = True)
