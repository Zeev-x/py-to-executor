import re
import sys
import os
import shutil
import importlib.util
import platform

env_path = "Reyette_Roxylious_Atelier"
url_icon = "https://raw.githubusercontent.com/Zeev-x/reyette-dlr/refs/heads/main/logo/app_icon_square.ico"
os_system = platform.system().lower()
script_name = os.path.basename(sys.argv[0])

def get_main_file():
    while True:
        main_file = input("Masukkan nama file utama (main.py): ").strip()
        if main_file == "":
            print("Nama file utama tidak boleh kosong. Silakan coba lagi.")
        elif not main_file.endswith(".py"):
            print("Nama file utama harus berakhiran .py. Silakan coba lagi.")
        else:
            return main_file

# Mapping modul
PACKAGE_MAP = {
    # Networking / Serial
    "serial": "pyserial",
    "socketserver": None,   # stdlib
    "asyncio": None,        # stdlib
    "socket": None,         # stdlib
    "ssl": None,            # stdlib
    "urllib": None,         # stdlib
    "selectors": None,      # stdlib
    "ipaddress": None,      # stdlib
    "http": None,           # stdlib
    "mimetypes": None,      # stdlib

    # Web / Parsing
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "lxml": "lxml",
    "html5lib": "html5lib",
    "requests": "requests",
    "urllib3": "urllib3",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "tornado": "tornado",
    "starlette": "starlette",
    "werkzeug": "Werkzeug",
    "ngrok": "ngrok",
    "jinja2": "jinja2",
    "markupsafe": "markupsafe",
    "charset_normalizer": "charset-normalizer",
    "idna": "idna",
    "certifi": "certifi",

    # Data / Science
    "numpy": "numpy",
    "scipy": "scipy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "pillow",
    "dateutil": "python-dateutil",
    "ConfigParser": "configparser",
    "ujson": "ujson",
    "simplejson": "simplejson",
    "tabulate": "tabulate",
    "openpyxl": "openpyxl",
    "xlrd": "xlrd",
    "xlwt": "xlwt",
    "xlsxwriter": "XlsxWriter",
    "pytz": "pytz",
    "cycler": "cycler",
    "kiwisolver": "kiwisolver",
    "pyparsing": "pyparsing",
    "joblib": "joblib",
    "threadpoolctl": "threadpoolctl",

    # Database
    "mysql": "mysql-connector-python",
    "MySQLdb": "mysqlclient",
    "psycopg2": "psycopg2",
    "pymongo": "pymongo",
    "redis": "redis",
    "sqlalchemy": "sqlalchemy",
    "greenlet": "greenlet",
    "PyMySQL": "PyMySQL",
    "pymysql": "PyMySQL",
    "asyncpg": "asyncpg",

    # Crypto / Security
    "Crypto": "pycryptodome",
    "bcrypt": "bcrypt",
    "argon2": "argon2-cffi",
    "cryptography": "cryptography",
    "cffi": "cffi",
    "paramiko": "paramiko",

    # GUI / Desktop
    "tkinter": None,        # stdlib
    "PyQt5": "PyQt5",
    "PySide6": "PySide6",
    "kivy": "kivy",
    "pystray": "pystray",

    # Server / Framework
    "flask": "flask",
    "django": "django",
    "fastapi": "fastapi",
    "pyftpdlib": "pyftpdlib",
    "uvicorn": "uvicorn",
    "gunicorn": "gunicorn",
    "starlette": "starlette",
    "pydantic": "pydantic",
    "asgiref": "asgiref",

    # ML / AI
    "torch": "torch",
    "tensorflow": "tensorflow",
    "keras": "keras",
    "xgboost": "xgboost",
    "lightgbm": "lightgbm",
    "typing_extensions": "typing_extensions",

    # Misc Tools / Downloaders
    "yt_dlp": "yt-dlp",
    "dotenv": "python-dotenv",
    "pyyaml": "PyYAML",
    "jinja2": "jinja2",
    "colorama": "colorama",
    "tqdm": "tqdm",
    "loguru": "loguru",
    "pytest": "pytest",
    "click": "click",
    "typer": "typer",
    "rich": "rich",
    "pygments": "pygments",
    "requests_html": "requests-html",
    "beautifulsoup": "beautifulsoup4",
    "packaging": "packaging",
    "setuptools": "setuptools",
    "pkg_resources": "setuptools",
    "importlib_metadata": "importlib-metadata",
    "importlib_resources": "importlib-resources",
    "psutil": "psutil",
}

def is_stdlib(pkg: str) -> bool:
    """Cek apakah modul berasal dari stdlib, aman dari ValueError."""
    try:
        spec = importlib.util.find_spec(pkg)
        if spec and spec.origin and "site-packages" not in spec.origin:
            return True
    except (ImportError, ValueError):
        return False
    return False

