from server import app
from flask import request, jsonify, session
import os
import oracledb
from flask_cors import cross_origin
dict_user = {}
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
      self.connect = oracledb.connect(dsn=dsn, user=username, password=password)

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
   if request.method == 'POST':
      username = request.form['username']
      password =request.form['password']
      dsn = os.environ['ORACLE_DSN']
      user = SessionUser(username, password, dsn)
      try:
         dict_user[username] = user
         session['username'] = username
         return jsonify({'message': 'OK', 'status': 200})
      except Exception as e:
         return jsonify({'message': 'ERROR', 'status': 401})
@app.route('/logout', methods=['GET'])
def logout():
   session.clear()
   dict_user.pop()
@app.route('/api/me', methods=['GET'])
def getme(request):
   id = request.headers.get('id')
   role = request.headers.get('role')
   if(not (id and role)):
         return jsonify({'message': 'Bad request', 'status': 400, 'data': 'NULL'})
   if role == 'customer':
      userData = cur.execute("SELECT * FROM users WHERE uuid = '%s'", id)
      customerData = cur.execute("SELECT * FROM CUSTOMERS WHERE uuid = '%s'", id)
      if(userData[0] and customerData[0]):
         return jsonify({'message': 'OK', 'status': 200, 'data': userData[0] + customerData[0]})
      else :
         return jsonify({'error': 'Not Found', 'status': 404, 'data': 'NULL'})
   elif role in ['CM', 'CA', 'CS']:
      userData = cur.execute("SELECT * FROM users WHERE uuid = '%s'", id)
      staffData = cur.execute("SELECT * FROM STAFFS WHERE uuid = '%s'", id)
      if(userData[0] and staffData[0]):
         return jsonify({'message': 'OK', 'status': 200, 'data': userData[0] + staffData[0]})
      else :
         return jsonify({'error': 'Not Found', 'status': 404, 'data': 'NULL'})
   else:
      return jsonify({'error': 'Not Role', 'status': 401})
   
@app.route('/api/applications', methods = ['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin(supports_credentials=True)
def api_applications():   
   current_user = dict_user[session['username']]
   cur = current_user.connect.cursor()
   if request.method == 'GET':
      applications = []
      if cur is not None:
         cur.execute("SELECT * FROM bankadm.applications")
         columns = [col[0] for col in cur.description]
         cur.rowfactory = lambda *args: dict(zip(columns, args))
         data = cur.fetchall()
         applications = data
      return jsonify(applications)
      
   if request.method == 'POST':
      form = request.form
      if cur is not None:
         try:
            cur.execute(f"INSERT INTO BANKADM.APPLICATIONS"
                     f"VALUES({form['acc_type']}, {form['climit']}, {form['c_name']},"
                     f"{form['c_income']}, {form['c_cccd']}, {form['c_phone_num']}, {form['c_addr']}, {form['c_email']}, 0, NULL, NULL, NULL)")
            return jsonify({'message': 'OK', 'status': 200})
         except:
            return jsonify({'error': 'ERROR', 'status': 404})

@app.route('/api/analyze', methods=['GET', 'POST'])
def analyze():

   current_user = dict_user[session['username']]
   cur = current_user.connect.cursor()

   if request.method == 'GET':
      pass
      # try:
         # for cur.execute(f"SELECT * FROM BANKADM.ANALYZE;")
   if request.method == 'POST':
      pass
   
      