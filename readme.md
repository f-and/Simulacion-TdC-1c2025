# Simulación para TP de Teoría de Control

Esta simulación está basada en la información recopilada para el trabajo práctico de Teoría de Control.

## Como ejecutarlo

Para ejecutar esta simulación se requiere:

- Tener Python instalado (https://www.python.org/downloads/)
- Tener pip instalado: Esto se valida ejecutando
  - Para Windows: `py -m pip --version`, si no está se puede ejecutar `py -m ensurepip --default-pip`
  - Para Linux/MacOS: `python3 -m pip --version`, si no está se puede ejecutar `python3 -m ensurepip --default-pip`
- Instalar los requerimientos: `pip install -r requirements.txt`.
- Ejecutar la simulación: `python -m simulacion.py`

## Como funciona la simulación

La simulación inicia instantaneamente con datos preconfigurados (un tánque con una cantidad inicial de vapor aleatoria y las variables del sistema pre-configuradas). A disposición se hayan 4 botones:
- Pausar/Reanudar simulación: Se puede pausar la simulación en cualquier momento para analizar los datos.
- Reiniciar la simulación: Se puede reiniciar la simulación para darle un nuevo valor inicial de vapor.
- Perturbación (consumo de emergencia): Se simula una perturbación donde se libera más vapor subitamente por un uso de emergencia, para demostrar que el sistema se estabiliza antes estas circumstancias.
- Perturbación (perdida de turbina): Se simula una perturbación donde una de las turbinas de carga deja de funcionar subitamente (pero es reemplazada por una inactiva), para demostrar que también se estabiliza ante estos casos.

A su vez hay un deslizador que controla la perturbación en forma de escalon, permitiendo subir o bajar el consumo para ver al sistema estabilizarse.

Por último, si el sistema llegase a fallar (por ejemplo por exceso de vapor en el tanque), va a aparecer un mensaje de falla por la causa, y se va a tener que reiniciar la simulación.