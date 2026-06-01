# Holded — API REST: Referencia

## Autenticación

### Obtener API Key
1. Holded → Configuración → Integraciones → API
2. Generar nueva API Key (una por empresa)
3. La key solo se muestra una vez: **guardarla de inmediato**

### Usar la API Key
```http
GET https://api.holded.com/api/invoicing/v1/documents/invoice
key: TU_API_KEY_AQUI
@Content-Type: application/json
```

La key va siempre en el **header** `key`, nunca en la URL.

## Base URL y versiones

```
https://api.holded.com/api/{módulo}/{versión}/{recurso}
```

## Endpoints de Facturación
- GET /api/invoicing/v1/documents/{type}
- POST /api/invoicing/v1/documents/invoice
- PUT /api/invoicing/v1/documents/{type}/{id}

## Endpoints de Contactos
- GET /api/contacts/v1/contacts
- POST /api/contacts/v1/contacts

## Paginación
- 20 resultados por página por defecto
- Parámetro: `?page=2`

## Códigos de respuesta
- 200 OK, 201 Creado, 400 Error, 401 API Key inválida, 404 No encontrado, 429 Rate limit

## Webhooks
- Configuración → Integraciones → Webhooks
- Eventos: document.created, payment.created, contact.updated