def parse_imports(file_path, visited):
    if not os.path.exists(file_path) or file_path in visited:
        return set()
    visited.add(file_path)

    packages = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                m1 = re.match(r'^\s*import\s+([a-zA-Z0-9_\.]+)', line)
                m2 = re.match(r'^\s*from\s+([a-zA-Z0-9_\.]+)', line)
                if m1:
                    packages.add(m1.group(1).split('.')[0])
                elif m2:
                    packages.add(m2.group(1).split('.')[0])
    except Exception as e:
        print(f"Gagal membaca {file_path}: {e}")
        return set()

    external = set()
    for pkg in packages:
        if is_stdlib(pkg):
            continue
        local_file = pkg + ".py"
        local_dir = pkg
        if os.path.exists(local_file):
            external |= parse_imports(local_file, visited)
            continue
        elif os.path.isdir(local_dir) and os.path.exists(os.path.join(local_dir, "__init__.py")):
            external |= parse_imports(os.path.join(local_dir, "__init__.py"), visited)
            continue
        mapped = PACKAGE_MAP.get(pkg, pkg)
        if mapped:
            external.add(mapped)

    return external

def get_all_py_files(root_dir="."):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                py_files.append(os.path.join(dirpath, fname))
    return py_files

def get_package_pip_for_project(root_dir="."):
    visited = set()
    external_packages = set()
    py_files = get_all_py_files(root_dir)
    for file_path in py_files:
        external_packages |= parse_imports(file_path, visited)
    return " ".join(sorted(external_packages)) if external_packages else None

def get_package_pip(main_file):
    visited = set()
    external_packages = parse_imports(main_file, visited)
    return " ".join(sorted(external_packages)) if external_packages else None

def get_requirements_or_detect(root_dir="."):
    req_file = os.path.join(root_dir, "requirements.txt")
    if os.path.exists(req_file):
        print("requirements.txt ditemukan, menggunakan daftar paket dari file...")
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                packages = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # ambil nama paket tanpa versi
                        pkg = line.split("==")[0].split(">=")[0].split("<=")[0]
                        packages.append(pkg)
                return " ".join(sorted(set(packages)))
        except Exception as e:
            print(f"Gagal membaca requirements.txt: {e}")
            return get_package_pip_for_project(root_dir)
    else:
        print("requirements.txt tidak ada, menggunakan deteksi otomatis...")
        return get_package_pip_for_project(root_dir)

def get_local_modules(root_dir="."):
    local_modules = set()
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                local_modules.add(os.path.splitext(fname)[0])
        for dname in dirnames:
            init_file = os.path.join(dirpath, dname, "__init__.py")
            if os.path.exists(init_file):
                local_modules.add(dname)
    return local_modules

HIDDEN_IMPORT_MAP = {
    # Networking / Serial
    "serial": [],
    "socketserver": [],
    "asyncio": [],
    "socket": [],
    "ssl": [],

    # Web / Parsing
    "bs4": ["soupsieve"],
    "yaml": [],
    "lxml": [],
    "html5lib": [],
    "requests": ["chardet", "idna", "certifi", "urllib3"],
    "urllib3": [],
    "httpx": ["asyncio"],
    "aiohttp": ["asyncio"],
    "tornado": ["asyncio"],
    "starlette": ["anyio"],
    "werkzeug": [],
    "ngrok": ["asyncio"],
    "jinja2": ["markupsafe"],
    "markupsafe": [],
    "charset_normalizer": [],
    "idna": [],
    "certifi": [],

    # Data / Science
    "numpy": [],
    "scipy": [],
    "pandas": ["numpy", "python-dateutil", "pytz"],
    "matplotlib": ["cycler", "kiwisolver", "pyparsing"],
    "seaborn": ["matplotlib"],
    "sklearn": ["joblib", "threadpoolctl"],
    "cv2": [],
    "PIL": [],
    "dateutil": [],
    "ConfigParser": [],
    "ujson": [],
    "simplejson": [],
    "tabulate": [],
    "openpyxl": [],
    "xlrd": [],
    "xlwt": [],
    "xlsxwriter": [],
    "pytz": [],
    "cycler": [],
    "kiwisolver": [],
    "pyparsing": [],
    "joblib": [],
    "threadpoolctl": [],

    # Database
    "mysql": [],
    "MySQLdb": [],
    "psycopg2": [],
    "pymongo": [],
    "redis": [],
    "sqlalchemy": ["greenlet"],
    "greenlet": [],
    "PyMySQL": [],
    "pymysql": [],
    "asyncpg": [],

    # Crypto / Security
    "Crypto": ["Cryptodome"],
    "bcrypt": [],
    "argon2": [],
    "cryptography": ["cffi"],
    "cffi": [],
    "paramiko": [],

    # GUI / Desktop
    "tkinter": [],
    "PyQt5": ["sip"],
    "sip": [],
    "PySide6": [],
    "kivy": [],
    "pystray": [],

    # Server / Framework
    "flask": ["jinja2", "werkzeug", "click"],
    "django": ["asgiref"],
    "fastapi": ["asyncio", "pydantic", "starlette"],
    "pyftpdlib": [],
    "uvicorn": [],
    "gunicorn": [],
    "pydantic": [],
    "asgiref": [],

    # ML / AI
    "torch": ["typing_extensions"],
    "typing_extensions": [],
    "tensorflow": ["absl", "astunparse", "gast"],
    "absl": [],
    "astunparse": [],
    "gast": [],
    "keras": ["tensorflow"],
    "xgboost": [],
    "lightgbm": [],

    # Misc Tools / Downloaders
    "yt_dlp": ["asyncio"],
    "dotenv": [],
    "jinja2": ["markupsafe"],
    "colorama": [],
    "tqdm": [],
    "loguru": [],
    "pytest": ["pluggy", "py", "attrs", "iniconfig"],
    "pluggy": [],
    "py": [],
    "attrs": [],
    "iniconfig": [],
    "click": [],
    "typer": [],
    "rich": ["pygments"],
    "pygments": [],
    "requests_html": ["requests", "pyppeteer"],
    "pyppeteer": [],
    "packaging": [],
    "setuptools": [],
    "pkg_resources": [],
    "importlib_metadata": [],
    "importlib_resources": [],
    "psutil": [],
}

