from flask import Flask, render_template, request, json, redirect,session

# python -m pip install flask https://code.visualstudio.com/docs/python/tutorial-flask
# pip install Flask-SQLAlchemy psycopg2
import psycopg2


db_name = "colegio"
db_user = "postgres"
db_password = "admin"
db_host = "localhost"
db_port = "5432"

app = Flask(__name__)
app.secret_key = 'secreto'
# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                        host=db_host, port=db_port)
cur = conn.cursor()

conn.commit() 
  
cur.close() 
conn.close() 


@app.route("/")
def main():
    #session.pop('user', None)
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp', methods = ['POST','GET'])
def signUp():
    _dni = request.form['inputDNI']
    _nombre = request.form['inputNombre']
    _p_apellido = request.form['inputP_Apellido']
    _s_apellido = request.form['inputS_Apellido']
    _direccion = request.form['inputDireccion']
    _telefono = request.form['inputTelefono']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    if _dni and _nombre and _p_apellido and _s_apellido and _direccion and _telefono and _email and _password:
        try: 
            conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                            host=db_host, port=db_port)
            if (conn):
                print("Conexion establecida")
            else:
                print("Conexion fallida")
            cursor = conn.cursor()
            cursor.execute("CALL crearCliente(%s, %s,%s, %s,%s, %s,%s, %s );",(_dni, _nombre, _p_apellido, _s_apellido, _direccion, _telefono, _email, _password))
               
            conn.commit()
            print("Usuario fue creado!")
            return json.dumps({'mensaje':'usuario fue creado!'})
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            return json.dumps({'error': f"Error al ejecutar el procedimiento almacenado: {e}"})

    else:
        return json.dumps({'mensaje': 'Campos estan vacios!'})
    cursor.close()
    conn.close()


@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('dashboard.html')
    else:
        return render_template('signin.html')




@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/validateLogin', methods = ['POST'])
def validateLogin():
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    
    conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                    host=db_host, port=db_port)

    cursor = conn.cursor()
    cursor.callproc('validarLogin',(_username,))
    data = cursor.fetchall()
    if len(data)>0:
        if str(data[0][4]) == _password:
            session['user'] = data[0][0]
            return redirect('/dashboard')
        else:
            return render_template('error.html', error='Usuario o contraseña es incorrecta')
    else:
        return render_template('error.html', error = 'Usuario no existe')
    cursor.close()
    conn.close()
    

@app.route('/userHome')
def userHome():
    if session.get('user'):
        # Obtener la lista de deseos del usuario
        _user = session.get('user')
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.callproc('obtenerdocentes', (_user,))
        data = cursor.fetchall()
        wishes_list = []
        for wish in data:
            wish_data = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2],
                'Date': wish[3]
            }
            wishes_list.append(wish_data)
        return render_template('userHome.html', wishes=wishes_list)
    else:
        return render_template('error.html', error='Acceso No Autorizado')


@app.route('/addWish', methods=['POST'])
def addWish():
    if session.get('user'):
        _id_docente = request.form['inputId']
        _nombre = request.form['inputNombre']
        _edad = request.form['inputEdad']
        _celular = request.form['inputCelular']
        _id_colegio = request.form['IdColegio']
        _id_taller = request.form['IdTaller']
        try:
            conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                        host=db_host, port=db_port)
       
            cursor = conn.cursor()
            cursor.execute("CALL agregarDocente(%s, %s, %s,%s,%s,%s);",(_id_docente,_nombre, _edad, _celular,_id_colegio, _id_taller ))
               
            conn.commit()
            return redirect('dashboard')
            return json.dumps({'mensaje':'usuario fue creado!'})
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            return render_template('error.html', error='Un error detectado')

    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/addTaller', methods=['POST'])
def addTaller():
    if session.get('user'):
        _id_taller = request.form['inputId']
        _nombre = request.form['inputNombre']
        _horario = request.form['inputHorario']
        _precio = request.form['inputPrecio']
        _vacantes = request.form['imputVacantes']
        try:
            conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                        host=db_host, port=db_port)
       
            cursor = conn.cursor()
            cursor.execute("CALL agregartaller( %s, %s,%s,%s,%s);",(_id_taller,_nombre, _horario, _precio,_vacantes))
               
            conn.commit()
            return redirect('talleres')
            return json.dumps({'mensaje':'usuario fue creado!'})
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            return render_template('error.html', error='Un error detectado')

    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close
        
