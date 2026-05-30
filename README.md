# PFO3 - Programacion sobre redes
Rediseño como Sistema Distribuido (Cliente-Servidor)

# Descripción
Implementación de un sistema distribuido con arquitectura cliente-servidor usando sockets TCP en Python puro (sin dependencias externas).

# Diagrama 
<img width="720" height="512" alt="Diagramas" src="https://github.com/user-attachments/assets/f09195b2-c43d-4d89-8cca-90a4913ab6dc" />

# Como ejecutar

Iniciar el servidor
```
python server.py
```
Salida esperada:
```
[10:00:00] INFO  Servidor escuchando en 0.0.0.0:9999
[10:00:00] INFO  Pool de hilos: 4 workers
 ```

Ejecutar los clientes (en otra terminal)
```
python client.py
```
Salida esperada:
```
[10:00:01] INFO  Iniciando 4 clientes concurrentes...
[10:00:01] INFO  [mobile-iOS-1] Enviando tarea '3f9a1b2c' (ml_inference)
[10:00:02] INFO  [mobile-iOS-1] ✓ Tarea '3f9a1b2c' completada en 0.91s por worker_1
...
```

# Notas
•	Requisitos: Python 3.10+.
•	No requiere instalación de dependencias externas (solo usa la librería estándar de Python: socket, threading, json, concurrent.futures).

# Autor
Victoria Sobral
