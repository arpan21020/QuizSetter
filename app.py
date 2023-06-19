from flask import Flask,render_template,current_app, render_template_string,request,session,redirect,jsonify,url_for
from flask_mysqldb import MySQL
import json


with open('./templates//config.json','r') as file:
    params = json.load(file)["params"]
    
app = Flask(__name__)
app.secret_key="flaskPython"

app.config['MYSQL_HOST'] = params['host']  # MySQL server address
app.config['MYSQL_USER'] = params['user']   # MySQL username
app.config['MYSQL_PASSWORD'] = params['password']  # MySQL password
app.config['MYSQL_DB'] = params['database']   # MySQL database name

mysql = MySQL(app)

def create_database():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {params['database']}")
        cursor.execute(f"USE {params['database']}")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS QuizList(Sno INT(10),datetime_column DATETIME,QuizNumber varchar(255));")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS Students(Name varchar(255),Email varchar(255),Phone varchar(255),Password varchar(255));")
        
        cursor.close()
        return 'Table created successfully!'
print(create_database())
app.config['MYSQL_DB'] = params['database']   # MySQL database name


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/index')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM actor')
    data = cur.fetchall()
    cur.close()
    return list(data)
    pass


@app.route('/student')
def studentDashboard():
    return render_template('studentDashboard.html')

@app.route('/register')
def studentRegister():
    return render_template('register.html')

def authenticate_admin(func):
    def wrapper(*args, **kwargs):
        if not is_authenticated() :
            return redirect('/admin')  # Redirect to login page if not authenticated
        return func(*args, **kwargs)
    return wrapper


AdminLogin=False
def is_authenticated():
    return AdminLogin == True

