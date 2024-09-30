import os
from flask import Flask,send_from_directory, request, render_template, jsonify
import joblib
from Funciones import descargar_imagenes_api, enviar_correo, extract_caracteristicas, categorize_predictions,get_images_from_folder,get_ropa_descriptions
from vectorize import preprocess_and_vectorize
#import xgboost

'''

def install_requirements():
    if os.path.exists('requirements.txt'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("El archivo requirements.txt no se encontró. Por favor, asegúrate de que el archivo exista en el directorio.")
'''



# Cargar modelos previamente entrenados y guardados con joblib

modelo = joblib.load('./Models/modelo.pkl')
vectorizador = joblib.load('./Models/vectorizador (1).pkl')

# Crear una instancia de la aplicación Flask
app = Flask(__name__)


# Ruta para la página de inicio
@app.route('/')
def home():
    return render_template('Index.html')


@app.route('/model')
def model():
    return render_template('model.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        mensaje = data.get('mensaje')

        # Llamar a la función para enviar el correo
        resultado = enviar_correo(nombre, mensaje)

        return jsonify({'status': 'success', 'message': resultado})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extraer datos JSON del cuerpo de la solicitud
        data = request.get_json()
        texto = data['texto']
        #cantidad = data['cantidad']
        

        # Crear un DataFrame a partir de los datos JSON
        df = extract_caracteristicas(texto)
        print(df)
        # Procesar el DataFrame y vectorizar
        df_final = preprocess_and_vectorize(df, vectorizador)

        # Realizar la predicción
        prediccion = modelo.predict(df_final)
        print(prediccion)

        # Categorizar la predicción
        Ropa = categorize_predictions(prediccion)
        print(Ropa)
        genero = 'man' if df['genero'].iloc[0] == 'hombre' else 'woman'
       
        query = Ropa+" for "+genero
        
        objetos = descargar_imagenes_api(Ropa)
        
        # Construir la ruta a las imágenes basándote en la subcarpeta
        path = './static/images/' + Ropa + '/'
        
        print("Carpeta:", Ropa)

        # Buscar imágenes en la ruta
        imagenes = []
        if os.path.exists(path):
            print("Existe la ruta:", path)
            imagenes = get_images_from_folder(path)
        else:
            print("No existe la ruta:", path)

        # Preparar la respuesta
        respuesta = {
            'consejo': get_ropa_descriptions(Ropa),
            'products': objetos
        }

        return jsonify(respuesta)

    except Exception as e:
        # Manejar cualquier error que ocurra durante la predicción
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("server iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)
    