"""
webhook_handler.py
Servidor Flask para recibir y procesar webhooks de Holded.
Ejemplos de acciones: notificar por email, actualizar CRM externo, crear tareas...

Uso:
    pip install flask requests
    python webhook_handler.py
    # Configurar URL en Holded: Configuración → Integraciones → Webhooks
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def procesar_factura_creada(data: dict):
    """Se ejecuta cuando se crea una nueva factura de venta."""
    numero = data.get("docNumber", "—")
    contacto = data.get("contactName", "—")
    total = data.get("total", 0)
    logger.info(f"Nueva factura: {numero} — {contacto} — {total:.2f} €")
    # Aquí puedes: enviar notificación, crear tarea de seguimiento, etc.


def procesar_pago_registrado(data: dict):
    """Se ejecuta cuando se registra un cobro en una factura."""
    numero = data.get("docNumber", "—")
    importe = data.get("paymentAmount", data.get("total", 0))
    logger.info(f"Cobro registrado: {numero} — {importe:.2f} €")
    # Aquí puedes: actualizar CRM, enviar recibo, notificar al equipo...


def procesar_contacto_creado(data: dict):
    """Se ejecuta cuando se crea un nuevo contacto."""
    nombre = data.get("name", "—")
    nif = data.get("vatnumber", "—")
    logger.info(f"Nuevo contacto: {nombre} — NIF: {nif}")
    # Aquí puedes: crear lead en CRM externo, enviar email de bienvenida...


HANDLERS = {
    "document.created": procesar_factura_creada,
    "payment.created": procesar_pago_registrado,
    "contact.created": procesar_contacto_creado,
}


@app.route("/webhook/holded", methods=["POST"])
def webhook():
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Payload vacío"}), 400

    evento = payload.get("event", "unknown")
    data = payload.get("data", payload)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"[{timestamp}] Evento recibido: {evento}")

    # Guardar log del evento
    with open("webhook_log.jsonl", "a") as f:
        f.write(json.dumps({"timestamp": timestamp, "event": evento, "data": data}) + "\n")

    # Ejecutar handler si existe
    handler = HANDLERS.get(evento)
    if handler:
        try:
            handler(data)
        except Exception as e:
            logger.error(f"Error procesando evento {evento}: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok", "event": evento}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
