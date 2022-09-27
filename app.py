import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt' user='blake' host='localhost'")
cursor = conn.cursor()




def create_all():
      print("Creating tables...")
      cursor.execute("""
          CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR,
            email VARCHAR NOT NULL UNIQUE,
            phone VARCHAR,
            city VARCHAR,
            state VARCHAR,
            org_id int,
            active smallint
          );
      """)

      cursor.execute("""
          CREATE TABLE IF NOT EXISTS Organizations (
            org_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            phone VARCHAR,
            city VARCHAR,
            state VARCHAR,
            active smallint
          );
      """)
      
      conn.commit()




### HOMEWORK ###
# CRUDDA for organiztions
  #  Create, Read, Update, Delete, Deactivate, Activate
# refactor user to have nested obj for organization

def add_org(name,phone,city,state,active):
    cursor.execute("""
        INSERT INTO organizations
            (name,phone,city,state,active)
            VALUES 
            (%s,%s,%s,%s,%s);""",
            (name,phone,city,state,active))

    conn.commit()




def update_org(org_id,name,phone,city,state,active):
    lst_fields = ['name','phone','city','state','active']
    lst_inputs = [name,phone, city, state, active]

    lst_update_strgs = []
    lst_update_inputs = []

    count = 0

    for org_field in lst_fields:
        if lst_inputs[count]:
            lst_update_strgs.append(f'{org_field}=%s')
            lst_update_inputs.append(lst_inputs[count])

        count += 1

    lst_update_inputs.append(org_id)

    update_str = ', '.join(lst_update_strgs)

    cursor.execute('UPDATE organizations SET ' + update_str + ' WHERE org_id=%s',lst_update_inputs)
    conn.commit()




@app.route('/org/update/<org_id>', methods=['POST','PUT'])
def update_org_by_id(org_id):
    cursor.execute('SELECT org_id FROM organizations WHERE org_id=%s',(org_id,))
    result = cursor.fetchone()

    if result: 
    
        data = request.form
        if not data:
            data = request.json
        
        name = data.get('name')
        phone = data.get('phone')
        city = data.get('city')
        state = data.get('state')
        active = data.get('active')

        update_org(org_id,name,phone,city,state,active)

        return ('Organization Updated'), 200

    else:
        return jsonify('No organization found'), 404


@app.route('/org/get/<org_id>')
def get_by_org_id(org_id):
    cursor.execute('SELECT * FROM organizations WHERE org_id=%s',(org_id,))
    results = cursor.fetchone()

    org = {
      'org_id':results[0],
      'name':results[1],
      'phone':results[2],
      'city':results[3],
      'state':results[4],
      'active':results[5]
    }

    if results:
        return jsonify(org), 200
    else: 
        return jsonify('No Org Id matching: '), 404




@app.route('/org/get-all')
def get_all_orgs():
  cursor.execute('SELECT * FROM organizations WHERE active=1')
  results = cursor.fetchall()

  all_orgs = []

  for org in results:
      org_obj = {
          'org_id':org[0],
          'name':org[1],
          'phone':org[2],
          'city':org[3],
          'state':org[4],
          'active':org[5]
          }
      all_orgs.append(org_obj)
  
  if all_orgs:
      return jsonify(all_orgs), 200
  else: 
      return jsonify('No active organizations')