DYNAMIC_IMPORT_REGEX = re.compile(r'__import__\(\s*["\']([a-zA-Z0-9_\.]+)["\']\s*\)|importlib\.import_module\(\s*["\']([a-zA-Z0-9_\.]+)["\']\s*\)')

def parse_hidden_imports(file_path, visited, local_modules):
    if not os.path.exists(file_path) or file_path in visited:
        return set()
    visited.add(file_path)

    imported_modules = set()
    dynamic_modules = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                m1 = re.match(r'^\s*import\s+([a-zA-Z0-9_\.]+)', line)
                m2 = re.match(r'^\s*from\s+([a-zA-Z0-9_\.]+)', line)
                if m1:
                    module = m1.group(1).split('.')[0]
                    imported_modules.add(module)
                elif m2:
                    module = m2.group(1).split('.')[0]
                    imported_modules.add(module)
                for match in DYNAMIC_IMPORT_REGEX.finditer(line):
                    dynamic_module = match.group(1) or match.group(2)
                    if dynamic_module:
                        dynamic_modules.add(dynamic_module.split('.')[0])
                        imported_modules.add(dynamic_module.split('.')[0])
    except Exception as e:
        print(f"Gagal membaca {file_path}: {e}")
        return set()

    hidden_imports = set()
    for module in imported_modules:
        if module in local_modules:
            continue
        if module in HIDDEN_IMPORT_MAP:
            hidden_imports.update(HIDDEN_IMPORT_MAP[module])
        if module in dynamic_modules:
            hidden_imports.add(module)

    return hidden_imports


def get_hidden_imports_for_project(root_dir="."):
    local_modules = get_local_modules(root_dir)
    visited = set()
    hidden_imports = set()
    py_files = get_all_py_files(root_dir)
    for file_path in py_files:
        hidden_imports |= parse_hidden_imports(file_path, visited, local_modules)
    return sorted(hidden_imports)


def get_name_of_app():
    while True:
        name_of_app = input("Nama aplikasi: ")
        if name_of_app.strip() == "":
            print("Nama aplikasi tidak boleh kosong. Silakan coba lagi.")
        else:
            return name_of_app

def get_windowed_option():
    while True:
        windowed_option = input("Apakah aplikasi ini akan dijalankan dalam mode windowed? (y/n): ").strip().lower()
        if windowed_option == 'y':
            return "--windowed"
        elif windowed_option == 'n':
            return ""
        else:
            print("Input tidak valid. Silakan masukkan 'y' untuk ya atau 'n' untuk tidak.")

def get_all_data(xfile, root_dir="."):
    EXCLUDE_DIRS = {env_path}
    EXCLUDE_FILES = {script_name, xfile}

    additional_data = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if any(ex in dirpath.split(os.sep) for ex in EXCLUDE_DIRS):
            continue

        for fname in filenames:
            if fname in EXCLUDE_FILES:
                continue
            file_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(file_path, root_dir)
            if platform.system().lower() == "windows":
                additional_data.append(f"{file_path};{rel_path}")
            else:
                additional_data.append(f"{file_path}:{rel_path}")
    return additional_data

