---
name: holded-pro
description: "Guía experta de Holded para asesorías, contadores y desarrolladores. Cubre todos los módulos (facturación, contabilidad, tesorería, impuestos, RRHH, CRM, proyectos), el programa de Partners, la API REST y automatizaciones con Python. Usar cuando se trabaje con Holded, sus configuraciones, flujos de trabajo, presentación de impuestos, gestión de clientes o integración vía API."
allowed-tools:
  - Read
  - Grep
argument-hint: [módulo, tarea, endpoint, flujo]
---

# Holded Pro — Guía para Asesorías y Desarrolladores

## Cómo usar esta skill

- **Sin argumentos** — carga los módulos principales y flujos más usados
- **Por módulo** — `facturación`, `contabilidad`, `tesorería`, `impuestos`, `RRHH`, `CRM`, `API`
- **Por tarea** — "¿cómo cierro el trimestre de IVA?", "cómo importo facturas", "cómo gestiono un cliente como Partner"
- **Por endpoint** — "qué endpoint uso para crear una factura", "cómo paginar contactos"

Archivos de referencia detallada (cargar según tema):
- `skills/facturacion.md` — ventas, compras, presupuestos, proformas, series
- `skills/contabilidad.md` — asientos, plan de cuentas, cierres, activos
- `skills/tesoreria.md` — conciliación, remesas, cobros, pagos, previsiones
- `skills/impuestos.md` — modelos 303, 111, 115, 190, 347 desde Holded
- `skills/asesorias-partners.md` — programa Partners, portal multicliente, accesos
- `skills/rrhh-nominas.md` — empleados, nóminas, SS, contratos
- `skills/crm-proyectos.md` — embudos, tareas, facturación por horas
- `skills/api-referencia.md` — endpoints, autenticación, ejemplos, paginación

Scripts listos en `scripts/`:
- `facturas_export.py` — exportar facturas por período
- `contactos_sync.py` — sincronizar contactos con CRM externo
- `modelo303_check.py` — verificar IVA antes del cierre trimestral
- `cierre_ejercicio.py` — checklist automatizado cierre anual
- `webhook_handler.py` — procesar eventos en tiempo real

---

## Holded en 60 segundos

**Holded** es un ERP en la nube para pymes y asesorías españolas. Integra en una sola plataforma:

| Módulo | Qué gestiona |
|--------|-------------|
| **Ventas** | Facturas, presupuestos, proformas, albaranes, cobros |
| **Compras** | Facturas de proveedor, escáner de facturas, pagos |
| **Contabilidad** | Plan General Contable, asientos, libros, activos fijos |
| **Tesorería** | Cuentas bancarias, conciliación, remesas, previsiones |
| **Impuestos** | Modelos tributarios, cuadros de IVA, retenciones |
| **Inventario** | Productos, stock, pedidos, almacenes |
| **RRHH** | Empleados, nóminas, control horario, vacaciones |
| **CRM** | Contactos, embudos, actividades, presupuestos |
| **Proyectos** | Tareas, tiempos, facturación de proyectos |
| **Analítica** | Informes P&L, balance, cash flow, KPIs |

---

## Configuración inicial — Checklist

### Nueva empresa en Holded
1. **Datos empresa** → Configuración → Empresa → completar NIF, dirección, CNAE
2. **Series de facturación** → Ventas → Configuración → Series (definir prefijos y numeración)
3. **Tipos de IVA** → Configuración → Impuestos → revisar tipos y % por defecto
4. **Plan de cuentas** → Contabilidad → Plan de cuentas → importar o ajustar PGC
5. **Cuentas bancarias** → Tesorería → Cuentas → añadir con IBAN para conciliación
6. **Métodos de pago** → Configuración → Pagos → efectivo, transferencia, domiciliación
7. **Usuarios y permisos** → Configuración → Usuarios → roles por módulo
8. **Integración asesoría** → si eres partner: invitar asesoría con rol "Contabilidad"

### Configurar para asesoría (modo Partner)
1. Crear cuenta Partner en holded.com/partners
2. Plan Asesor: comprar licencias o activar Unlimited
3. Crear empresa cliente → asignar gestor de la asesoría
4. Configurar acceso bidireccional

---

## Flujos de trabajo más usados

### Ciclo de ventas completo
```
Presupuesto → [aceptado] → Proforma / Albarán → Factura → Cobro → Conciliación bancaria
```

### Ciclo de compras completo
```
Factura proveedor (manual o escáner) → Contabilización → Pago → Conciliación
```

### Cierre trimestral IVA
```
1. Revisar facturas emitidas y recibidas del trimestre
2. Contabilidad → Impuestos → Modelo 303 → revisar cuadro
3. Ajustar facturas sin contabilizar
4. Exportar modelo 303 → presentar en AEAT
5. Si sale a pagar: registrar pago en tesorería
```

### Cierre mensual asesoría
```
1. Sincronizar movimientos bancarios (conciliación)
2. Contabilizar facturas pendientes del cliente
3. Revisar asientos automáticos (nóminas, amortizaciones)
4. Generar balance provisional
5. Exportar SII si aplica
```

---

## Atajos y trucos clave

- **Duplicar documento** → botón "..." en cualquier factura/presupuesto
- **Plantillas** → guardar presupuestos recurrentes como plantilla
- **Etiquetas** → sistema de tags en contactos y documentos para filtrar
- **Factura recurrente** → Ventas → Recurrentes (auto-genera mensualmente)
- **Escáner facturas** → Compras → Escáner → sube PDF/foto → Holded extrae datos con OCR

---

## Integraciones nativas destacadas

| Integración | Para qué |
|-------------|---------|
| **Stripe** | Cobros online con link de pago en facturas |
| **GoCardless** | Domiciliaciones SEPA |
| **Shopify / WooCommerce** | Sincronizar pedidos e-commerce |
| **Zapier / Make** | Automatizaciones sin código |
| **SII (AEAT)** | Envío automático de facturas |
| **A3 / Sage** | Exportación contable para asesorías |

---

## Errores frecuentes y soluciones

| Problema | Causa probable | Solución |
|---------|---------------|---------|
| Factura no aparece en modelo 303 | Sin tipo de IVA asignado | Editar factura → asignar tipo IVA correcto |
| Asiento descuadrado | Factura con múltiples tipos IVA mal configurada | Revisar líneas de la factura y cuentas contables |
| Contacto duplicado | Mismo NIF importado dos veces | Contactos → Fusionar duplicados |
| Banco no sincroniza | Token de banca expirado | Tesorería → Cuentas → Reconectar |
| Nómina no contabilizada | Falta configuración de cuentas SS | RRHH → Configuración → Cuentas contables nómina |
| SII rechazado | Factura con datos incompletos | Contabilidad → SII → Ver errores → corregir factura |
