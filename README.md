# GTM Audit Analyzer

Herramienta de auditoría para Google Tag Manager que combina crawleo estático de sitios web con captura de eventos en vivo mediante un snippet de consola.

## Estructura

```
gtm-audit/
├── main.py                        # Punto de entrada
├── check_dependencies.py          # Verificación e instalación de dependencias
├── requirements.txt
├── .gitignore
├── analyzer/
│   ├── config.py                  # Parámetros globales del crawler
│   ├── crawler.py                 # Crawleo y análisis estático
│   ├── js_analyzer.py             # Análisis del JSON exportado por el snippet
│   └── reporter.py                # Generación del reporte Excel
└── snippet/
    └── gtm_audit_snippet.js       # Snippet para pegar en la consola del navegador
```

## Instalación

```bash
git clone https://github.com/MVFran/WebCrawler.git
cd WebCrawler
python check_dependencies.py
```

O con pip directamente:

```bash
pip install -r requirements.txt
```

## Uso

### 1. Captura en vivo (opcional)

Abre el sitio a auditar en el navegador, pega el contenido de `snippet/gtm_audit_snippet.js` en la consola y navega por el sitio. Cuando termines, haz clic en **Exportar JSON** en el badge que aparece en pantalla.

### 2. Ejecutar el analizador

```bash
python main.py
```

El programa solicitará:

- **URL del sitio** — debe incluir `http://` o `https://`
- **Ruta del JSON** — el archivo exportado por el snippet; presiona Enter para omitirlo y ejecutar solo el crawler estático

### 3. Reporte

Se genera un archivo `gtm_audit_report_YYYYMMDD_HHMM.xlsx` con las siguientes hojas:

| Hoja | Contenido |
|---|---|
| Resumen | Métricas globales del crawleo y del snippet |
| Páginas | Estado de tracking por URL |
| Formularios (estático) | Campos detectados en el HTML |
| CTAs | Botones y enlaces identificados como llamadas a la acción |
| DataLayer (vivo) | Eventos capturados por el snippet *(requiere JSON)* |
| Formularios (vivo) | Envíos de formulario capturados *(requiere JSON)* |

## Configuración

Los parámetros del crawler se ajustan en `analyzer/config.py`:

```python
MAX_PAGES = 200    # Límite de páginas a crawlear
DELAY     = 1.0    # Segundos entre requests
HEADERS   = {'User-Agent': 'GTMAudit-Bot/1.0'}
```
