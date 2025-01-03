import os
import configparser
import requests
import time
import re
from bs4 import BeautifulSoup

# Leer configuración desde properties.cfg
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        "username": config.get("user", "username"),
        "state": config.get("settings", "state"),
        "template": config.get("settings", "templates", fallback="default")
    }

# Leer template desde la carpeta template
def load_template(template_name, resource_type):
    """
    Carga un archivo de plantilla desde la carpeta templates.
    """
    file_path = f"templates/{template_name}_{resource_type}.template"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró la plantilla {file_path}.")
        return ""

# Validar la existencia de todos los ficheros de plantilla
def validate_templates(template_name):
    """
    Valida que existan todos los recursos necesarios para una plantilla.
    """
    resources = ["html", "css", "js", "jquery"]
    for resource in resources:
        file_path = f"templates/{template_name}_{resource}.template"
        if not os.path.exists(file_path):
            print(f"Advertencia: Falta el archivo {file_path}.")

# Obtener juegos desde BGG API
def fetch_bgg_games(username, state):
    url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&own={1 if state == 'own' else 0}&wishlist={1 if state == 'wishlist' else 0}&excludesubtype=boardgameexpansion&brief=1"

    while True:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Devuelve XML directamente
        elif response.status_code == 503:
            print("La solicitud ha sido aceptada y será procesada. Esperando 10 segundos...")
            time.sleep(10)
        else:
            response.raise_for_status()

# Guardar XML de la colección
def save_collection_xml(xml_data, state, username):
    collection_path = f"{state}_{username}_games_list.xml"
    # Eliminar el archivo si ya existe
    if os.path.exists(collection_path):
        os.remove(collection_path)
    with open(collection_path, "w", encoding='utf-8') as xml_file:
        xml_file.write(xml_data)
    print(f"XML de la colección guardado en: {collection_path}")
    return collection_path

# Parsear XML para obtener información de los juegos
def parse_bgg_games(xml_data):
    soup = BeautifulSoup(xml_data, "xml")
    games = []
    for item in soup.find_all("item"):
        game = {
            "id": item["objectid"],
            "name": item.find("name").text
        }
        games.append(game)
    return games

# Crear carpeta para guardar los XML de los juegos
def create_game_folder(state, username):
    folder_name = f"{state}_{username}_games"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# Guardar XML individual del juego
def fetch_game_xml(game_id):
    url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_id}&stats=1"
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Devuelve XML directamente
        elif response.status_code == 429:
            print("Demasiadas solicitudes. Esperando 30 segundos...")
            time.sleep(30)
        else:
            print(f"Error al obtener datos para el juego ID {game_id}: {response.status_code}")
            return None

# Extraer información ideal de edad mínima
def get_ideal_age(game_xml):
    soup = BeautifulSoup(game_xml, "xml")
    poll = soup.find("poll", {"name": "suggested_playerage"})
    if not poll:
        return "Desconocida"

    best_count = 0
    ideal_age = "Desconocida"
    for result in poll.find_all("result"):
        numvotes = int(result["numvotes"])
        if numvotes > best_count:
            best_count = numvotes
            ideal_age = result["value"]
    return ideal_age

# Obtener el número ideal de jugadores
def get_ideal_players(game_xml):
    """
    Extrae el número recomendado de jugadores desde poll-summary.
    """
    soup = BeautifulSoup(game_xml, "xml")
    poll_summary = soup.find("poll-summary", {"name": "suggested_numplayers"})
    if not poll_summary:
        return "Desconocido"

    recommended = poll_summary.find("result", {"name": "recommmendedwith"})
    if not recommended:
        return "Desconocido"

    value = recommended["value"]
    numbers = re.findall(r'\d+', value)
    return "–".join(numbers) if numbers else "Desconocido"

