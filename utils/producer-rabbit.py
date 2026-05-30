import pika

credenciales = pika.PlainCredentials("students", "Ut3c2026")
parametros = pika.ConnectionParameters("213.199.42.57", 5672, "/", credenciales)

try:
    conexion = pika.BlockingConnection(parametros)
    canal = conexion.channel()

    # 2. Declarar la cola (crearla si no existe)
    nombre_cola = "laboratorio_1"
    canal.queue_declare(queue=nombre_cola, durable=True)

    # 3. Crear el mensaje y enviarlo
    mensaje = "¡Hola! Este es el primer mensaje del laboratorio."
    canal.basic_publish(exchange="", routing_key=nombre_cola, body=mensaje)

    print(f" [x] Mensaje enviado exitosamente: '{mensaje}'")

except Exception as e:
    print(f" [!] Error de conexión: {e}")
finally:
    # 4. Cerrar la conexión limpiamente
    if "conexion" in locals() and conexion.is_open:
        conexion.close()
