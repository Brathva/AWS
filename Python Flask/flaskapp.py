import os, calendar, time
import sqlite3, textract, re

from flask import Flask, render_template, request, g, current_app, send_from_directory

app = Flask(__name__)

DATABASE = 'C:/Users/barat/TestDataBase.db'
DIRECTORY_NAME = 'C:/Users/barat/PycharmProjects/Assignment1/static'

@app.route('/',methods=['POST','GET'])
def starting():
    if request.method == "POST":
        user_Name = request.form['username']
        password = request.form['password']
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
            cur = db.cursor()
            cur.execute('select * from user_detail where user_Name =?', (user_Name,))
            row = cur.fetchone()
            if(row == None):
                return render_template('Homepage.html', us_exist='false')
            else:
                cur.execute('select * from user_detail where user_Name =? and passwrd =?', (user_Name, password,))
                row = cur.fetchone()
                if (row == None):
                    return render_template('Homepage.html', us_pwd_exist='false')
                else:
                    wc= row[6]
                    if(wc == None):
                        wc = ""

                    fn = row[5]
                    if(fn == None):
                        fn = ""
                    return render_template('display.html',firstname=row[0],lastname=row[1],email=row[4],Filename=fn,wordcount=wc, username = row[2])
            db.close()
        return render_template('Homepage.html')

    return render_template('Homepage.html')

@app.route('/Create', methods=['POST','GET'])
def getvalue():

    if request.method == 'POST':
        first_Name = request.form['firstname']
        last_Name = request.form['lastname']
        email = request.form['email']
        passwrd = request.form['pwd']
        username = request.form['username']
        fileName=""
        wordcount=0
        db = getattr(g, '_database', None)
        if db is None:
                db = g._database = sqlite3.connect(DATABASE)
                cur = db.cursor()
                cur.execute('select * from user_detail where user_Name =?', (username,))
                row = cur.fetchone()
                if(row == None ):
                    cur.execute('select * from user_detail where email =?', (email,))
                    row = cur.fetchone()
                    if(row == None):
                        cur.execute("insert into user_detail (first_Name, last_Name, user_Name,passwrd,email) values (?,?,?,?,?)",(first_Name,last_Name,username,passwrd,email))
                        db.commit()
                        return render_template('display.html',firstname=first_Name,lastname=last_Name,email=email, username=username, Filename=fileName, wordcount=wordcount)
                    else:
                        return render_template('Create.html', em_exist='true')
                else:
                    return render_template('Create.html', us_exist = 'true')
                db.close()
        return render_template('Create.html')
    return render_template('Create.html')

@app.route('/files/<file_name>')
def get_file(file_name):
	directory = os.path.join(current_app.root_path, DIRECTORY_NAME)
	return send_from_directory(directory, file_name, as_attachment=True)

@app.route('/update', methods=['POST','GET'])
def update_file():
    file = request.files['file']
    username = request.values.get("username")
    ext = 'true'
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        cur = db.cursor()
        cur.execute('select * from user_detail where user_Name =?', (username,))
        row = cur.fetchone()
        wc = row[6]
        file_ext = file.filename
        ts = calendar.timegm(time.gmtime())
        fileName = username + str(ts) + ".txt"
        tg_Dir = DIRECTORY_NAME + "/" + fileName
        if (row == None):
            return render_template('Homepage.html', us_exist='false')
        else:
            first_Name = row[0]
            last_Name = row[1]
            email = row[4]
            file.save(tg_Dir)
            cur.execute('update user_detail set Filename =? where user_Name =?', (fileName,username,))
            db.commit()
            if file_ext.endswith('.txt'):
                file1 = open(tg_Dir, "rt")
                data = file1.read()
                words = data.split()
                wordCount = len(words)
                cur.execute('update user_detail set wordCount =? where user_Name =?', (wordCount,username,))
                db.commit()
            else:
                ext = 'false'
                return render_template('display.html', firstname=first_Name, lastname=last_Name, email=email,
                                       Filename=fileName, wordcount=wc, username = username,ext_iss = ext)
            return render_template('display.html',firstname=first_Name,lastname=last_Name,email=email,Filename= fileName,username = username, wordcount= wordCount )
    return render_template('Create.html')


if __name__ == '__main__':
  app.run(debug=True)