@app.route('/addAlumno', methods=['POST'])
def addAlumno():
    if session.get('user'):
        _id_taller = request.form['inputId']
        _nombre = request.form['inputNombre']
        _edad = request.form['inputEdad']
        _celular = request.form['inputCelular']
        _direccion = request.form['imputDireccion']
        try:
            conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                        host=db_host, port=db_port)
       
            cursor = conn.cursor()
            cursor.execute("CALL agregarAlumno( %s, %s,%s,%s,%s);",(_id_taller,_nombre, _edad, _celular,_direccion))
               
            conn.commit()
            return redirect('alumnos')
            return json.dumps({'mensaje':'usuario fue creado!'})
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            return render_template('error.html', error='Un error detectado')

    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/addMatricula', methods=['POST'])
def addMatricula():
    if session.get('user'):
        _id_matricula = request.form['inputIdMatricula']
        _id_alumno = request.form['inputIdAlumno']
    
        try:
            conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                        host=db_host, port=db_port)
       
            cursor = conn.cursor()
            cursor.execute("CALL agregarMatricula( %s,%s);",(_id_matricula,_id_alumno))
               
            conn.commit()
            return redirect('matriculas')
            return json.dumps({'mensaje':'usuario fue creado!'})
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            return render_template('error.html', error='Un error detectado')

    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/addMatriculaDetalle', methods=['POST'])
def addMatriculaDetalle():
    if session.get('user'):
        _id_taller = request.form['inputIdTaller']
        _id_matricula = request.form['inputIdMatricula']
    
        try:
            conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                        host=db_host, port=db_port)
       
            cursor = conn.cursor()
            cursor.execute("CALL agregarDetalleMatricula( %s,%s);",(_id_taller,_id_matricula))
               
            conn.commit()
            return redirect('matriculas')
            return json.dumps({'mensaje':'usuario fue creado!'})
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            return render_template('error.html', error='Un error detectado')

    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/showAddWish')
def showAddWish():
    return render_template('addWish.html')


@app.route('/getWish')
def getWish():
    if session.get('user'):
        _user = session.get('user')

        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                    host=db_host, port=db_port)

        cursor = conn.cursor()
        cursor.callproc('obtenerdocentes', (_user,))
        data = cursor.fetchall()
        deseos_list = []
        for deseo in data:
            deseo_list = {
                'Id': deseo[0],
                'Title': deseo[1],
                'Description': deseo[2],
                'Date': deseo[3],
                'Taller': deseo[5]

                }
            deseos_list.append(deseo_list)
        return json.dumps(deseos_list)
    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/getTaller')
def getTaller():
    if session.get('user'):
        _user = session.get('user')

        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                    host=db_host, port=db_port)

        cursor = conn.cursor()
        cursor.callproc('obtenertalleres', (_user,))
        data = cursor.fetchall()
        deseos_list = []
        for deseo in data:
            deseo_list = {
                'Id': deseo[0],
                'Title': deseo[1],
                'Description': deseo[2],
                'Date': deseo[3],
                'Taller': deseo[4]

                }
            deseos_list.append(deseo_list)
        return json.dumps(deseos_list)
    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/getAlumnos')
def getAlumnos():
    if session.get('user'):
        _user = session.get('user')

        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                    host=db_host, port=db_port)

        cursor = conn.cursor()
        cursor.callproc('obteneralumnos', (_user,))
        data = cursor.fetchall()
        deseos_list = []
        for deseo in data:
            deseo_list = {
                'Id': deseo[0],
                'Title': deseo[1],
                'Description': deseo[2],
                'Date': deseo[3],
                'Taller': deseo[4]

                }
            deseos_list.append(deseo_list)
        return json.dumps(deseos_list)
    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close
@app.route('/getMatriculas')
def getMatriculas():
    if session.get('user'):
        _user = session.get('user')

        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                    host=db_host, port=db_port)

        cursor = conn.cursor()
        cursor.callproc('obtenermatriculas', (_user,))
        data = cursor.fetchall()
        deseos_list = []
        for deseo in data:
            deseo_list = {
                'Id': deseo[0],
                'Title': deseo[1],
                
                }
            deseos_list.append(deseo_list)
        return json.dumps(deseos_list)
    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close

@app.route('/editDocente/<int:id_docente>', methods=['POST'])
def editDocente(id_docente):
    if session.get('user'):
        # Actualizar el deseo en la base de datos
        nombre_docente = request.form['inputNombre']
        edad = request.form['inputEdad']
        celular = request.form['inputCel']
        id_colegio = request.form['inputIdColegio']
        id_taller = request.form['inputIdTaller']

        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.execute("SELECT editarDocente(%s, %s, %s,%s,%s,%s);", (id_docente, nombre_docente, edad,celular,id_colegio, id_taller ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    else:
        return render_template('error.html', error='Acceso no Autorizado')
    

@app.route('/dashboard')
def dashboard():
    if session.get('user'):
        # Obtener la lista de deseos del usuario
        _user = session.get('user')
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.callproc('obtenerdocentes', (_user,))
        data = cursor.fetchall()
        wishes_list = []
        for wish in data:
            wish_data = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2],
                'Date': wish[3],
                'Taller': wish[5]

            }
            wishes_list.append(wish_data)
        return render_template('dashboard.html', wishes=wishes_list)
    else:
        return render_template('error.html', error='Acceso No Autorizado')
    
