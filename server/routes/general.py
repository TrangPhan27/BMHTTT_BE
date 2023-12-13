from server import cursor as cur
from server import app
from flask import request, jsonify

@app.route('/api/getall')
def get_all():
   users = []
   for row in cur.execute("SELECT * FROM users"):
      user = {'uname': row[2], 'email': row[3] }
      print(user)
      users.append(user)
   return jsonify({'all_users': users})
@app.route('/api/login', methods = ["GET"])
def login(request, id):
   username = request.GET.get('username', None)
   password = request.GET.get('password', None)
   if(username and password):
      userData = cur.execute("SELECT * FROM users WHERE uname = '%s' AND pw = '%s", username, password)
      print(userData)
      if(userData[0]):
         return jsonify({'message': 'OK', 'status': 200, 'data': userData[0]})
      else:
         return jsonify({'error': 'Not Found', 'status': 404, 'data': 'NULL'})
   else :
      return jsonify({'error': 'Bad request', 'status': 400})
   
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
def api_applications(request, id):
   role = request.headers.get('role')
   idUser = request.headers.get('id')
   if(not (idUser and role)):
         return jsonify({'message': 'Bad request', 'status': 400, 'data': 'NULL'})
      
   if(request.method == 'GET'):
      if(id):
         if(role in ['customer']):
            applications = cur.execute("SELECT * FROM APPLICATIONS WHERE created_by = '%s' AND id = '%s", idUser, id)
            return jsonify({'message': 'OK', 'status': 200, 'data': applications})
         elif (role in ['CM', 'CA', 'CS']):
            applications = cur.execute("SELECT * FROM APPLICATIONS WHERE id = '%s", id)
            return jsonify({'message': 'OK', 'status': 200, 'data': applications})
         else:
            return jsonify({'error': 'Not Role', 'status': 401})
      else :
         if(role in ['customer']):
            applications = cur.execute("SELECT * FROM APPLICATIONS WHERE created_by = '%s'", idUser)
            return jsonify({'message': 'OK', 'status': 200, 'data': applications})
         elif (role in ['CM', 'CA', 'CS']):
            applications = cur.execute("SELECT * FROM APPLICATIONS")
            return jsonify({'message': 'OK', 'status': 200, 'data': applications})
         else:
            return jsonify({'error': 'Not Role', 'status': 401})
   
   if(request.method == 'POST'):
      if(role in ['customer', 'CS']):
         data = request.POST.get
         return jsonify({'message': 'OK', 'status': 200, 'data': 'NULL'})
      else :
         return jsonify({'error': 'Not Role', 'status': 401})
   
   if(request.method == 'PUT'):
      if(id):
         data = request.POST.get
      else:
         return jsonify({'message': 'Bad request', 'status': 400, 'data': 'NULL'})
         
   
      