from flask import Flask , render_template , request, redirect, url_for
import sqlite3
from matrix2 import run , write ,missing,read

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("home.html" )
@app.route("/About")
def about():
    return render_template("aboutus.html")
@app.route("/login",methods=['GET','POST'])
def login():
	error = None
	if request.method=='POST':
		email = request.form['email']
		password = request.form['psw']
		if email =="admin" and password == "admin":
			return  redirect(url_for('admin'))
		else:
			error = "INVALID DETAILS"
	return render_template("login.html",error=error)
@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/admin")
def admin():
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		data = cursor.execute("SELECT * FROM room")
		data = cursor.fetchall()
	return render_template("admin.html",data=data)
@app.route("/addroom",methods=['GET','POST'])
def addroom():
	data=None
	error = None
	if request.method == 'POST':
		room_no = request.form['room_no']
		row = request.form['row']
		col = request.form['col']
		seat = request.form['seat']
		myconn = sqlite3.connect("room_details.db")
		if (int(seat) <= int(row) * int(col)):
			with myconn:
				cursor = myconn.cursor()
				cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
				temp_no = cursor.execute("SELECT room_no from room where room_no=?",[room_no])
				temp_no = cursor.fetchone()	
			if temp_no is None:
				with myconn:
					cursor = myconn.cursor()
					cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
					cursor.execute("INSERT INTO room VALUES(?,?,?,?)",[room_no,col,row,seat]) 
					error = room_no + " is added"
			else:
				error = room_no + " is already exist"
		else:
			error = "Invalid number of seat" 
	return render_template("addroom.html",error = error,data=data)
@app.route("/Generate",methods=['GET','POST'])
def generate():
	error= None
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		temp_no = cursor.execute("SELECT room_no from room ")
		temp_no = cursor.fetchall()
	if request.method == 'POST':
		room_no  = request.form['room']
		it_start = request.form['it_start']
		it_end   = request.form['it_end']
		ec_start = request.form['ec_start']
		ec_end   = request.form['ec_end']
		el_start = request.form['el_start']
		el_end   = request.form['el_end']
		r_missing = request.form['missing']
		with myconn:
			cursor = myconn.cursor()
			row    = cursor.execute("SELECT row FROM room WHERE room_no = ?",[room_no])
			row = cursor.fetchone()
			row = row[0]
			col    = cursor.execute("SELECT col FROM room WHERE room_no = ?",[room_no])
			col = cursor.fetchone()
			col = col[0]
			seat    = cursor.execute("SELECT seat FROM room WHERE room_no = ?",[room_no])
			seat = cursor.fetchone()
			seat= seat[0]
		it_start = int(it_start)
		it_end   = int(it_end)
		ec_start = int(ec_start) 
		ec_end   = int(ec_end)   
		el_start = int(el_start)
		el_end   = int(el_end) 
		r_missing = r_missing.split()
		for  i in range(len(r_missing)):
			r_missing[i] = int(r_missing[i])
		it_list = list(range(it_start,it_end+1))
		it_list = missing(r_missing,it_list)
		ec_list = list(range(ec_start,ec_end+1))
		ec_list = missing(r_missing,ec_list)
		el_list = list(range(el_start,el_end+1))
		el_list = missing(r_missing,el_list)
		check =len(el_list)+len(ec_list)+len(it_list)
		if( check <= int(seat) ): 
			data = run(el_list,ec_list,it_list,row,col)
			write(data,room_no)
			error = "Seating Arrangment For "+ room_no + " Is generated "
		else:
			error = " Total Number of student is Not More than " + str(seat) + " " +  str(check)	
	return render_template("generate.html",room_no = temp_no,error=error )
@app.route('/result',methods=['GET','POST'])
def show():
	data=None
	filename = None
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		temp_no = cursor.execute("SELECT room_no from room ")
		temp_no = cursor.fetchall()
	if request.method == 'POST':
		room_no = request.form['room']
		data =  read(room_no)
		data= data.to_html()
		filename = '/static/execl/'+room_no+'.xlsx'
	return render_template("show_result.html",data=data,room_no=temp_no,filename=filename)
@app.route('/delete/<id>')
def delete(id):
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
		cursor.execute("DELETE FROM room WHERE room_no=?",[id])
	return  redirect(url_for('admin'))
@app.route('/edit/<id>',methods=['GET','POST'])
def edit(id):
	if request.method == 'POST':
		room_no = request.form['room_no']
		row = request.form['row']
		col = request.form['col']
		seat = request.form['seat']
		myconn = sqlite3.connect("room_details.db")
		if (int(seat) <= int(row) * int(col)):
			with myconn:
				cursor = myconn.cursor()
				cursor.execute("CREATE TABLE IF NOT EXISTS room(room_no integer(10),col integer(10),row integer(10),seat integer(10))")
				cursor.execute("INSERT INTO room VALUES(?,?,?,?)",[room_no,col,row,seat]) 
				error = room_no + " is added"
		else:
			error = "Invalid number of seat" 
	error = None
	myconn = sqlite3.connect("room_details.db")
	with myconn:
		cursor = myconn.cursor()
		data = cursor.execute("SELECT * FROM room WHERE room_no = ?",[id])
		data = cursor.fetchmany()
	room_no = data[0][0]
	col = 	data[0][1]
	row = data[0][2]
	seat = data[0][3]
	return render_template("addroom.html",error = error,room = room_no,col = col, row = row, seat = seat)




if __name__ == "__main__":
    app.run()