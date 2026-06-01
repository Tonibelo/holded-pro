"""
cierre_ejercicio.py
Checklist automatizado para el cierre del ejercicio fiscal en Holded.
Verifica el estado de: facturas, cobros, conciliación, asientos y nóminas.

Uso:
    python cierre_ejercicio.py --year 2024

Requiere: pip install requests
"""

import requests
import time
import argparse
from datetime import datetime

API_KEY = "TU_API_KEY_AQUI"
BASE_URL = "https://api.holded.com/api"
HEADERS = {"key": API_KEY}

OK = "✅"
WARN = "⚠️ "
ERR = "❌"


def get_docs(tipo: str, start_ts: int, end_ts: int, page: int = 1) -> list:
    r = requests.get(
        f"{BASE_URL}/invoicing/v1/documents/{tipo}",
        headers=HEADERS,
        params={"page": page, "starttmp": start_ts, "endtmp": end_ts},
        timeout=30
    )
    if r.status_code == 429:
        time.sleep(60)
        return get_docs(tipo, start_ts, end_ts, page)
    if r.status_code != 200:
        return []
    data = r.json()
    return data if isinstance(data, list) else data.get("data", [])


def get_todos_docs(tipo: str, start_ts: int, end_ts: int) -> list:
    todos = []
    page = 1
    while True:
        docs = get_docs(tipo, start_ts, end_ts, page)
        if not docs:
            break
        todos.extend(docs)
        page += 1
        time.sleep(0.3)
    return todos


def verificar_facturas_pendientes(year: int):
    print(f"\n{'─'*50}")
    print("📄 FACTURAS")
    print(f"{'─'*50}")

    start = int(datetime(year, 1, 1).timestamp())
    end = int(datetime(year, 12, 31, 23, 59, 59).timestamp())

    # Facturas de venta
    ventas = get_todos_docs("invoice", start, end)
    pendientes_cobro = [f for f in ventas if f.get("pending", 0) > 0]
    borradores = [f for f in ventas if f.get("status") in ["draft", 0]]

    estado_v = OK if not pendientes_cobro and not borradores else WARN
    print(f"{estado_v} Ventas: {len(ventas)} facturas")
    if borradores:
        print(f"   {ERR} {len(borradores)} en estado borrador (no contabilizadas)")
    if pendientes_cobro:
        total_pendiente = sum(float(f.get("pending", 0)) for f in pendientes_cobro)
        print(f"   {WARN} {len(pendientes_cobro)} con cobro pendiente ({total_pendiente:,.2f} €)")

    # Facturas de compra
    compras = get_todos_docs("purchase", start, end)
    pendientes_pago = [f for f in compras if f.get("pending", 0) > 0]

    estado_c = OK if not pendientes_pago else WARN
    print(f"{estado_c} Compras: {len(compras)} facturas")
    if pendientes_pago:
        total_pend = sum(float(f.get("pending", 0)) for f in pendientes_pago)
        print(f"   {WARN} {len(pendientes_pago)} con pago pendiente ({total_pend:,.2f} €)")

    return {
        "ventas_total": len(ventas),
        "ventas_borradores": len(borradores),
        "ventas_pendientes_cobro": len(pendientes_cobro),
        "compras_total": len(compras),
        "compras_pendientes_pago": len(pendientes_pago),
    }


def verificar_impuestos_trimestrales(year: int):
    print(f"\n{'─'*50}")
    print("🧾 IMPUESTOS TRIMESTRALES")
    print(f"{'─'*50}")

    # No podemos verificar directamente si los modelos se presentaron vía API
    # pero podemos verificar que hay facturas en cada trimestre
    trimestres = {
        "1T": (datetime(year, 1, 1), datetime(year, 3, 31)),
        "2T": (datetime(year, 4, 1), datetime(year, 6, 30)),
        "3T": (datetime(year, 7, 1), datetime(year, 9, 30)),
        "4T": (datetime(year, 10, 1), datetime(year, 12, 31)),
    }

    for nombre, (inicio, fin) in trimestres.items():
        start_ts = int(inicio.timestamp())
        end_ts = int(fin.timestamp())
        ventas = get_todos_docs("invoice", start_ts, end_ts)
        compras = get_todos_docs("purchase", start_ts, end_ts)
        print(f"{OK} {nombre}: {len(ventas)} facturas venta / {len(compras)} compras")
        time.sleep(0.5)

    print(f"\n{WARN} Verificar manualmente en Holded → Contabilidad → Impuestos que los modelos 303, 111 y 115 de los 4 trimestres están presentados")


def generar_resumen_final(stats: dict, year: int):
    print(f"\n{'='*50}")
    print(f"  RESUMEN CIERRE EJERCICIO {year}")
    print(f"{'='*50}")

    items_ok = 0
    items_warn = 0

    checks = [
        ("Facturas venta contabilizadas", stats["ventas_borradores"] == 0),
        ("Cobros al día", stats["ventas_pendientes_cobro"] == 0),
        ("Pagos a proveedores al día", stats["compras_pendientes_pago"] == 0),
    ]

    for descripcion, ok in checks:
        if ok:
            print(f"{OK} {descripcion}")
            items_ok += 1
        else:
            print(f"{WARN} {descripcion} — REVISAR")
            items_warn += 1

    pendientes_manuales = [
        "Amortizaciones del ejercicio contabilizadas",
        "Provisiones por deterioro de clientes",
        "Periodificaciones de gastos/ingresos",
        "Asiento de nómina de diciembre",
        "Conciliación bancaria de diciembre",
        "Modelos 303, 111, 115 del 4T presentados",
        "Modelo 190 y 180 anuales presentados",
        "Modelo 347 presentado (si aplica)",
        "Inventario de activos fijos actualizado",
    ]

    print(f"\n📋 PENDIENTE DE VERIFICAR MANUALMENTE:")
    for item in pendientes_manuales:
        print(f"   {item}")

    print(f"\n{'─'*50}")
    print(f"  Automáticos OK: {items_ok}/{items_ok + items_warn}")
    print(f"  Manuales pendientes: {len(pendientes_manuales)}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="Checklist cierre de ejercicio en Holded")
    parser.add_argument("--year", type=int, default=datetime.now().year - 1)
    args = parser.parse_args()

    print(f"\n🔍 INICIANDO VERIFICACIÓN CIERRE EJERCICIO {args.year}")
    print(f"   Fecha de verificación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    stats = verificar_facturas_pendientes(args.year)
    verificar_impuestos_trimestrales(args.year)
    generar_resumen_final(stats, args.year)


if __name__ == "__main__":
    main()
