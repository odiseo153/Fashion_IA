from features import personalidades, caracteristicas_fisicas, Eventos, generos
import spacy
import pandas as pd
from labels import ropa,clothing
import os
from fuzzywuzzy import fuzz, process
import numpy as np
import yagmail
import requests
from dotenv import load_dotenv

load_dotenv()

# Cargar el modelo de lenguaje en español
nlp = spacy.load("es_core_news_sm")

def fuzzy_match(token, choices, threshold=80):
    match, score = process.extractOne(token, choices, scorer=fuzz.token_sort_ratio)
    if score >= threshold:
        return match
    return None


def extract_caracteristicas(text):
    # Procesar el texto con spaCy
    doc = nlp(text.lower())
    
    # Inicializar resultados
    found_caracteristicas_fisicas = {}
    found_personalidades = []
    found_eventos = ""
    found_genero = "desconocido"

    # Convertir características físicas, eventos y géneros a minúsculas para comparación
    caracteristicas_fisicas_lower = {k.lower(): [v.lower() for v in vs] for k, vs in caracteristicas_fisicas.items()}
    eventos_lower = [e.lower() for e in Eventos["Evento"]]
    personalidades_lower = [p.lower() for p in personalidades]
    
    generos_m_lower = [g.lower() for g in generos['M']]
    generos_f_lower = [g.lower() for g in generos['F']]

    # Buscar personalidades en el texto usando fuzzy matching
    for token in doc:
        match = fuzzy_match(token.text.lower(), personalidades_lower)
        if match:
            found_personalidades.append(match)

    # Buscar características físicas en el texto
    for key, values in caracteristicas_fisicas_lower.items():
        found_caracteristicas_fisicas[key] = 'desconocido'  # Inicializar con 'desconocido'
        for token in doc:
            match = fuzzy_match(token.text.lower(), values)
            if match:
                found_caracteristicas_fisicas[key] = match
                break

    # Buscar género en el texto
    for token in doc:
        if fuzzy_match(token.text.lower(), generos_m_lower):
            found_genero = "hombre"
            break
        elif fuzzy_match(token.text.lower(), generos_f_lower):
            found_genero = "mujer"
            break

    # Buscar eventos en el texto
    for token in doc:
        match = fuzzy_match(token.text.lower(), eventos_lower)
        if match:
            found_eventos = match
            break  # Salir del bucle en cuanto se encuentre un evento

    # Crear el DataFrame con los resultados
    df_data = {
        'genero': found_genero,
        'piel': found_caracteristicas_fisicas.get('piel', 'desconocido'),
        'ojos': found_caracteristicas_fisicas.get('ojos', 'desconocido'),
        'contextura Fisica': found_caracteristicas_fisicas.get('contextura fisica', 'desconocido'),
        'estatura': found_caracteristicas_fisicas.get('estatura', 'desconocido'),
        'personalidad': ', '.join(found_personalidades) if found_personalidades else 'desconocido',
        'ocasion': found_eventos or 'desconocido'
    }
    
    df = pd.DataFrame([df_data])
    
    return expand_all_columns(df)





def categorize_predictions(y_pred):
    # Invertir los diccionarios de etiquetas para obtener categoría a partir del índice
    inverse_labels_ropas = {v: k for k, v in clothing.items()}
    
    # Variables para almacenar las categorías
    Ropas = []

    # Iterar sobre cada predicción
    for pred in y_pred.astype(int):
        ropa_idx = np.maximum(pred, 0)

        # Obtener la categoría de cada índice
        ropas = inverse_labels_ropas.get(ropa_idx, "Unknown")

    return ropas



