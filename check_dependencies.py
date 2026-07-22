import importlib
import subprocess
import sys

REQUIRED = {
    'requests':     'requests',
    'bs4':          'beautifulsoup4',
    'pandas':       'pandas',
    'openpyxl':     'openpyxl',
}

def check_and_install():
    missing = []
    for module, package in REQUIRED.items():
        try:
            importlib.import_module(module)
            print(f"{package}")
        except ImportError:
            print(f"{package} — no encontrado")
            missing.append(package)

    if missing:
        print(f"\n  Instalando {len(missing)} paquete(s) faltante(s)...\n")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
        print("\nInstalación completada\n")
    else:
        print("\nTodas las dependencias están instaladas\n")

if __name__ == '__main__':
    print("\nVerificando dependencias...\n")
    check_and_install()