def get_icon(url):
    icon_path = os.path.join("icon", "icon.ico")
    if os.path.exists(icon_path):
        print("Icon exists")

    if os_system == "windows":
        cmd = [
            f"mkdir icon && curl -o {icon_path} {url}",
            "cls"
        ]
    else:
        cmd = [
            f"mkdir icon && curl -o {icon_path} {url}",
            "clear"
        ]

    try:
        for x in cmd:
            os.system(x)
    except Exception as e:
        print(e)

def run_cmd(main_file, name_of_app, windowed_option, additional_data, package_pip=None):
    def get_pip_final(package_pip):
        if package_pip:
            return f"{package_pip} pyinstaller"
        else:
            return "pyinstaller"

    hidden_imports = get_hidden_imports_for_project(".")
    hidden_import_args = " ".join([f"--hidden-import={imp}" for imp in hidden_imports]) if hidden_imports else ""

    if hidden_imports:
        print("Hidden import yang terdeteksi:")
        for imp in hidden_imports:
            print(f" - {imp}")
    else:
        print("Tidak ada hidden import yang terdeteksi.")

    if os_system == "windows":
        cmd = [
            "@echo off",
            f"py -3.12 -m venv {env_path}",
            f"{env_path}\\Scripts\\python.exe -m pip install --upgrade {get_pip_final(package_pip)}",
           f'{env_path}\\Scripts\\pyinstaller.exe {main_file} --onefile --icon=icon/icon.ico --name="{name_of_app}" {windowed_option} {hidden_import_args} {" ".join([f"--add-data \"{data}\"" for data in additional_data])}',
        ]
    else:
        cmd = [
            "set -e",
            f"python -m venv {env_path}",
            f"{env_path}/bin/python -m pip install --upgrade {get_pip_final(package_pip)}",
            f'{env_path}/bin/pyinstaller {main_file} --onefile --icon=icon/icon.ico --name="{name_of_app}" {windowed_option} {hidden_import_args} {" ".join([f"--add-data={data.replace(';',':')}" for data in additional_data])}',
        ]

    try:
        for x in cmd:
            print(f"Running command: {x}")
            os.system(x)
    except Exception as e:
        print(e)

def after_build_windows(app_name):
    src = os.path.join("dist", f"{app_name}.exe")
    dst = os.path.join(os.getcwd(), f"{app_name}.exe")

    dir_temp = [f"{env_path}", "build", "dist"]
    file_temp = [f"{app_name}.spec"]

    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")

    for x in dir_temp:
        if os.path.exists(x):
            print(f"Deleting {x}")
            shutil.rmtree(x)

    for y in file_temp:
        if os.path.exists(y):
            print(f"Deleting {y}")
            os.remove(y)

def after_build_linux(app_name):
    src = os.path.join("dist", app_name)
    dst = os.path.join(os.getcwd(), app_name)

    dir_temp = [env_path, "build", "dist"]
    file_temp = [f"{app_name}.spec"]

    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")

    for x in dir_temp:
        if os.path.exists(x):
            print(f"Deleting {x}")
            shutil.rmtree(x)

    for y in file_temp:
        if os.path.exists(y):
            print(f"Deleting {y}")
            os.remove(y)

def worker():
    get_icon(url_icon)
    main_file = get_main_file()
    package_pip_project = get_requirements_or_detect(".")
    name_of_app = get_name_of_app()
    windowed_option = get_windowed_option()
    additional_data = get_all_data(main_file, ".")

    print("Anda akan build aplikasi dengan pengaturan berikut:")
    print(f"File utama: {main_file}")
    print(f"Package pip: {package_pip_project if package_pip_project else 'Tidak ada'}")
    print(f"Nama aplikasi: {name_of_app}")
    print(f"Mode windowed: {'Ya' if windowed_option else 'Tidak'}")
    if additional_data:
        print("Data tambahan:")
        for data in additional_data:
            print(f" - {data}")

    while True:
        confirm = input("Apakah Anda ingin melanjutkan? (y/n): ").strip().lower()
        if confirm == 'y':
            run_cmd(main_file, name_of_app, windowed_option, additional_data, package_pip_project)
            if os_system == "windows":
                after_build_windows(name_of_app)
            else:
                after_build_linux(name_of_app)
            break
        elif confirm == 'n':
            print("Proses build dibatalkan. Silakan jalankan kembali script ini jika ingin mencoba lagi.")
            break
        else:
            print("Input tidak valid. Silakan masukkan 'y' untuk ya atau 'n' untuk tidak.")

if __name__ == "__main__":
    try:
        worker()
    except KeyboardInterrupt:
        print("Closing by user")
    finally:
        if os_system == "windows":
            os.system("pause")
        else:
            pass