def enviar_correo(nombre,  mensaje):
    # Usa variables de entorno para almacenar las credenciales de forma segura
    usuario = os.getenv('EMAIL_USER')  # Configura EMAIL_USER en tus variables de entorno
    contraseña = os.getenv('EMAIL_PASS')  # Configura EMAIL_PASS en tus variables de entorno
    
    # Configura el SMTP
    yag = yagmail.SMTP(usuario, contraseña)
    
    # Plantilla HTML simplificada
    mensaje_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        .notification-container {{
          width: 320px;
          font-family: Arial, sans-serif;
          background-color: #f0fdf4;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }}
        .success-heading {{
          font-size: 18px;
          font-weight: bold;
          color: #166534;
        }}
        .message-text {{
          margin-top: 10px;
          color: #15803d;
        }}
        .button-container {{
          margin-top: 20px;
        }}
        .button {{
          padding: 10px 15px;
          background-color: #d1fae5;
          border: none;
          border-radius: 5px;
          font-weight: bold;
          color: #065f46;
          cursor: pointer;
        }}
        .button:hover {{
          background-color: #a7f3d0;
        }}
      </style>
    </head>
    <body>
      <div class="notification-container">
        <p class="success-heading">{nombre}</p>
        <p class="message-text">{mensaje}</p>
        <div class="button-container">
          <button class="button" onclick="window.location.href='https://example.com'">Acción</button>
        </div>
      </div>
    </body>
    </html>
    """

    try:
        # Enviar el correo con el contenido HTML
        yag.send(to='mega09elne@gmail.com', subject='Datos Sobre Usuario', contents=mensaje_html)
        return "Correo enviado correctamente."
    except Exception as e:
        return f"Error al enviar el correo: {str(e)}"





def get_images_from_folder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        image_files = []
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_path.lower().endswith(image_extensions):
                image_files.append(file_path)
        return image_files
    else:
        return []
    
def descargar_imagenes_api(query, num_imagenes=15):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": query,
        "page": str(7),
        "country": "US",
        "sort_by": "RELEVANCE",
        "product_condition": "ALL",
        "is_prime": "false",
        "deals_and_discounts": "NONE"
    }

    headers = {
        "x-rapidapi-key": "f80d59416bmshba4d1c3787cc46ep101db5jsndb95bb993bc7",
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
 
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Verificar que la solicitud fue exitosa (código 200)
        return response.json()['data']['products']  # Devolver la respuesta en formato JSON
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los productos: {e}")
        return None
 

# Función para descargar imágenes de todos los div con clase específica
def descargar_imagenes_api1(query, div_class = 'XiG zI7 iyn Hsu', num_imagenes=15):
    # URL del sitio que deseas scrapear (puede variar)
    api_key = "46243061-e8a7599081ec88304b10a97bb"
    url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&pretty=true"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        # Realizar solicitud HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar que la solicitud fue exitosa (código 200)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página: {e}")
        return
    
    # Parse the JSON response
    data = response.json()

    # Crear carpeta para guardar las imágenes si no existe
    #if not os.path.exists(query):
    #    os.makedirs(query)

    # Contador para nombrar las imágenes
    img_counter =0
    img_urls = []  # Para evitar duplicados

    # Access the 'hits' list from the JSON data
    for hit in data["hits"]:
        # Access and print the 'largeImageURL'
        #print(hit["largeImageURL"])
        img_urls.append(hit["largeImageURL"])

        img_counter += 1
        if img_counter == num_imagenes:
          break

    if img_counter == 1:
        print("No se encontraron imágenes en los divs seleccionados.")
    else:
        print(f"Descarga completada. {img_counter - 1} imágenes descargadas.")
      
    return img_urls
   

def get_ropa_descriptions(prenda):
    # Descripciones de uso para cada prenda de ropa
    ropa_uses = {
        'camisa': 'Las camisas son ideales para un entorno formal, como reuniones de negocios o la oficina, y también pueden usarse casualmente.',
        'bermuda': 'Las bermudas son cómodas y perfectas para climas cálidos o salidas informales, ofreciendo un look relajado.',
        'camiseta': 'Las camisetas son prendas versátiles para el uso diario, perfectas para salidas informales, deportes o estar en casa.',
        'chaquetas': 'Las chaquetas son ideales para el clima frío o para añadir estilo a un atuendo. Pueden ser casuales o formales.',
        'falda': 'Las faldas son versátiles, adecuadas tanto para el trabajo como para eventos sociales dependiendo del estilo.',
        'manga_larga': 'Las prendas de manga larga son útiles para climas fríos y para combinar en capas. Son cómodas y prácticas.',
        'pantalon': 'Los pantalones son básicos en cualquier armario, adecuados para entornos formales o casuales según el diseño.',
        'sombrero': 'Los sombreros son ideales para protegerse del sol o para añadir un toque de estilo a cualquier atuendo.',
        'vestido': 'Los vestidos son prendas femeninas perfectas para eventos formales o salidas casuales dependiendo de su diseño.',
        'zapato': 'Los zapatos completan cualquier look, siendo versátiles para el trabajo, eventos formales, o actividades deportivas.'
    }

    # Obtener la descripción para la prenda o devolver un mensaje si no está disponible
    return ropa_uses.get(prenda, 'Descripción no disponible')




def split_column_and_expand(df, column_to_split):
    """
    Divide una columna de un DataFrame en múltiples filas y expande las otras columnas.

    Args:
        df: El DataFrame de entrada.
        column_to_split: El nombre de la columna a dividir.

    Returns:
        Un DataFrame con la columna dividida en nuevas filas.
    """
    # Asegurar que los valores de la columna sean cadenas de texto
    df[column_to_split] = df[column_to_split].astype(str)

    # Convertir todos los valores de la columna a minúsculas
    df[column_to_split] = df[column_to_split].str.lower()

    # Dividir la columna en listas basadas en comas
    df[column_to_split] = df[column_to_split].str.split(',')

    # Explode la columna dividida para crear nuevas filas
    df_expanded = df.explode(column_to_split)

    # Quitar espacios adicionales al principio y al final de los valores de las columnas
    df_expanded[column_to_split] = df_expanded[column_to_split].str.strip()

    # Filtrar filas con valores vacíos o nulos en la columna especificada
    df_expanded = df_expanded[df_expanded[column_to_split].notna() & (df_expanded[column_to_split] != '')]

    return df_expanded


def expand_all_columns(df):
    """
    Expande todas las columnas de un DataFrame que contengan valores separados por comas.

    Args:
        df: El DataFrame de entrada.

    Returns:
        Un nuevo DataFrame con todas las columnas expandidas.
    """
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, str) and ',' in x).any():
            df = split_column_and_expand(df, col)

    return df