@app.route('/org/delete/<org_id>',methods=['DELETE'])
def delete_org(org_id):
    cursor.execute('SELECT org_id FROM organizations WHERE org_id=%s',(org_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute('DELETE FROM organizations WHERE org_id=%s',org_id)
        conn.commit()
        return jsonify('Organization deleted'), 200

    else:
        return jsonify('No Organization found'), 404



@app.route('/org/deactivate/<org_id>', methods=['POST','PUT'])
def deactivate_org(org_id):
    cursor.execute('SELECT org_id,name,active FROM organizations WHERE org_id=%s',(org_id,))
    results = cursor.fetchall()
    
    if results:
        org_name = results[0][1]

        if results[0][2] == 0:
            return jsonify(f'Organization: {org_name} is already deactivated'), 400

        else:
            cursor.execute('UPDATE organizations SET active=0 WHERE org_id=%s', (org_id))
            conn.commit()

            return jsonify(f'Organization: {org_name}  deactivated'), 200

    else:
        return jsonify('No org found'), 404




@app.route('/org/reactivate/<org_id>', methods=['POST','PUT'])
def reactivate_org(org_id):
    cursor.execute('SELECT org_id,name,active FROM organizations WHERE org_id=%s',(org_id,))
    results = cursor.fetchall()

    if results:
        org_name = results[0][1]

        if results[0][2] == 1:
            return jsonify(f'Organization: {org_name} is already active'), 400

        else:
            cursor.execute('UPDATE organizations SET active=1 WHERE org_id=%s', (org_id))
            conn.commit()

            return jsonify(f'Organization: {org_name} reactivated'), 200

    else:
        return jsonify('No org found'), 404



@app.route('/org/add', methods=['POST'])
def add_org_route():
    data = request.form if request.form else request.json
    
    name = data.get('name')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    active = data.get('active')

    add_org(name,phone,city,state,active)

    return jsonify('Org Created'), 200




def add_user(f_name,l_name,email,phone,city,state,org_id,active):
        cursor.execute(f"""
            INSERT INTO users (first_name, last_name, email, phone, city, state, org_id, active) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s);""",(f_name,l_name,email,phone,city,state,org_id,active))
        conn.commit()




@app.route('/user/add', methods=['POST'])
def user_add():
    post_data = request.form
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')
    add_user(first_name, last_name, email, phone, city, state, org_id, active)

    return jsonify('User created'), 201




@app.route('/user/<user_id>')
def get_user_by_id(user_id):
    cursor.execute("""
        SELECT * FROM users 
            WHERE user_id=%s;""",
        [user_id])

    results = cursor.fetchone()

    if results:
        cursor.execute('SELECT * FROM organizations WHERE org_id=%s',(str(results[7])))
        org_results = cursor.fetchall()

        org = results[7]

        if org_results:
            org = {
              'org_id':org_results[0][0],
              'name':org_results[0][1],
              'phone':org_results[0][2],
              'city':org_results[0][3],
              'state':org_results[0][4],
              'active':org_results[0][5]
            }

        user = {
          'user_id':results[0],
          'first_name':results[1],
          'last_name':results[2],
          'email':results[3],
          'phone':results[4],
          'city':results[5],
          'state':results[6],
          'org_id':org,
          'active':results[8]
        }
        return jsonify(user), 200

    else:
        return jsonify('User not found'), 404



@app.route('/users/get')
def get_all_active_users():
    cursor.execute("""SELECT * FROM users WHERE active=1""")
    results = cursor.fetchall()

    if results:
        users = []
        for result in results:
            user_record = {
            'user_id':result[0],
            'first_name':result[1],
            'last_name':result[2],
            'email':result[3],
            'phone':result[4],
            'city':result[5],
            'state':result[6],
            'org_id':result[7],
            'active':result[8]
            }
            users.append(user_record)
        return jsonify(users), 200

    else:
      return jsonify('No users in database')   




@app.route('/user/update/<user_id>', methods=['PUT','POST'])
def update_user(user_id):

    update_fields = []
    update_values = []
    field_names = ['first_name',"last_name",'email','phone','city','state','org_id','active']

    post_data = request.json
    if not post_data:
        post_data = request.form


    for field in field_names:
        field_value = post_data.get(field)
        if field_value:
            update_fields.append(str(field) + '=%s')
            update_values.append(field_value)

    if update_fields:
        update_values.append(user_id)
        query_string = f"UPDATE users SET " + ', '.join(update_fields) + " WHERE user_id=%s"
        cursor.execute(query_string, update_values)
        conn.commit()

        return jsonify('user updated'), 200
    else:
        return jsonify('No user found'), 404





@app.route('/user-delete/<user_id>')
def delete_user(user_id):
    cursor.execute('SELECT user_id FROM users WHERE user_id=%s',(user_id,))
    result = cursor.fetchone()
    print(result[0])
    if result:
        cursor.execute("""DELETE FROM users WHERE user_id=%s""",[user_id])
        conn.commit()
        return jsonify('User Record Deleted'), 200
    else:
        return jsonify('No user found'), 404




@app.route('/user/activate/<user_id>', methods=['PATCH'])
def activate_user(user_id):
    cursor.execute('SELECT user_id FROM users WHERE user_id=%s',(user_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute("""UPDATE users SET active=1 WHERE user_id=%s""",(user_id,))
        conn.commit()
        return jsonify(f'Activated user id: {user_id}'), 200
    else:
        return jsonify('No user found'), 404




@app.route('/user/deactivate/<user_id>', methods=['PATCH'])
def deactivate_user(user_id):
    cursor.execute('SELECT user_id FROM users WHERE user_id=%s',(user_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute("""UPDATE users SET active=0 WHERE user_id=%s""",(user_id,))
        conn.commit()
        return jsonify(f'Deactivated user id: {user_id}'), 200
    else:
        return jsonify('No user found'), 404




if __name__ == '__main__':
    create_all()
    app.run(port=8089)

