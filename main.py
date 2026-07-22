import os
import sys
from analyzer.crawler import crawl_site
from analyzer.js_analyzer import analyze_js_log
from analyzer.reporter import export_report


def prompt_site_url():
    while True:
        url = input("  URL del sitio a analizar: ").strip()
        if url.startswith('http://') or url.startswith('https://'):
            return url
        print("La URL debe comenzar con http:// o https://\n")


def prompt_json_file():
    path = input("Ruta del JSON exportado por el snippet (Enter para omitir): ").strip()
    if not path:
        return None
    if not os.path.isfile(path):
        print(f"Archivo no encontrado: {path} — se usará solo el crawler estático\n")
        return None
    return path


def main():
    print(f"\n{'═'*55}")
    print("   GTM Audit Analyzer")
    print(f"{'═'*55}\n")

    site_url  = prompt_site_url()
    json_file = prompt_json_file()

    print()

    crawl_data, all_forms = crawl_site(site_url)

    js_data = analyze_js_log(json_file)
    if js_data:
        print("Resumen del snippet JS:")
        for k, v in js_data['by_type'].items():
            print(f"    {k}: {v}")
        print()

    print("Generando reporte Excel...")
    export_report(crawl_data, all_forms, js_data)


if __name__ == '__main__':
    main()
