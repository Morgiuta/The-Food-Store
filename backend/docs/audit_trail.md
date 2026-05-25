# Audit Trail de pedidos

El historial de estados de pedidos es append-only: solo se inserta un registro nuevo cuando cambia el estado de un pedido; nunca se modifica ni se elimina.

En codigo, no existen endpoints ni metodos de repositorio para actualizar o borrar `HistorialEstadoPedido`. Las transiciones pasan por `PedidosService`, que agrega una nueva fila en `historial_estados_pedido`.

En PostgreSQL, el startup crea el trigger `trg_historial_estados_pedido_append_only`, que bloquea cualquier `UPDATE` o `DELETE` directo sobre `historial_estados_pedido`.
