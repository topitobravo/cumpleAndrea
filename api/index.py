from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
import jwt
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from db import SupabaseClient
from unidecode import unidecode

ROUTES={
    'register': "/oajspoihpifojapoisjpiodsa"

}

app = Flask(__name__)
app.config['JWT_SECRET'] = "aspoifjiopsjcpoijaspiojcpoiajsipojapoisiodads"

supabase: Client = SupabaseClient().get_client()

@app.template_filter('mes_nombre')
def mes_nombre(numero):
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return meses.get(numero, "Mes inválido")

app.jinja_env.filters['month_name'] = mes_nombre

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
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')



@app.route('/')
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
        regular_riddles = [r for r in all_riddles if r['type'] == 'regular']
        
        # Obtener el acertijo mensual actual (basado en mes/año actual)
        current_date = datetime.now()
        monthly_riddle = supabase.table('riddles') \
                               .select('*') \
                               .eq('type', 'monthly') \
                               .eq('month', current_date.month) \
                               .eq('year', current_date.year) \
                               .execute() \
                               .data
        monthly_riddle = monthly_riddle[0]
        # Obtener progreso del usuario
        progress = supabase.table('user_progress') \
                          .select('riddle_id, solved_at') \
                          .eq('user_id', user_id) \
                          .execute() \
                          .data

        monthly_status = {
            'available': False,
            'next_attempt': None
        }
          # Crear diccionario de progreso
        solved_riddles = {p['riddle_id']: datetime.fromisoformat(p['solved_at']) 
                        for p in progress if p['solved_at']}
        if monthly_riddle:
            last_solved = solved_riddles.get(monthly_riddle['id'])
            if last_solved:
                monthly_status['available'] = True
                next_month_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            else:
                next_month_date = None
        return render_template('index.html',
            user=request.user,
            riddles=regular_riddles,
            monthly_riddle=monthly_riddle,
            solved_riddles=solved_riddles,
            monthly_status=monthly_status,
            current_date=datetime.now(),
            next_month_date = next_month_date
        )

    except Exception as e:
        app.logger.error(f'Error en index: {str(e)}')
        return render_template('error.html', message="Error cargando los acertijos"), 500

@app.route('/bienvenida', methods=['GET', 'POST'])
def bienvenida():
    inicial = supabase.table('riddles').select('*').eq('name', 'Inicial').execute().data[0]
    if request.method == 'POST':
        answer = request.form.get('respuesta')
        if comparar_strings(answer,inicial['answer']):
            return make_response(redirect(url_for('register')))
        else:
            return render_template('bienvenida.html', error="Vuelvelo a intentar. Venga, esta es muy facil :)")
    
    return render_template('bienvenida.html',pregunta=inicial['question'])


#login
@app.route('/login', methods=['GET', 'POST'])
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
def solve_riddle(riddle_id):
    riddle = supabase.table('riddles').select('*').eq('id', riddle_id).execute().data
    if not riddle:
        return redirect(url_for('index'))
    
    riddle = riddle[0]
    progress = supabase.table('user_progress').select('*').match({
        'user_id': request.user['id'],
        'riddle_id': riddle_id
    }).execute().data
    
    if request.method == 'POST':
        answer = request.form.get('respuesta', '').strip().lower()
        if comparar_strings(answer,riddle['answer']):
            # Registrar progreso
            supabase.table('user_progress').upsert({
                'user_id': request.user['id'],
                'riddle_id': riddle_id,
                'solved_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            
            return render_template('clue.html', pista=riddle['hint'])
        
        return render_template('riddle.html', 
                             riddle=riddle,
                             error='Respuesta incorrecta')
    
    return render_template('riddle.html', riddle=riddle)

@app.route('/monthly', methods=['GET', 'POST'])
@jwt_required
def monthly_riddle():
        user_id = request.user['id']
        current_date = datetime.now(timezone.utc)
        
        # Obtener acertijo mensual actual (mes/año actual)
        monthly_riddle = supabase.table('riddles') \
                               .select('*') \
                               .eq('type', 'monthly') \
                               .eq('month', current_date.month) \
                               .eq('year', current_date.year) \
                               .execute().data

        if not monthly_riddle:
            return render_template('error.html', 
                                 error="No hay acertijo mensual disponible"), 404

        monthly_riddle = monthly_riddle[0]
        # Verificar si ya resolvió ESTE MES
        solved_this_month = supabase.table('user_progress') \
                                  .select('solved_at') \
                                  .eq('user_id', user_id) \
                                  .eq('riddle_id', monthly_riddle['id']) \
                                  .not_.is_('solved_at', 'null') \
                                  .execute().data

        # Manejar POST
        error = None
        success = False
        if request.method == 'POST' and not solved_this_month:
            respuesta = request.form.get('respuesta', '').strip().lower()
            
            # Registrar intento
            
            
            if comparar_strings(respuesta,monthly_riddle['answer']):
                # Marcar como resuelto
                supabase.table('user_progress').upsert({
                    'user_id': user_id,
                    'riddle_id': monthly_riddle['id'],
                    'solved_at': current_date.isoformat()
                }).execute()
                success = True
                solved_this_month = True
            else:
                supabase.table('user_progress').upsert({
                'user_id': user_id,
                'riddle_id': monthly_riddle['id'],
                'attempts': monthly_riddle.get('attempts', 0) + 1,
                'last_attempt': current_date.isoformat()
            }).execute()
                error = "Respuesta incorrecta. ¡Sigue intentándolo!"

        # Calcular próximo mes disponible
        next_month_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        return render_template('monthly.html',
            monthly_riddle=monthly_riddle,
            solved=solved_this_month,
            success=success,
            error=error,
            next_month_date=next_month_date
        )

        app.logger.error(f'Error en mensual: {str(e)}')
        return render_template('error.html', 
                            error="Error al cargar el acertijo mensual"), 500
@app.route('/riddle/<string:riddle_id>', methods=['GET', 'POST'])
@jwt_required
def riddle(riddle_id):
    try:
        # Obtener usuario y riddle
        user_id = request.user['id']
        riddle = supabase.table('riddles') \
                      .select('*') \
                      .eq('id', riddle_id) \
                      .single() \
                      .execute()
        riddle = riddle.data
        
        # Verificar si ya fue resuelta
        progreso = supabase.table('user_progress') \
                         .select('solved_at') \
                         .eq('user_id', user_id) \
                         .eq('riddle_id', riddle_id) \
                         .execute()
        
        if progreso.data:
            return render_template('clue.html', 
                                 pista=riddle['hint'],
                                 tipo='éxito')

        # Manejar POST
        if request.method == 'POST':
            respuesta = request.form.get('respuesta', '').strip().lower()
            
            if respuesta == riddle['answer'].lower():
                # Registrar en Supabase
                supabase.table('user_progress').insert({
                    'user_id': user_id,
                    'riddle_id': riddle_id,
                    'solved_at': datetime.now(timezone.utc).isoformat()
                }).execute()
                
                return render_template('clue.html', 
                                     pista=riddle['hint'],
                                     tipo='éxito')
            else:
                # Registrar intento fallido
                supabase.table('user_progress').upsert({
                    'user_id': user_id,
                    'riddle_id': riddle_id,
                    'attempts': riddle.get('attempts', 0) + 1
                }).execute()
                
                return render_template('riddle.html',
                                     riddle=riddle,
                                     error='Respuesta incorrecta 😿')

        # Renderizar riddle
        return render_template('riddle.html',
                             riddle=riddle)

    except Exception as e:
        app.logger.error(f'Error en riddle: {str(e)}')
        return redirect(url_for('index'))

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