@app.route('/admin',methods=['GET','POST'])
def admin_Login():
    
    if is_authenticated():
        return redirect('/admin-Dashboard') 
   
    if(request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        
        print("username:",username)
        print(password)
        if(username==params['admin_username'] and password==params['admin_password']):
            AdminLogin = True
            return render_template('adminDashboard.html')
        else:
            return render_template('adminLogin.html')
    else:
        return render_template('adminLogin.html')
    
@app.route('/adminLogout')
def admin_logout():
    AdminLogin=False
    return redirect('/admin')
@app.route("/admin-Dashboard")
@authenticate_admin
def adminDashboard():
    return render_template('adminDashboard.html')
# @app.route('/setQuiz')
# def setQuiz():
#     return render_template('setQuiz.html')

@app.route('/setQuiz',methods=['GET','POST'])
def save_quiz():
    print(request.headers)
    if(request.method=='POST'):
            if request.content_type != 'application/json':
                print("ERROR OCCURED")
                print(request.content_type)
                
    
            cur = mysql.connection.cursor()
            cur.execute("Select sno FROM QuizList;")
            prev_data = cur.fetchall()
            cur.close()
            idx=1
            data = request.get_json()
            form_data = data['data']
            if(prev_data==None):
                cur = mysql.connection.cursor()
                quizname='quiz'+str(idx)
                cur.execute(f"Insert into QuizList Values({str(idx)},CURRENT_TIMESTAMP,{quizname})")
                cur.execute(f"CREATE TABLE IF NOT EXISTS {quizname}(Qno INTEGER,Question TEXT,option1 TEXT,option2 TEXT,option3 TEXT,option4 TEXT,correctans TEXT)")
                cur.execute(f"ALTER TABLE Students ADD COLUMN {quizname} Integer;")
                
                
                # Access the form field values and process them as needed
                for i in range(0,len(form_data)):
                    print(form_data[i])
                    cur.execute("INSERT INTO "+quizname+" VALUES(%s, %s, %s, %s, %s, %s, %s)", (i+1, form_data[i][0], form_data[i][1][0], form_data[i][1][1], form_data[i][1][2], form_data[i][1][3], form_data[i][2]))
                # cur.execute("INSERT INTO {quizname} VALUES(\"{request.form.get(\"question\")}\")")
                mysql.connection.commit()   
                cur.close()
            else:
                idx=len(prev_data)+1
                cur = mysql.connection.cursor()
                quizname='quiz'+str(idx)
                cur.execute(f"Insert into QuizList Values({str(idx)},CURRENT_TIMESTAMP,\'{quizname}\')")
                cur.execute(f"CREATE TABLE IF NOT EXISTS {quizname}(Qno INTEGER,Question TEXT,option1 TEXT,option2 TEXT,option3 TEXT,option4 TEXT,correctans TEXT)")
                cur.execute(f"ALTER TABLE Students ADD COLUMN {quizname} Integer;")
                
                 # Access the form field values and process them as needed
                for i in range(0,len(form_data)):
                    print(form_data[i])
                    cur.execute("INSERT INTO "+quizname+" VALUES(%s, %s, %s, %s, %s, %s, %s)", (i+1, form_data[i][0], form_data[i][1][0], form_data[i][1][1], form_data[i][1][2], form_data[i][1][3], form_data[i][2]))

                mysql.connection.commit()   
                cur.close()
            
            
    return render_template('setQuiz.html')
                
           
    
    
    
    #cur.execute('INSERT INTO QuizList VALUES(CURRENT_TIMESTAMP,)')
    
    return redirect('admin-Dashboard')

@app.route('/registered',methods=['GET','POST'])
def registered():
    if request.method=='POST':
        nm=request.form.get('name')
        email=request.form.get('email')
        phn=request.form.get('phone')
        pswd=request.form.get('password')
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO Students Values(%s,%s,%s,%s)",(nm,email,phn,pswd))
        mysql.connection.commit()
        cur.close()
        return redirect('/student')
login_credentials={}
@app.route('/studentQuizLogin',methods=['GET','POST'])
def studentQuizLogin():
    if request.method=='POST':
        email=request.form.get('email')
        pswd=request.form.get('password')
        
        cur=mysql.connection.cursor()
        cur.execute("SELECT QuizNumber from quizlist;")
        data=cur.fetchall()
        cur.close()
        print(data)
        table=data[-1][0]
        cur=mysql.connection.cursor()
        cur.execute("SELECT email,password,"+table+" from students;")
        data=cur.fetchall()
        cur.close()
        for i in data:
            
            if(email==i[0] and pswd==i[1] and i[2]==None):
                
                login_credentials['email']=email
                login_credentials['password']=pswd
                
                cur=mysql.connection.cursor()
                cur.execute(f"SELECT * from {table};")
                data=cur.fetchall()
                cur.close()
                
                return render_template("Quiz_template.html",quizData=data)
        if(email==i[0] and pswd==i[1] and i[2]!=None):
            message = 'Sorry, you cannot retake the test. Your previous attempt has already been recorded.'
        else:
            message = 'Invalid credentials!'
        return render_template_string("""
        <script>
            // Custom JavaScript code
            var additionalData = 'Incorrect Username and password';
            console.log(additionalData);
            
            // Display the alert message
            alert('{{ message }}');
            
            // Redirect to a different page
            window.location.href = '/student';
        </script>
    """, message=message)
@app.route("/showResult",methods=['GET','POST'])
def result():
    if request.method=='POST':
                selectedOptions=request.form
                cur=mysql.connection.cursor()
                cur.execute("SELECT QuizNumber from quizlist;")
                data=cur.fetchall()
                cur.close()
                table=data[-1][0]
                cur=mysql.connection.cursor()
                cur.execute(f"SELECT * from {table};")
                data=cur.fetchall()
                cur.close()
                score=0
                correctoptions=[]
                optionsselected=[]
                for i in data:
                    correctoptions.append(i[6])
                    optionsselected.append(selectedOptions.get(str(i[0])))
                    if(i[6]==selectedOptions.get(str(i[0]))):
                        score+=1
                cur=mysql.connection.cursor()
                cur.execute("UPDATE students SET "+table+"="+str(score)+" where email=%s and password=%s;",(login_credentials['email'],login_credentials['password']))
                
                mysql.connection.commit()
                
                cur.close()
                resultData={'score':score,'selectedOptions':optionsselected,'correctOptions':correctoptions,'quizData':data,'length':len(correctoptions)}
                print("IN POST METHOD:",resultData)
                return redirect(url_for('resultpage',resultData=json.dumps(resultData)))
    
    
    else:
                cur=mysql.connection.cursor()
                cur.execute("SELECT QuizNumber from quizlist;")
                data=cur.fetchall()
                cur.close()
                table=data[-1][0]
                cur=mysql.connection.cursor()
                cur.execute(f"SELECT * from {table};")
                data=cur.fetchall()
                cur.close()
                
                return render_template("Quiz_template.html",quizData=data)
@app.route('/resultpage')
def resultpage():
     print("CALLING RESULT PAGE....................................................................................................................")
     result_data = json.loads(request.args.get('resultData', None))
     print("RESULT DATA:",type(result_data),result_data)
     return render_template('result.html', resultData=result_data)
if __name__=="__main__":
    app.run(debug=True)