# Flujo de prueba en Swagger

Este flujo sirve para probar el nuevo contrato unificado de `productos`, donde categorias e ingredientes se envian dentro del mismo payload.

## Orden recomendado

1. `POST /categorias`
2. `POST /ingredientes`
3. `POST /productos`
4. `GET /productos`
5. `GET /productos/{producto_id}`
6. `PATCH /productos/{producto_id}`
7. `DELETE /productos/{producto_id}`

## 1. Crear una Categoria

Endpoint: `POST /categorias`

```json
{
  "nombre": "Pizzas",
  "descripcion": "Categoria principal",
  "imagen_url": "https://ejemplo.com/pizzas.jpg",
  "parent_id": null,
  "orden_display": 1
}
```

## 2. Crear un Ingrediente

Endpoint: `POST /ingredientes`

```json
{
  "nombre": "Queso",
  "descripcion": "Mozzarella",
  "es_alergeno": true
}
```

## 3. Crear un Producto con relaciones unificadas

Endpoint: `POST /productos`

```json
{
  "nombre": "Pizza Muzzarella",
  "descripcion": "Clasica",
  "precio_base": 12000,
  "imagen_url": "https://ejemplo.com/muza.jpg",
  "imagenes_url": [
    "https://ejemplo.com/muza-1.jpg",
    "https://ejemplo.com/muza-2.jpg"
  ],
  "stock_cantidad": 10,
  "tiempo_prep_min": 20,
  "categorias": [
    {
      "categoria_id": 1,
      "es_principal": true
    }
  ],
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "es_removible": true,
      "es_opcional": false
    }
  ]
}
```

## 4. Listar Productos

Endpoint: `GET /productos`

Query params sugeridos:

- `offset = 0`
- `limit = 20`

## 5. Obtener un Producto puntual

Endpoint: `GET /productos/1`

Usar el `id` que devuelva el alta del producto.

## 6. Actualizar datos base y relaciones del Producto

Endpoint: `PATCH /productos/1`

```json
{
  "precio_base": 13500,
  "stock_cantidad": 15,
  "categorias": [
    {
      "categoria_id": 1,
      "es_principal": true
    }
  ],
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "es_removible": true,
      "es_opcional": true
    }
  ]
}
```

Nota: si envias `categorias` o `ingredientes`, la lista se sincroniza completa. Eso significa que lo que no mandes dentro de esa lista se elimina de la relacion del producto.

## 7. Actualizar solo relaciones del Producto

Endpoint: `PATCH /productos/1`

```json
{
  "categorias": [
    {
      "categoria_id": 1,
      "es_principal": true
    }
  ],
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "es_removible": false,
      "es_opcional": true
    }
  ]
}
```

## 8. Borrar logicamente un Producto

Endpoint: `DELETE /productos/1`

No requiere body.
