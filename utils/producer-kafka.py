# Kafka solo crea el topic cuando el primer mensaje es enviado, por eso el productor se ejecuta antes que el consumidor

from confluent_kafka import Producer

# 1. Configuración de conexión (IP pública y puerto)
configuracion = {"bootstrap.servers": "213.199.42.57:9092"}

# 2. Crear la instancia del Productor
productor = Producer(configuracion)
tema = "laboratorio_1"


# Función auxiliar para confirmar si el mensaje llegó o falló
def confirmacion_entrega(err, msg):
    if err is not None:
        print(f" [!] Error al entregar el mensaje: {err}")
    else:
        print(f" [x] Mensaje guardado en el topic '{msg.topic()}' (Partición: {msg.partition()})")


# 3. Crear y enviar el mensaje
mensaje = "¡Hola Kafka! Este es el primer mensaje del laboratorio."

# Kafka envía los mensajes en formato de bytes, por eso usamos .encode('utf-8')
productor.produce(tema, value=mensaje.encode("utf-8"), callback=confirmacion_entrega)

print(" [*] Enviando mensaje al servidor...")

# 4. Asegurarse de que el mensaje salga de la memoria local hacia el servidor
productor.flush()
