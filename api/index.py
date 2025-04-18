from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
import jwt
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from unidecode import unidecode

ROUTES={
    'register': "/oajspoihpifojapoisjpiodsa",
    'login' : "/aoisjhfopishfpiojahsipjfioas",
    'index' : "/caca",
    'aviso' : "/jahcdjhioajsiojciojasocojsisd", #hecho
    'ruta1' : "/asfasfgasfsaafsadfassagasgs",
    'ruta2' : "/safasefwaefwaefaawefawefwf",
    'ruta3' : "/fwafasfasfsefasfasefasfas",
    'ruta4' : "/afsfsafsafsaefasefeasefaea",
    'ruta5' : "/afasfseafsafafeafafafeaef",
    'ruta6s' : "/afefasfesafsaeaeafasfaeasfa",
    'bienvenida' : "/bienvenida"
}

app = Flask(__name__)
app.config['JWT_SECRET'] = "aspoifjiopsjcpoijaspiojcpoiajsipojapoisiodads"
POSTGRES_URL="postgres://postgres.ymhqxdxgjmkqqnogyaxx:gRNRbBi3FNvd2JTM@aws-0-eu-west-2.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"
POSTGRES_PRISMA_URL="postgres://postgres.ymhqxdxgjmkqqnogyaxx:gRNRbBi3FNvd2JTM@aws-0-eu-west-2.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"
SUPABASE_URL="https://ymhqxdxgjmkqqnogyaxx.supabase.co"
NEXT_PUBLIC_SUPABASE_URL="https://ymhqxdxgjmkqqnogyaxx.supabase.co"
POSTGRES_URL_NON_POOLING="postgres://postgres.ymhqxdxgjmkqqnogyaxx:gRNRbBi3FNvd2JTM@aws-0-eu-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
SUPABASE_JWT_SECRET="jQXOLyGohIFgF8zwyMr3ATgvse9C6L4b792/opLocrNZzzsJOx43Pf3sHHro+6z5vKGDmkbvMhRC7IY3lrcbPw=="
POSTGRES_USER="postgres"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltaHF4ZHhnam1rcXFub2d5YXh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzNzAwOTYsImV4cCI6MjA1ODk0NjA5Nn0.igwPOKAqXoot3OnE6n3W1rti3GhAaHj6K-rqiUi_3lA"
POSTGRES_PASSWORD="gRNRbBi3FNvd2JTM"
POSTGRES_DATABASE="postgres"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltaHF4ZHhnam1rcXFub2d5YXh4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzM3MDA5NiwiZXhwIjoyMDU4OTQ2MDk2fQ.Zx8ShbefCCIE87PN02n1XGCtc5XItVP009Hr2RW9kFw"
POSTGRES_HOST="db.ymhqxdxgjmkqqnogyaxx.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltaHF4ZHhnam1rcXFub2d5YXh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzNzAwOTYsImV4cCI6MjA1ODk0NjA5Nn0.igwPOKAqXoot3OnE6n3W1rti3GhAaHj6K-rqiUi_3lA"




@app.template_filter('mes_nombre')
def mes_nombre(numero):
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return meses.get(numero, "Mes inválido")

app.jinja_env.filters['month_name'] = mes_nombre


class SupabaseClient:
    def __init__(self):
        self.url: str = SUPABASE_URL
        self.key: str = SUPABASE_ANON_KEY
        self.client: Client = create_client(self.url, self.key)

    def get_client(self):
        return self.client

supabase: Client = SupabaseClient().get_client()

# Decorador para proteger rutas
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return redirect(url_for('login'))
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
            user = supabase.table('users').select('*').eq('id', payload['sub']).execute().data
            if not user:
                return redirect(url_for('login'))
            request.user = user[0]
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def comparar_strings(s1, s2):
    return unidecode(s1).lower() == unidecode(s2).lower()

def create_jwt(user_id):
    payload = {
        'sub': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=10),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')



@app.route(ROUTES['index'])
@jwt_required
def index():
    try:
        # Obtener usuario actual
        user_id = request.user['id']

        # Obtener todas las adivinanzas activas
        all_riddles = supabase.table('riddles') \
                            .select('*') \
                            .execute() \
                            .data

        # Separar adivinanzas regulares y mensuales
        riddles_regalo = [r for r in all_riddles if r['type'] == 'regalo']
        riddles_regalo = sorted(riddles_regalo,key=lambda x:x['indice'])
        riddles_viernes = [r for r in all_riddles if r['type'] == 'viernes' and r['indice'] !=1]
        riddles_viernes =  sorted(riddles_viernes,key=lambda x:x['indice'])

        progress = supabase.table('user_progress') \
                    .select('riddle_id, solved_at') \
                    .eq('user_id', user_id) \
                    .execute() \
                    .data

          # Crear diccionario de progreso
        solved_riddles = {p['riddle_id']: datetime.fromisoformat(p['solved_at'])
                        for p in progress if p['solved_at']}

        return render_template('index.html',
            user=request.user,
            riddles_regalo=riddles_regalo,
            solved_riddles=solved_riddles,
            riddles_viernes=riddles_viernes
        )

    except Exception as e:
        app.logger.error(f'Error en index: {str(e)}')
        return render_template('error.html', message="Error cargando los acertijos"), 500

