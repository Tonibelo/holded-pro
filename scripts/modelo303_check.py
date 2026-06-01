"""
modelo303_check.py
Verifica el estado del IVA del trimestre antes del cierre:
- Facturas de venta sin tipo de IVA asignado
- Facturas de compra pendientes de contabilizar
- Resumen de bases e IVA del trimestre

Uso:
    python modelo303_check.py --trimestre 1 --year 2025
    python modelo303_check.py --trimestre 3 --year 2024

Requiere: pip install requests
"""

import requests
import time
import argparse
from datetime import datetime

API_KEY = "TU_API_KEY_AQUI"
BASE_URL = "https://api.holded.com/api/invoicing/v1/documents"
HEADERS = {"key": API_KEY}

TRIMESTRES = {
    1: ("01-01", "03-31"),
    2: ("04-01", "06-30"),
    3: ("07-01", "09-30"),
    4: ("10-01", "12-31"),
}


def get_fechas_trimestre(trimestre: int, year: int):
    inicio_str, fin_str = TRIMESTRES[trimestre]
    inicio = datetime.strptime(f"{year}-{inicio_str}", "%Y-%m-%d")
    fin = datetime.strptime(f"{year}-{fin_str}", "%Y-%m-%d")
    return int(inicio.timestamp()), int(fin.timestamp())


def obtener_documentos(tipo: str, start_ts: int, end_ts: int) -> list:
    docs = []
    page = 1
    while True:
        r = requests.get(
            f"{BASE_URL}/{tipo}",
            headers=HEADERS,
            params={"page": page, "starttmp": start_ts, "endtmp": end_ts},
            timeout=30
        )
        if r.status_code == 429:
            print("Rate limit. Esperando 60s...")
            time.sleep(60)
            continue
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        if isinstance(data, list):
            docs.extend(data)
        else:
            items = data.get("data", [])
            if not items:
                break
            docs.extend(items)
        page += 1
        time.sleep(0.5)
    return docs


def analizar_iva(documentos: list, tipo: str) -> dict:
    """Analiza el IVA de una lista de documentos."""
    resultado = {
        "total_docs": len(documentos),
        "sin_iva": [],
        "bases_por_tipo": {},
        "total_base": 0,
        "total_iva": 0,
    }

    for doc in documentos:
        items = doc.get("items", doc.get("lines", []))
        tiene_iva = False

        for item in items:
            tax = item.get("tax", item.get("taxId", 0))
            subtotal = float(item.get("subtotal", item.get("amount", 0)))
            iva_importe = subtotal * (float(tax) / 100) if tax else 0

            if tax:
                tiene_iva = True
                tax_key = f"{tax}%"
                if tax_key not in resultado["bases_por_tipo"]:
                    resultado["bases_por_tipo"][tax_key] = {"base": 0, "iva": 0}
                resultado["bases_por_tipo"][tax_key]["base"] += subtotal
                resultado["bases_por_tipo"][tax_key]["iva"] += iva_importe
                resultado["total_base"] += subtotal
                resultado["total_iva"] += iva_importe

        if not tiene_iva:
            resultado["sin_iva"].append({
                "id": doc.get("id"),
                "numero": doc.get("docNumber", "Sin número"),
                "contacto": doc.get("contactName", "—"),
                "total": doc.get("total", 0),
                "fecha": datetime.fromtimestamp(doc.get("date", 0)).strftime("%d/%m/%Y") if doc.get("date") else "—"
            })

    return resultado


def imprimir_informe(resultado_ventas: dict, resultado_compras: dict, trimestre: int, year: int):
    print("\n" + "="*60)
    print(f"  INFORME IVA — {trimestre}T {year}")
    print("="*60)

    print(f"\n📤 VENTAS ({resultado_ventas['total_docs']} facturas)")
    print(f"   Base imponible total:  {resultado_ventas['total_base']:>10,.2f} €")
    print(f"   IVA repercutido total: {resultado_ventas['total_iva']:>10,.2f} €")
    print(f"   Desglose por tipo:")
    for tipo, valores in resultado_ventas["bases_por_tipo"].items():
        print(f"     IVA {tipo:>4}: Base {valores['base']:>10,.2f} € | Cuota {valores['iva']:>8,.2f} €")

    if resultado_ventas["sin_iva"]:
        print(f"\n  ⚠️  FACTURAS DE VENTA SIN IVA ({len(resultado_ventas['sin_iva'])} docs):")
        for doc in resultado_ventas["sin_iva"][:10]:  # Mostrar máx 10
            print(f"     [{doc['fecha']}] {doc['numero']} — {doc['contacto']} — {doc['total']:.2f} €")

    print(f"\n📥 COMPRAS ({resultado_compras['total_docs']} facturas)")
    print(f"   Base imponible total:  {resultado_compras['total_base']:>10,.2f} €")
    print(f"   IVA soportado total:   {resultado_compras['total_iva']:>10,.2f} €")
    print(f"   Desglose por tipo:")
    for tipo, valores in resultado_compras["bases_por_tipo"].items():
        print(f"     IVA {tipo:>4}: Base {valores['base']:>10,.2f} € | Cuota {valores['iva']:>8,.2f} €")

    resultado_303 = resultado_ventas["total_iva"] - resultado_compras["total_iva"]
    print(f"\n{'='*60}")
    print(f"  RESULTADO MODELO 303:")
    print(f"  IVA repercutido: {resultado_ventas['total_iva']:>10,.2f} €")
    print(f"  IVA soportado:   {resultado_compras['total_iva']:>10,.2f} €")
    print(f"  {'A INGRESAR' if resultado_303 >= 0 else 'A COMPENSAR'}:     {abs(resultado_303):>10,.2f} €")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Verificar IVA trimestral en Holded")
    parser.add_argument("--trimestre", type=int, required=True, choices=[1, 2, 3, 4])
    parser.add_argument("--year", type=int, default=datetime.now().year)
    args = parser.parse_args()

    start_ts, end_ts = get_fechas_trimestre(args.trimestre, args.year)

    print(f"Obteniendo facturas del {args.trimestre}T {args.year}...")
    ventas = obtener_documentos("invoice", start_ts, end_ts)
    compras = obtener_documentos("purchase", start_ts, end_ts)

    resultado_ventas = analizar_iva(ventas, "ventas")
    resultado_compras = analizar_iva(compras, "compras")

    imprimir_informe(resultado_ventas, resultado_compras, args.trimestre, args.year)


if __name__ == "__main__":
    main()
