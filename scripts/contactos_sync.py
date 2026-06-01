"""
contactos_sync.py
Sincroniza contactos entre Holded y un CSV externo (CRM, Excel, etc.)

Modos:
  - export: exporta todos los contactos de Holded a CSV
  - import: importa contactos desde un CSV a Holded (crea o actualiza)
  - check:  comprueba qué contactos del CSV no existen en Holded

Uso:
    python contactos_sync.py export --output contactos_holded.csv
    python contactos_sync.py import --input nuevos_clientes.csv
    python contactos_sync.py check --input lista_clientes.csv

Requiere: pip install requests
"""

import requests
import csv
import time
import argparse
import json

API_KEY = "TU_API_KEY_AQUI"
BASE_URL = "https://api.holded.com/api/contacts/v1/contacts"
HEADERS = {"key": API_KEY, "Content-Type": "application/json"}


def get_todos_contactos() -> list:
    """Obtiene todos los contactos de Holded paginando."""
    contactos = []
    page = 1
    print("Descargando contactos de Holded...")

    while True:
        r = requests.get(BASE_URL, headers=HEADERS, params={"page": page}, timeout=30)
        if r.status_code == 429:
            time.sleep(60)
            continue
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        if isinstance(data, list):
            contactos.extend(data)
        else:
            items = data.get("data", [])
            if not items:
                break
            contactos.extend(items)
        print(f"  Página {page}: {len(data) if isinstance(data, list) else len(items)} contactos")
        page += 1
        time.sleep(0.3)

    print(f"Total: {len(contactos)} contactos")
    return contactos


def exportar_contactos(output_file: str):
    """Exporta todos los contactos de Holded a un CSV."""
    contactos = get_todos_contactos()
    if not contactos:
        print("No hay contactos para exportar.")
        return

    campos = ["id", "name", "tradeName", "code", "vatnumber", "email",
              "phone", "address", "city", "postalCode", "countryCode",
              "iban", "type", "tags"]

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for c in contactos:
            # Normalizar tipo (puede ser lista)
            tipo = c.get("type", [])
            c["type"] = ",".join(tipo) if isinstance(tipo, list) else tipo
            tags = c.get("tags", [])
            c["tags"] = ",".join(tags) if isinstance(tags, list) else tags
            writer.writerow({k: c.get(k, "") for k in campos})

    print(f"Exportado a: {output_file}")


def crear_contacto(datos: dict) -> dict:
    """Crea un nuevo contacto en Holded."""
    payload = {
        "name": datos.get("name", ""),
        "tradeName": datos.get("tradeName", ""),
        "code": datos.get("code", ""),
        "vatnumber": datos.get("vatnumber", datos.get("nif", "")),
        "email": datos.get("email", ""),
        "phone": datos.get("phone", datos.get("telefono", "")),
        "address": datos.get("address", datos.get("direccion", "")),
        "city": datos.get("city", datos.get("ciudad", "")),
        "postalCode": datos.get("postalCode", datos.get("cp", "")),
        "countryCode": datos.get("countryCode", "ESP"),
        "iban": datos.get("iban", ""),
        "type": [t.strip() for t in datos.get("type", "client").split(",") if t.strip()],
    }
    # Limpiar campos vacíos
    payload = {k: v for k, v in payload.items() if v}

    r = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=30)
    return r.json()


def importar_contactos(input_file: str):
    """Importa contactos desde un CSV a Holded."""
    # Primero, obtener todos los NIFs existentes para evitar duplicados
    print("Cargando contactos existentes para detectar duplicados...")
    existentes = get_todos_contactos()
    nifs_existentes = {c.get("vatnumber", "").upper() for c in existentes if c.get("vatnumber")}

    creados = 0
    omitidos = 0
    errores = []

    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        filas = list(reader)

    print(f"Importando {len(filas)} contactos desde {input_file}...")

    for i, fila in enumerate(filas, 1):
        nif = fila.get("vatnumber", fila.get("nif", "")).strip().upper()

        if nif and nif in nifs_existentes:
            print(f"  [{i}/{len(filas)}] OMITIDO (ya existe): {fila.get('name', '—')} — NIF: {nif}")
            omitidos += 1
            continue

        resultado = crear_contacto(fila)

        if resultado.get("id") or resultado.get("status") == 1:
            print(f"  [{i}/{len(filas)}] CREADO: {fila.get('name', '—')}")
            if nif:
                nifs_existentes.add(nif)
            creados += 1
        else:
            print(f"  [{i}/{len(filas)}] ERROR: {fila.get('name', '—')} — {resultado}")
            errores.append({"fila": i, "nombre": fila.get("name"), "error": str(resultado)})

        time.sleep(0.5)

    print(f"\nResultado: {creados} creados, {omitidos} omitidos, {len(errores)} errores")
    if errores:
        print("Errores:")
        for e in errores:
            print(f"  Fila {e['fila']}: {e['nombre']} — {e['error']}")


def verificar_contactos(input_file: str):
    """Verifica qué contactos del CSV no existen en Holded."""
    print("Cargando contactos de Holded...")
    existentes = get_todos_contactos()
    nifs_existentes = {c.get("vatnumber", "").upper() for c in existentes if c.get("vatnumber")}
    nombres_existentes = {c.get("name", "").upper() for c in existentes if c.get("name")}

    no_encontrados = []

    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            nif = fila.get("vatnumber", fila.get("nif", "")).strip().upper()
            nombre = fila.get("name", fila.get("nombre", "")).strip().upper()

            encontrado = (nif and nif in nifs_existentes) or (nombre and nombre in nombres_existentes)
            if not encontrado:
                no_encontrados.append(fila)

    print(f"\nContactos NO encontrados en Holded: {len(no_encontrados)}")
    for c in no_encontrados:
        print(f"  {c.get('name', c.get('nombre', '—'))} — NIF: {c.get('vatnumber', c.get('nif', '—'))}")


def main():
    parser = argparse.ArgumentParser(description="Sincronizar contactos con Holded")
    parser.add_argument("modo", choices=["export", "import", "check"])
    parser.add_argument("--input", help="CSV de entrada (para import y check)")
    parser.add_argument("--output", default="contactos_holded.csv", help="CSV de salida (para export)")
    args = parser.parse_args()

    if args.modo == "export":
        exportar_contactos(args.output)
    elif args.modo == "import":
        if not args.input:
            print("ERROR: --input requerido para modo import")
            return
        importar_contactos(args.input)
    elif args.modo == "check":
        if not args.input:
            print("ERROR: --input requerido para modo check")
            return
        verificar_contactos(args.input)


if __name__ == "__main__":
    main()
