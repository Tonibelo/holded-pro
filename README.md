# 🏢 holded-pro

**La guía más completa de Holded para asesorías, contadores y desarrolladores.**

Convierte a Claude en un experto de Holded: responde consultas sobre cualquier módulo, guía flujos de trabajo, ayuda a presentar impuestos y automatiza tareas con la API REST.

[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge)](https://docs.anthropic.com)
[![Holded](https://img.shields.io/badge/Holded-ERP-orange?style=for-the-badge)](https://holded.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## 📦 Contenido

| Archivo | Descripción |
|---------|-------------|
| `SKILL.md` | Skill principal: configuración, flujos y trucos |
| `skills/facturacion.md` | Ventas, compras, presupuestos, series, cobros/pagos |
| `skills/contabilidad.md` | PGC, asientos, activos, amortizaciones, SII |
| `skills/tesoreria.md` | Conciliación, remesas SEPA, previsión de cash flow |
| `skills/impuestos.md` | Modelos 303, 111, 115, 190, 347, 349 paso a paso |
| `skills/asesorias-partners.md` | Programa Partners, gestión multicliente, marketplace |
| `skills/rrhh-nominas.md` | Empleados, nóminas, cotizaciones SS, finiquitos |
| `skills/crm-proyectos.md` | Embudos, proyectos, facturación por horas |
| `skills/api-referencia.md` | Endpoints REST, autenticación, ejemplos, webhooks |
| `scripts/facturas_export.py` | Exportar facturas a CSV por período y tipo |
| `scripts/contactos_sync.py` | Importar/exportar/verificar contactos |
| `scripts/modelo303_check.py` | Verificar IVA del trimestre antes del cierre |
| `scripts/cierre_ejercicio.py` | Checklist automatizado cierre anual |
| `ejemplos/webhook_handler.py` | Servidor Flask para procesar eventos de Holded |

---

## 🚀 Instalación (Claude Code)

```bash
mkdir -p ~/.claude/skills/holded-pro/skills
mkdir -p ~/.claude/skills/holded-pro/scripts
mkdir -p ~/.claude/skills/holded-pro/ejemplos

# SKILL.md principal
curl -o ~/.claude/skills/holded-pro/SKILL.md \
  https://raw.githubusercontent.com/TU_USUARIO/holded-pro/master/SKILL.md

# Skills por módulo
for skill in facturacion contabilidad tesoreria impuestos asesorias-partners rrhh-nominas crm-proyectos api-referencia; do
  curl -o ~/.claude/skills/holded-pro/skills/${skill}.md \
    https://raw.githubusercontent.com/TU_USUARIO/holded-pro/master/skills/${skill}.md
done

# Scripts de automatización
for script in facturas_export contactos_sync modelo303_check cierre_ejercicio; do
  curl -o ~/.claude/skills/holded-pro/scripts/${script}.py \
    https://raw.githubusercontent.com/TU_USUARIO/holded-pro/master/scripts/${script}.py
done
```

---

## 💬 Uso en Claude Code

```bash
# Cargar el skill
/holded-pro

# Consultas por módulo
/holded-pro facturación
/holded-pro contabilidad
/holded-pro impuestos
/holded-pro API

# Consultas específicas
/holded-pro "¿cómo cierro el trimestre de IVA?"
/holded-pro "¿qué endpoint uso para crear una factura?"
/holded-pro "cómo gestionar clientes como asesoría partner"
/holded-pro "checklist cierre de ejercicio"
```

---

## 🐍 Scripts de automatización

### Requisitos
```bash
pip install requests python-dateutil flask
```

### Exportar facturas del 4T 2024
```bash
python scripts/facturas_export.py --type invoice --start 2024-10-01 --end 2024-12-31
```

### Verificar IVA antes del cierre trimestral
```bash
python scripts/modelo303_check.py --trimestre 3 --year 2025
```

### Sincronizar contactos desde un CSV
```bash
python scripts/contactos_sync.py import --input nuevos_clientes.csv
python scripts/contactos_sync.py export --output backup_contactos.csv
```

### Checklist cierre de ejercicio
```bash
python scripts/cierre_ejercicio.py --year 2024
```

### Servidor de webhooks
```bash
python ejemplos/webhook_handler.py
# Configurar URL en Holded: Configuración → Integraciones → Webhooks → http://tu-servidor:5000/webhook/holded
```

---

## ⚙️ Configuración de la API Key

En todos los scripts, sustituye `TU_API_KEY_AQUI` por tu clave real:

```python
API_KEY = "TU_API_KEY_AQUI"
```

O mejor, usa variables de entorno:
```python
import os
API_KEY = os.environ.get("HOLDED_API_KEY", "")
```

```bash
export HOLDED_API_KEY="tu_api_key_real"
```

Obtener la API Key: **Holded → Configuración → Integraciones → API → Generar key**

---

## 📚 Módulos cubiertos

- ✅ **Facturación**: ventas, compras, presupuestos, proformas, albaranes, recurrentes
- ✅ **Contabilidad**: PGC, asientos, libros, activos fijos, amortizaciones, SII
- ✅ **Tesorería**: conciliación, remesas SEPA, previsión de cash flow, reglas automáticas
- ✅ **Impuestos**: modelos 303, 390, 111, 115, 180, 190, 193, 347, 349 desde Holded
- ✅ **Partners/Asesorías**: programa partner, niveles, portal multicliente, marketplace
- ✅ **RRHH**: empleados, nóminas, cotizaciones SS 2025, control horario, finiquitos
- ✅ **CRM**: embudos, oportunidades, actividades, presupuestos, reuniones
- ✅ **Proyectos**: tareas, imputación de horas, facturación por horas/hitos
- ✅ **API REST**: todos los endpoints principales, autenticación, paginación, webhooks

---

## 🤝 Contribuir

Pull requests bienvenidos. Si encuentras algo desactualizado o incorrecto, abre un issue o envía directamente tu corrección.

---

## 📄 Licencia

MIT

---

*Basado en la documentación oficial de [Holded](https://holded.com) y [Holded Developers](https://developers.holded.com). No es un producto oficial de Holded.*