# Generamos cada elemento a introducir en el html
def generate_data(game_xml, collection_name, game_id, template_name, cards_html):
    """
    Extrae información de un juego, genera filas o elementos según la plantilla y los añade al HTML.
    :param game_xml: Contenido XML del juego.
    :param collection_name: Diccionario con nombres de juegos.
    :param game_id: ID del juego.
    :param template_name: Nombre base de la plantilla a usar.
    :param cards_html: Acumulador para las filas o elementos HTML generados.
    """
    game_name = collection_name.get(game_id, "Desconocido")
    game_url = f"https://boardgamegeek.com/boardgame/{game_id}"

    soup = BeautifulSoup(game_xml, "xml")
    item = soup.find("item")
    if not item:
        print(f"Error: No se encontró el elemento <item> para el juego {game_name}.")
        return

    # Extraer información del juego
    thumbnail = item.find("image").text if item.find("image") else "https://via.placeholder.com/300x150"
    min_players = item.find("minplayers")["value"]
    max_players = item.find("maxplayers")["value"]
    playing_time = item.find("playingtime")["value"] if item.find("playingtime") else "Desconocida"
    weight = round(float(item.find("averageweight")["value"]), 1) if item.find("averageweight") else "Desconocido"
    min_age = get_ideal_age(game_xml)
    year_published = item.find("yearpublished")["value"] if item.find("yearpublished") else "Desconocido"
    ideal_players = get_ideal_players(game_xml)

    # Generar el HTML para el juego usando la plantilla de fila
    row_template = load_template(template_name, "row")
    row_html = row_template.format(
        name=game_name,
        url=game_url,
        thumbnail=thumbnail,
        min_players=min_players,
        max_players=max_players,
        ideal_players=ideal_players,
        playing_time=playing_time,
        weight=weight,
        min_age=min_age,
        year_published=year_published
    )
    cards_html.append(row_html)

# Generar HTML final
def generate_html(username, cards_html, template_name="default"):
    """
    Genera el HTML completo usando plantillas.
    :param username: Nombre del usuario.
    :param cards_html: Lista de filas o elementos HTML generados.
    :param template_name: Nombre base de la plantilla a usar.
    """
    html_template = load_template(template_name, "html")
    css_template = load_template(template_name, "css")
    js_template = load_template(template_name, "js")
    jquery_template = load_template(template_name, "jquery")

    # Insertar CSS, JS, jQuery y filas en el HTML principal
    html_content = html_template.replace("{{CSS}}", f"<style>{css_template}</style>")
    html_content = html_content.replace("{{JQUERY}}", f"<script>{jquery_template}</script>")
    html_content = html_content.replace("{{JS}}", f"<script>{js_template}</script>")
    html_content = html_content.replace("{{ROWS}}", "".join(cards_html))  # Unir las filas generadas

    # Guardar el HTML final
    html_file_path = f"{username}_games_list.html"
    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

        html_file.write("""
            </div>
            <footer>
                <p>Generado por <a href="https://github.com/JuezFenix/bgg-profiler" target="_blank">BGG-Profiler</a>.</p>
            </footer>
        </body>
        </html>
        """)

def main():
    # Cargar datos de properties
    config = load_config("properties.cfg")
    username = config["username"]
    state = config["state"]
    template_name = config["template"]
    # Validamos el template
    validate_templates(template_name)

    # Guardar y cargar XML de la colección
    xml_data = fetch_bgg_games(username, state)
    collection_path = save_collection_xml(xml_data, state, username)
    collection_games = {game["id"]: game["name"] for game in parse_bgg_games(xml_data)}

    folder_name = create_game_folder(state, username)
    cards_html = []  # Lista para almacenar las filas del HTML

    for game_id, game_name in collection_games.items():
        xml_file_path = os.path.join(folder_name, f"{game_id}.xml")

        print(f"Procesando juego ID: {game_id}, Nombre: {game_name}")

        if not os.path.exists(xml_file_path):
            print(f"No existe XML almacenado para el juego. Descargando...")
            game_xml = fetch_game_xml(game_id)
            if game_xml:
                with open(xml_file_path, "w", encoding='utf-8') as xml_file:
                    xml_file.write(game_xml)
            time.sleep(1)
        else:
            print(f"Usando XML almacenado para el juego.")
            with open(xml_file_path, "r", encoding='utf-8') as xml_file:
                game_xml = xml_file.read()

        # Generar los datos para el HTML
        generate_data(game_xml, collection_games, game_id, template_name, cards_html)

    # Generar el HTML final
    generate_html(username, cards_html, template_name)

if __name__ == "__main__":
    main()
