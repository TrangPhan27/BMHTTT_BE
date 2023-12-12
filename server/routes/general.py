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