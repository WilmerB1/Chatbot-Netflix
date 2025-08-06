"""
Imagina que esta API es una biblioteca de películas.
la función load_movies() es como un bibliotecario que carga el catálogo de libros (películas) cuando se abre la biblioteca.
la función get_movies() muestra todo el catálogo cuando alguien lo pide.
la función get_movie(id) es como si alguien preguntará por un libro en específico por su código de identificación.
La función chatbot (query) es un asistente que busca libros según palabras clave y sinonimo.
La función get_movies_by_category(category) ayuda a encontrar películas según su genero (acción, comedia, etc.).
"""

# Importamos las herramientas necesarias para para construir nuestra API.
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse para página web, JSONResponse para respuestas en formato JSON.
import pandas as pd # Pandas nos ayuda a manejar datos como si fuera un Excel.
import nltk # NLTK es una librería para procesar texto y analizar palabras.
from nltk.tokenize import word_tokenize # se usa para dividir un texto en palabras individules.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinonimo de palabras. 

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador.
nltk.data.path.append ('C:/Users/elkin/AppData/Roaming/nltk_data/tokenizers')

# Descargamos las herramientas necesarias de NLTK para el análisis de palabras.

nltk.download ('punkt') # paquete para dividir frases en palabras
nltk.download ('wordnet') # Paquete para encontrar sinónimos de palabras en inglés

# Función para catgar las películas desde un archivo csv

def load_movies():
    # Leemos el archivo que contiene información de películas y selecciones las columnas importantes
    df = pd.read_csv ('Dataset/netflix_titles.csv')[['show_id', 'title', 'release_year', 'listed_in', 'rating', 'description']]

    # Renombramos las columnas para que sean más fáciles de entender
    df.columns = ['id', 'title', 'year', 'category', 'rating', 'overview']

    # Llenamos los espacios vacios con texto vacio y convertimos los datos en una lista de diccionarios
    return df.fillna('').to_dict(orient='records')

# Cargamos las películas al iniciar la API para no leer el archivo cada vez que alguién pregunte por ellas. 
movies_list = load_movies()

# Función para encontrar sinónimos de una palabra 

def get_synonyms(word):
    # usamos WordNet para obtener distintas palabras que significan lo mismo.
    return{lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicación FastAPI, que será el motor de nuestra API
# Esto inicializa la API con un nombre y versión 
app = FastAPI(title="Mi aplicación de películas", version="1.0.0")

# Ruta de inicio: cuando alguién entra a la API sin especificar nada, verá un mensaje de bienvenida.

@app.get('/', tags=['Home'])
def home():
# Cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida
 return HTMLResponse('<h1>Bienvenido a la API de películas</h1>')

# Obteniendo la lista de películas
# Creamos una ruta para obtener todas las películas

# Ruta para obtener todas las películas disponibles

@app.get('/movies', tags=['Movies'])
def get_movies():
    # Si hay películas, las enviamos, si no, mostramos un error
    return movies_list or HTTPException(status_code=500, detail="No hay datos de películas disponibles")

 
 # Ruta para obtener una película específica según su ID
@app.get('/movies/{id}', tags=['Movies'])
def get_movies(id: str):
    # Buscamos en la lista de películas la que tenga el mismo ID
    return next ((m for m in movies_list if m['id']  == id), {'detalle': "película encontrada"})

# Ruta del Chatbot que responde con películas según palabras clave de la categoría

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave, para entender mejor la intención del usuario
    query_words = word_tokenize(query.lower())

    # Buscamos sinónimos de las palabras claves para ampliar la busqueda 
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)

    # Filtramos la lista de películas buscando coincidencias en la categoría
    results = [m for m in movies_list if any (s in m['category'].lower() for s in synonyms)]

   # Si encontramos películas, enviamos la lista; si no, mostramos un mensaje de que no se encontraron coincidencias.

    return JSONResponse (content={
        "respuesta": "Aquí tienes algunas películas relaconadas." if results else "No encontre Películas en esa categoría",
        "películas": results
        })

# Ruta para buscar películas por categoría específica 

@app.get ('/movies/by_category/', tags=['Movies'])
def get_movies_by_category(category: str):
    # Filtramos la lista de películas según la categoría ingresada
    return [m for m in movies_list if category.lower() in m['category'].lower()]


