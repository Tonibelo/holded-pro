"""
facturas_export.py
Exporta facturas de Holded a CSV filtradas por tipo y rango de fechas.

Uso:
    python facturas_export.py --type invoice --start 2024-01-01 --end 2024-12-31
    python facturas_export.py --type purchase --start 2024-10-01 --end 2024-12-31

Requiere: pip install requests python-dateutil
"""

import requests
import csv
import time
import argparse
from datetime import datetime
from dateutil import parser as dateparser

API_KEY = "TU_API_KEY_AQUI"  # Sustituir por tu API Key de Holded
BASE_URL = "https://api.holded.com/api/invoicing/v1/documents"
HEADERS = {"key": API_KEY}

TIPOS_VALIDOS = [
    "invoice", "salesreceipt", "creditnote", "proforma",
    "estimate", "waybill", "purchase", "purchaseorder", "purchaserefund"
]


def fecha_a_timestamp(fecha_str: str) -> int:
    """Convierte 'YYYY-MM-DD' a timestamp Unix."""
    dt = dateparser.parse(fecha_str)
    return int(dt.timestamp())


def obtener_todas_facturas(tipo: str, start_ts: int, end_ts: int) -> list:
    """Obtiene todas las facturas paginando la API."""
    facturas = []
    page = 1
    print(f"Descargando {tipo}s...")

    while True:
        url = f"{BASE_URL}/{tipo}"
        params = {"page": page, "starttmp": start_ts, "endtmp": end_ts}

        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=30)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                print("Rate limit alcanzado. Esperando 60s...")
                time.sleep(60)
                continue
            elif r.status_code == 401:
                print("ERROR: API Key inválida. Revisa tu configuración.")
                break
            else:
                print(f"Error HTTP {r.status_code}: {e}")
                break

        data = r.json()

        # La API devuelve lista vacía o dict vacío en última página
        if not data or (isinstance(data, list) and len(data) == 0):
            break

        if isinstance(data, list):
            facturas.extend(data)
            print(f"  Página {page}: {len(data)} documentos")
        else:
            # A veces devuelve un dict con los datos
            items = data.get("data", data.get("items", []))
            if not items:
                break
            facturas.extend(items)
            print(f"  Página {page}: {len(items)} documentos")

        page += 1
        time.sleep(0.5)  # Respetar rate limits

    print(f"Total: {len(facturas)} documentos descargados")
    return facturas


def exportar_a_csv(facturas: list, tipo: str, filename: str = None):
    """Exporta la lista de facturas a un CSV."""
    if not facturas:
        print("No hay datos para exportar.")
        return

    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"holded_{tipo}_{ts}.csv"

    # Campos a exportar
    campos = [
        "id", "docNumber", "date", "contactName", "contactCode",
        "subtotal", "taxAmount", "total", "currency", "status",
        "pending", "notes"
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()

        for factura in facturas:
            # Normalizar fecha
            fecha = factura.get("date", 0)
            if isinstance(fecha, int) and fecha > 0:
                factura["date"] = datetime.fromtimestamp(fecha).strftime("%Y-%m-%d")

            # Extraer nombre del contacto si viene como objeto
            contacto = factura.get("contact", {})
            if isinstance(contacto, dict):
                factura["contactName"] = contacto.get("name", factura.get("contactName", ""))
                factura["contactCode"] = contacto.get("code", factura.get("contactCode", ""))

            writer.writerow({k: factura.get(k, "") for k in campos})

    print(f"Exportado a: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Exportar facturas de Holded a CSV")
    parser.add_argument("--type", default="invoice", choices=TIPOS_VALIDOS,
                        help="Tipo de documento (default: invoice)")
    parser.add_argument("--start", required=True, help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--output", help="Nombre del archivo CSV de salida")
    args = parser.parse_args()

    start_ts = fecha_a_timestamp(args.start)
    end_ts = fecha_a_timestamp(args.end)

    print(f"Exportando {args.type} desde {args.start} hasta {args.end}")
    facturas = obtener_todas_facturas(args.type, start_ts, end_ts)
    exportar_a_csv(facturas, args.type, args.output)


if __name__ == "__main__":
    main()
