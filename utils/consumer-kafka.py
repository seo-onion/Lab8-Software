from confluent_kafka import Consumer

# 1. Configuración de conexión
configuracion = {
    "bootstrap.servers": "213.199.42.57:9092",
    "group.id": "grupo_estudiantes_1",  # Identificador del grupo de consumidores
    "auto.offset.reset": "earliest",  # Si es la primera vez, lee desde el principio
}

# 2. Crear la instancia del Consumidor
consumidor = Consumer(configuracion)
tema = "laboratorio_1"

# 3. Suscribirse al tema
consumidor.subscribe([tema])

print(f" [*] Esperando mensajes en el topic '{tema}'. Presiona CTRL+C para salir.")

try:
    # 4. Bucle infinito escuchando mensajes
    while True:
        # Pide mensajes al servidor (espera hasta 1 segundo)
        msg = consumidor.poll(timeout=1.0)

        if msg is None:
            continue  # No hay mensajes nuevos, sigue esperando

        if msg.error():
            print(f" [!] Error de Kafka: {msg.error()}")
            continue

        # Decodificar y mostrar el mensaje
        texto = msg.value().decode("utf-8")
        print(f" [x] Mensaje recibido: {texto}")

except KeyboardInterrupt:
    print("\n [*] Deteniendo el consumidor...")
finally:
    # 5. Cerrar la conexión limpiamente (vital en Kafka para liberar el grupo)
    consumidor.close()