@app.route('/talleres')
def talleres():
    if session.get('user'):
        # Obtener la lista de deseos del usuario
        _user = session.get('user')
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.callproc('obtenertalleres', (_user,))
        data = cursor.fetchall()
        wishes_list = []
        for wish in data:
            wish_data = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2],
                'Date': wish[3],
                'Taller': wish[4]

            }
            wishes_list.append(wish_data)
        return render_template('talleres.html', wishes=wishes_list)
    else:
        return render_template('error.html', error='Acceso No Autorizado')

@app.route('/alumnos')
def alumnos():
    if session.get('user'):
        # Obtener la lista de deseos del usuario
        _user = session.get('user')
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.callproc('obteneralumnos', (_user,))
        data = cursor.fetchall()
        wishes_list = []
        for wish in data:
            wish_data = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2],
                'Date': wish[3],
                'Taller': wish[4]

            }
            wishes_list.append(wish_data)
        return render_template('alumnos.html', wishes=wishes_list)
    else:
        return render_template('error.html', error='Acceso No Autorizado')
    
@app.route('/matriculas')
def matriculas():
    if session.get('user'):
        # Obtener la lista de deseos del usuario
        _user = session.get('user')
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.callproc('obtenermatriculas', (_user,))
        data = cursor.fetchall()
        wishes_list = []
        for wish in data:
            wish_data = {
                'Id': wish[0],
                'Title': wish[1],

            }
            wishes_list.append(wish_data)
        return render_template('matriculas.html', wishes=wishes_list)
    else:
        return render_template('error.html', error='Acceso No Autorizado')
    
@app.route('/deleteDocente/<int:id_docente>', methods=['GET'])
def deleteDocente(id_docente):
    if session.get('user'):
        # Eliminar el deseo de la base de datos
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.execute("SELECT eliminarDocente(%s);", (id_docente,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    else:
        return render_template('error.html', error='Acceso no Autorizado')

@app.route('/deleteAlumno/<int:id_Alumno>', methods=['GET'])
def deleteAlumno(id_Alumno):
    if session.get('user'):
        # Eliminar el deseo de la base de datos
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.execute("SELECT eliminarAlumno(%s);", (id_Alumno,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    else:
        return render_template('error.html', error='Acceso no Autorizado')

@app.route('/deleteTaller/<int:id_taller>', methods=['GET'])
def deleteTaller(id_taller):
    if session.get('user'):
        # Eliminar el deseo de la base de datos
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.execute("SELECT eliminarTaller(%s);", (id_taller,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    else:
        return render_template('error.html', error='Acceso no Autorizado')

@app.route('/deleteMatricula/<int:id_matricula>', methods=['GET'])
def deleteMatricula(id_matricula):
    if session.get('user'):
        # Eliminar el deseo de la base de datos
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.execute("SELECT eliminarMatricula(%s);", (id_matricula,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    else:
        return render_template('error.html', error='Acceso no Autorizado')

@app.route('/detalle_matricula')
def detalle_matricula():
    if session.get('user'):
        # Obtener la lista de deseos del usuario
        _user = session.get('user')
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.callproc('obtener_info_matricula', ())
        data = cursor.fetchall()
        wishes_list = []
        for wish in data:
            wish_data = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2],
                'Date': wish[3],
                'Taller': wish[4]

            }
            wishes_list.append(wish_data)
        return render_template('detalle_matricula.html', wishes=wishes_list)
    else:
        return render_template('error.html', error='Acceso No Autorizado')
@app.route('/getDetalle')
def getDetalle():
    if session.get('user'):
        _user = session.get('user')

        conn = psycopg2.connect(database=db_name, user=db_user, password=db_password,
                    host=db_host, port=db_port)

        cursor = conn.cursor()
        cursor.callproc('obtener_info_matricula', ())
        data = cursor.fetchall()
        deseos_list = []
        for deseo in data:
            deseo_list = {
                'Id': deseo[0],
                'Title': deseo[1],
                'Description': deseo[2],
                'Date': deseo[3],
                'Taller': deseo[4]

                }
            deseos_list.append(deseo_list)
        return json.dumps(deseos_list)
    else:
        return render_template('error.html', error='Acceso no Autorizado')
    cursor.close
    conn.close    


if __name__ == "__main__":
    app.run()