@app.route(ROUTES['aviso'], methods=['GET', 'POST'])
def aviso():
    if request.method == 'POST':
        respuesta = request.form.get('respuesta', '').strip().lower()
        if respuesta != "":
            supabase.table('respuesta').upsert({
                'respuesta': respuesta,
            }).execute()
            return render_template('aviso2.html', respuesta = "Gracias!! Respuesta registrada <3")
        else:
            return render_template('aviso.html')
    return render_template('aviso2.html')

@app.route('/bienvenida', methods=['GET', 'POST'])
def bienvenida():
    return redirect(url_for('aviso'))

@app.route('/cacaculopedopis', methods=['GET', 'POST'])
def cacaculopedopis():
    return redirect(url_for('welcome'))

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    inicial = supabase.table('riddles').select('*').eq('type', 'inicial').execute().data[0]
    if request.method == 'POST':
        answer = request.form.get('respuesta')
        if comparar_strings(answer,inicial['answer']):
            return make_response(redirect(url_for('register')))
        else:
            return render_template('bienvenida.html', error="Vuelvelo a intentar. Venga, esta es muy facil :)")

    return render_template('bienvenida.html',pregunta=inicial['question'])

#login
@app.route(ROUTES['login'], methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = supabase.table('users').select('*').eq('username', username).execute().data
        if not user or not check_password_hash(user[0]['password_hash'], password):
            return render_template('auth/login.html', error='Credenciales inválidas')

        response = make_response(redirect(url_for('index')))
        token = create_jwt(user[0]['id'])
        response.set_cookie('access_token', token, httponly=True)
        return response

    return render_template('auth/login.html')

@app.route(ROUTES['register'], methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))

        try:
            user = supabase.table('users').insert({
                'username': username,
                'password_hash': password,
                'is_admin': False
            }).execute().data

            response = make_response(redirect(url_for('index')))
            token = create_jwt(user[0]['id'])
            response.set_cookie('access_token', token, httponly=True, secure=True)
            return response
        except Exception as e:
            return render_template('auth/register.html', error='Error al registrar usuario')

    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('access_token')
    return response

@app.route('/riddle/<riddle_id>', methods=['GET', 'POST'])
@jwt_required
def handle_riddle(riddle_id):
    user_id = request.user['id']
    progress = supabase.table('user_progress') \
                .select('riddle_id, solved_at') \
                .eq('user_id', user_id) \
                .execute() \
                .data
    # Crear diccionario de progreso
    solved_riddles = {p['riddle_id']: datetime.fromisoformat(p['solved_at'])
                    for p in progress if p['solved_at']}

    riddle = supabase.table('riddles').select('*').eq('id', riddle_id).execute().data
    if not riddle:
        return redirect(url_for('index'))

    riddle = riddle[0]

    print(riddle)
    if riddle['id']  in solved_riddles:
        solved = True
    elif riddle['type'] == 'viernes' and riddle['indice'] == 0:
        solved = True
    else:
        solved = False

    if request.method == 'POST':
        if solved:
            return render_template('clue.html', riddle=riddle)
        answer = request.form.get('respuesta', '').strip().lower()
        if comparar_strings(answer,riddle['answer']):
            # Registrar progreso
            supabase.table('user_progress').upsert({
                'user_id': request.user['id'],
                'riddle_id': riddle_id,
                'solved_at': datetime.now(timezone.utc).isoformat()
            }).execute()

            return render_template('clue.html', riddle=riddle)
        else:
           supabase.table('user_progress').upsert({
                'user_id': request.user['id'],
                'riddle_id': riddle_id,
                'last_attempt': datetime.now(timezone.utc).isoformat(),
                'tried_answer': answer
            }).execute()

        return render_template('riddle.html',
                             riddle=riddle,
                             error='Respuesta incorrecta')
    else:
        if solved:
            return render_template('clue.html', riddle=riddle)
    return render_template('riddle.html', riddle=riddle)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)