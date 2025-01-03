# bgg-profiler

**bgg-profiler** es una herramienta diseñada para interactuar con la API de BoardGameGeek (BGG) y generar perfiles personalizados basados en las colecciones de juegos de mesa de los usuarios. Permite extraer información detallada de los juegos, procesarla y generar un HTML atractivo que muestra los datos de manera organizada.

## Requisitos y Dependencias

Para utilizar este proyecto, necesitas:

- **Sistema Operativo:** Compatible con cualquier sistema operativo que soporte Python.
- **Python 3.7 o superior.**
- **Librerías necesarias:**
  - `requests`
  - `beautifulsoup4`
  - `configparser`

Puedes instalar todas las dependencias ejecutando:
```bash
pip install -r requirements.txt
```

## Configuración Inicial

1. **Configurar `properties.cfg`:** Este archivo contiene los parámetros básicos del usuario y del estado de la colección. Un ejemplo de configuración es:
   ```ini
   [user]
   username = tu_nombre_de_usuario

   [settings]
   state = own  # Opciones: own, wishlist
   templates = default
   ```

2. **Crear Plantillas:** Las plantillas HTML, CSS y JavaScript se deben colocar en la carpeta `templates` con los siguientes nombres:
   - `default_html.template`
   - `default_css.template`
   - `default_js.template`
   - `default_jquery.template`

## Primera Ejecución

Sigue los pasos a continuación para ejecutar el programa por primera vez:

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/JuezFenix/bgg-profiler.git
   ```

2. **Navega al directorio del proyecto:**
   ```bash
   cd bgg-profiler
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta el programa:**
   ```bash
   python bgg-profiler.py
   ```

El programa:
- Valida la configuración y las plantillas.
- Obtiene los datos de la colección de BGG mediante su API.
- Guarda los datos en formato XML en la carpeta correspondiente.
- Genera un archivo HTML con la información procesada.

## Ejecuciones Sucesivas

Una vez configurado, simplemente ejecuta:
```bash
python bgg-profiler.py
```

Esto actualizará la información de la colección y generará un nuevo HTML, utilizando los datos más recientes.

## Notas Adicionales

- **Estructura de carpetas generadas:**
  - XMLs de la colección se guardan en `estado_usuario_games_list.xml`.
  - XMLs individuales de los juegos se almacenan en carpetas con formato `estado_usuario_games/`.

- **Advertencias:**
  - El programa generará errores si las plantillas requeridas no existen.
  - Si la API de BGG responde con `503` o `429`, se implementan tiempos de espera automáticos para manejar las limitaciones de la API.

Para más información o para reportar problemas, visita el repositorio en [GitHub](https://github.com/JuezFenix/bgg-profiler).
