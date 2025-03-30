from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

DATABASE = 'data.json'

# Configura tus adivinanzas y respuestas aquí
RIDDLES = {
    '1': {
        'pregunta': 'Adivinanza 1: Oro parece, plata no es...',
        'respuesta': 'plátano',
        'pista': 'Está en la nevera'
    },
    '2': {
        'pregunta': 'Adivinanza 2: Sin pies ni manos, sube a la montaña...',
        'respuesta': 'humo',
        'pista': 'Busca en el armario de la entrada'
    },
    '3': {
        'pregunta': 'Adivinanza 3: Blanca por dentro, verde por fuera...',
        'respuesta': 'pera',
        'pista': 'Mirar debajo de la cama'
    },
    '4': {
        'pregunta': 'Adivinanza 4: Redondo como una luna, lleno de estrellas...',
        'respuesta': 'reloj',
        'pista': 'En el cajón del escritorio'
    },
    'mensual': {
        'pregunta': 'Adivinanza Mensual: Con llaves pero no soy puerta...',
        'respuesta': 'teclado',
        'pista': 'Regalo mensual en el jardín'
    }
}

def cargar_datos():
    if not os.path.exists(DATABASE):
        datos_iniciales = {
            'riddles': {str(i): False for i in range(1, 5)},
            'mensual': {'ultimo_intento': None, 'resuelto': False}
        }
        with open(DATABASE, 'w') as f:
            json.dump(datos_iniciales, f)
    
    with open(DATABASE, 'r') as f:
        return json.load(f)

def guardar_datos(datos):
    with open(DATABASE, 'w') as f:
        json.dump(datos, f)

@app.route('/')
def inicio():
    datos = cargar_datos()
    return render_template('index.html', 
                         riddles=datos['riddles'],
                         mensual=datos['mensual'])

@app.route('/riddle/<int:id>', methods=['GET', 'POST'])
def adivinanza(id):
    datos = cargar_datos()
    id_str = str(id)
    
    if datos['riddles'][id_str]:
        return render_template('clue.html', 
                            pista=RIDDLES[id_str]['pista'])
    
    if request.method == 'POST':
        if request.form['respuesta'].lower() == RIDDLES[id_str]['respuesta']:
            datos['riddles'][id_str] = True
            guardar_datos(datos)
            return redirect(url_for('inicio'))
        
        return render_template('riddle.html', 
                             riddle=RIDDLES[id_str],
                             error='Respuesta incorrecta')
    
    return render_template('riddle.html', 
                         riddle=RIDDLES[id_str])

@app.route('/mensual', methods=['GET', 'POST'])
def mensual():
    datos = cargar_datos()
    mensual_data = datos['mensual']
    
    if mensual_data['resuelto']:
        return render_template('clue.html', 
                            pista=RIDDLES['mensual']['pista'])
    
    ahora = datetime.now()
    
    if request.method == 'POST':
        if mensual_data['ultimo_intento']:
            ultimo_intento = datetime.fromisoformat(mensual_data['ultimo_intento'])
            if ahora < ultimo_intento + timedelta(days=30):
                return render_template('monthly.html',
                                      error='Debes esperar hasta el próximo mes')
        
        if request.form['respuesta'].lower() == RIDDLES['mensual']['respuesta']:
            mensual_data['resuelto'] = True
            mensual_data['ultimo_intento'] = ahora.isoformat()
            guardar_datos(datos)
            return redirect(url_for('inicio'))
        
        mensual_data['ultimo_intento'] = ahora.isoformat()
        guardar_datos(datos)
        return render_template('monthly.html',
                              error='Respuesta incorrecta')
    
    return render_template('monthly.html')

# if __name__ == '__main__':
#     app.run(debug=True)
 