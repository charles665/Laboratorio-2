from pathlib import Path
import json
import pandas as pd


def _resolve_input_files(input_path, valid_extensions):
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró la ruta: {path}")

    if path.is_file():
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"El archivo {path} no tiene una extensión soportada: {sorted(valid_extensions)}"
            )
        return [path]

    if path.is_dir():
        files = [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in valid_extensions]
        files.sort()
        if not files:
            raise FileNotFoundError(
                f"No se encontraron archivos con extensión {sorted(valid_extensions)} en {path}"
            )
        return files

    raise FileNotFoundError(f"No se pudo resolver la ruta: {path}")

def extract_from_csv(file_path):
    """Lee todos los archivos CSV encontrados de forma recursiva."""
    files = _resolve_input_files(file_path, {".csv"})
    dataframes = {}

    for file in files:
        dataframes[file.name] = pd.read_csv(file, encoding="utf-8-sig")

    return dataframes



def extract_from_json(file_path):
    """Lee las colecciones de referencia y las devuelve como DataFrames."""
    files = _resolve_input_files(file_path, {".json"})
    dataframes = {}

    for file in files:
        with file.open(encoding="utf-8") as source:
            collections = json.load(source)

        if not isinstance(collections, dict):
            raise ValueError(f"El JSON {file} debe contener un objeto de colecciones")

        for name, records in collections.items():
            if not isinstance(records, list):
                raise ValueError(f"La colección {name} de {file} debe ser una lista")
            dataframes[name] = pd.DataFrame(records)

    return dataframes
