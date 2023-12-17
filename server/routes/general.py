from server import app
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import os
import oracledb
from flask_cors import cross_origin
def login_required(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
      if 'username' not in session:
         return jsonify({'message': 'Unauthorized', 'status': 401}), 401
      return f(*args, **kwargs)
   return decorated_function

def start_pool(user, password):
    dsn = os.environ['ORACLE_DSN']
    print(f"{user}/{password}@{dsn}")
    pool_min = 4
    pool_max = 4
    pool_inc = 0

    pool = oracledb.create_pool(user=user,
                                   password=password,
                                   dsn=dsn,
                                   min=pool_min,
                                   max=pool_max,
                                   increment=pool_inc)
    return pool
class SessionUser:
   def __init__(self, username, password, dsn) -> None:
      self.username = username
      self.password = password
      self.dsn = dsn
      self.connect: oracledb.Connection = oracledb.connect(dsn=dsn, user=username, password=password)
dict_user: dict[str, SessionUser] = {}

@app.route('/api/getall')
def get_all():
   current_username = session['username']
   current_user = dict_user[current_username]
   users = []
   cur = current_user.connect.cursor()
   if cur is not None:
      for row in cur.execute("SELECT * FROM bankadm.users"):
         user = {'uname': row[2], 'email': row[3] }
         users.append(user)
      return jsonify({'all_users': users})
   return {}

@app.route('/login', methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def login():
   # if request.method == 'POST':
   #    username = request.form['username']
   #    password =request.form['password']
   #    if username == 'bankca' and password == '@Aa12345678':
   #       user = SessionUser(username, password, os.environ['ORACLE_DSN'])
   #       if username in dict_user.keys():
   #          print("A user have been login")
   #          return jsonify({'message': 'Already login', 'status': 403})
   #       session['username'] = username
   #       dict_user[username] = user
   #       user.connect.close()
   #       print(dict_user)
   #       return jsonify({'message': 'OK', 'status': 200})
      username = request.form['username']
      password =request.form['password']
      dsn = os.environ['ORACLE_DSN']
      # user has been login
      print(session.keys())
      if 'username' in session.keys():
         print("have been login")
         return jsonify({'message': 'Already login', 'status': 403})
      print(dict_user)
      if username in dict_user.keys():
         return jsonify({'message': 'Another device', 'status': 403})
      try:
         oracledb.connect(dsn=dsn, user=username, password=password).close()
      except oracledb.DatabaseError as e:
         error, = e.args
         if error.code == 1017:
            return jsonify({'message': 'Invalid username or password', 'status': 401})        
         if error.code == 28000:
            return jsonify({'message': 'Account locked(>5 times)', 'status': 401})
      user = SessionUser(username, password, dsn)
      session['username'] = username
      dict_user[username] = user
      print(session.accessed)
      return jsonify({'message': 'OK', 'status': 200})
   
@app.route('/logout', methods=['GET'])
@login_required
def logout():
   username = session['username']
   session.clear()
   if username not in dict_user.keys():
      return jsonify({'message': 'OK', 'status': 200})
   user = dict_user[username]
   try:
      user.connect.close()
   except:
      pass
   dict_user.pop(username)
   return jsonify({'message': 'OK', 'status': 200})
   # print(session.accessed)
   # if not session.accessed:
   #    return jsonify({'message': 'ERROR', 'status': 401})
   
   # print(dict_user)

@app.route('/api/me', methods=['GET'])
@login_required
def getme():
   current_user = dict_user[session['username']]
   cur = current_user.connect.cursor()
   isCustomer = cur.execute("SELECT sys_context('SYS_SESSION_ROLES','CUSTOMER_ROLE') FROM dual").fetchone()[0]
   user = cur.execute("SELECT * FROM bankadm.users").fetchone()
   if isCustomer == 'TRUE':
      userData = cur.execute("SELECT * FROM bankadm.customers WHERE uuid = sys_context('users_ctx', 'uuid')").fetchone()
   else:
      userData = cur.execute("SELECT * FROM bankadm.staffs WHERE uuid = sys_context('users_ctx', 'uuid')").fetchone()
   # print(staff)
   return jsonify({'message': 'OK', 'status': 200, 'data': user[1:] + userData[1:]})

   # if customer[0]:
   #    return jsonify({'message': 'OK', 'status': 200, 'data': customer[0]})
   # elif staff[0]:
   #    return jsonify({'message': 'OK', 'status': 200, 'data': staff[0]})
   # else:
   #    return jsonify({'error': 'Not Found', 'status': 404, 'data': 'NULL'})
   # if role == 'customer':
   #    if(userData[0] and customerData[0]):
   #       return jsonify({'message': 'OK', 'status': 200, 'data': userData[0] + customerData[0]})
   #    else :
   #       return jsonify({'error': 'Not Found', 'status': 404, 'data': 'NULL'})
   # elif role in ['CM', 'CA', 'CS']:
   #    userData = cur.execute("SELECT * FROM users WHERE uuid = '%s'", id)
   #    staffData = cur.execute("SELECT * FROM STAFFS WHERE uuid = '%s'", id)
   #    if(userData[0] and staffData[0]):
   #       return jsonify({'message': 'OK', 'status': 200, 'data': userData[0] + staffData[0]})
   #    else :
   #       return jsonify({'error': 'Not Found', 'status': 404, 'data': 'NULL'})
   # else:
   #    return jsonify({'error': 'Not Role', 'status': 401})
   
@app.route('/api/applications', methods = ['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin(supports_credentials=True)
@login_required
def api_applications():   
   current_user = dict_user[session['username']]
   cur = current_user.connect.cursor()
   if request.method == 'GET':
      applications = []
      if cur is not None:
         cur.execute("SELECT * FROM bankadm.applications")
         columns = [col[0] for col in cur.description]
         cur.rowfactory = lambda *args: dict(zip(columns, args))
         data = cur.execute("SELECT * FROM bankadm.applications").fetchall()
         for i in data:
            i.pop("CREATED_BY")
         applications = data
         print(applications)
      return jsonify({'message': 'OK', 'status': 200, 'data': applications})
      # return applications
      # return jsonify(applications)
      
   if request.method == 'POST':
      form = request.form
      
      if cur is not None:
         excute_f = """INSERT INTO BANKADM.APPLICATIONS 
                     (acc_type ,climit , c_name , c_income , c_cccd , c_phone_num , c_addr , c_email)
                     VALUES ('%s', %s, '%s', %s, '%s', %s, '%s', '%s')
                     """
         # print(form)
         excute_str = excute_f % (form['acc_type'], form['climit'], 
                                  form['c_name'], form['c_income'], 
                                  form['c_cccd'], form['c_phone_num'], 
                                  form['c_addr'], form['c_email'])
         try:
            cur.execute(excute_str)
            current_user.connect.commit()
            return jsonify({'message': 'OK', 'status': 200})
         except:
            return jsonify({'error': 'ERROR', 'status': 404})
   if request.method == 'DELETE':
      isCM = cur.execute("SELECT sys_context('SYS_SESSION_ROLES','CREDIT_MANAGER_ROLE') FROM dual").fetchone()[0]
      if isCM == 'TRUE':
         form = request.form
         if cur is not None:
            excute_f = """DELETE FROM BANKADM.APPLICATIONS WHERE id = %s"""
            excute_str = excute_f % (form['id'])
            try:
               cur.execute(excute_str)
               current_user.connect.commit()
               return jsonify({'message': 'OK', 'status': 200})
            except:
               return jsonify({'error': 'ERROR', 'status': 404})
         # return jsonify({'message': 'OK', 'status': 200})

@app.route('/api/analyze', methods=['GET', 'POST'])
@login_required
def analyze():

   current_user = dict_user[session['username']]
   cur = current_user.connect.cursor()

   if request.method == 'GET':
      cur.execute(f"SELECT * FROM BANKADM.ANALYZE")
      columns = [col[0] for col in cur.description]
      cur.rowfactory = lambda *args: dict(zip(columns, args))
      data = cur.execute(f"SELECT * FROM BANKADM.ANALYZE").fetchall()
      return jsonify({'message': 'OK', 'status': 200, 'data': data})
      # try:
         # for cur.execute(f"SELECT * FROM BANKADM.ANALYZE;")
   if request.method == 'POST':
      pass

   
      