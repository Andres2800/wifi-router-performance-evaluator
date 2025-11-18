import pywifi
import speedtest
import time
import logging
import json
import mysql.connector
from ping3 import ping
from pywifi import const
from plumbum import local
from termcolor import colored
import matplotlib.pyplot as plt
from plumbum.commands.processes import CommandNotFound, ProcessExecutionError

#---------------------------------------------------------------------
#               Declaración de funciones
#---------------------------------------------------------------------

def print_with_color(text, color):
    """
    Imprime un texto en la consola con un color específico.

    Args:
        text (str): El texto que se desea imprimir.
        color (str): El color en el que se desea imprimir el texto. 
                     Debe ser un color válido reconocido por la biblioteca `colored`.
    """
    print(colored(text, color))


def commit_base(datos, valores):
    """
    Inserta datos de evaluación de routers/access point en la base de datos MySQL.

    Establece una conexión con la base de datos, prepara las sentencias SQL para insertar
    datos en dos tablas diferentes y ejecuta estas sentencias con los datos proporcionados.

    Args:
        datos (list): Lista de datos relacionados con el rendimiento del router.
                      Debe contener datos como velocidad de descarga, carga, latencias, jitter, etc.
        valores (list): Lista de valores adicionales que se desean registrar en la base de datos.

    Conexiones y tablas:
        - Se conecta a la base de datos "prueba_routers_huawei".
        - Inserta datos en las siguientes tablas:
            - evaluacion_parametros3
            - valores_medidos3

    El formato de las sentencias SQL se encuentra en los comentarios y se utiliza 
    una estructura de marcadores de posición (%s) para asegurar la correcta inserción de los datos.

    """
    # Establecer conexión a la base de datos
    conexion1 = mysql.connector.connect(host="localhost", user="root", passwd="", database="prueba_routers_huawei")
    cursor1 = conexion1.cursor()
    
    # SQL para insertar datos en la tabla de evaluación
    sq2 = "insert into evaluacion_parametros3(`Fabricante`, `Velocidad descarga`, `Velocidad carga`, `Latencia servidor 1`, `Jitter servidor 1`, `Perdidas servidor 1`, `Latencia servidor 2`, `Jitter servidor 2`, `Perdidas servidor 2`, `Latencia servidor 3`, `Jitter servidor 3`, `Perdidas servidor 3`,`Capacidad ethernet 1`, `Capacidad ethernet 2`, `Potencia wifi6 2.4GHz cerca`, `Potencia wifi6 2.4GHz medio`,`Potencia wifi6 2.4GHz lejos`, `Potencia wifi6 5GHz cerca`,`Potencia wifi6 5GHz medio`,`Potencia wifi6 5GHz lejos`, `Potencia wifi5 5GHz cerca`, `Potencia wifi5 5GHz medio`, `Potencia wifi5 5GHz lejos`, `Capacidad wifi6 2.4GHz cerca`,`Capacidad wifi6 2.4GHz medio`,`Capacidad wifi6 2.4GHz lejos`, `Capacidad wifi6 5GHz cerca`,`Capacidad wifi6 5GHz medio`,`Capacidad wifi6 5GHz lejos`, `Capacidad wifi5 5GHz cerca`, `Capacidad wifi5 5GHz medio`, `Capacidad wifi5 5GHz lejos`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    # SQL para insertar datos en la tabla de valores medidos
    sql = "insert into valores_medidos3(`Fabricante`, `Velocidad descarga`, `Velocidad carga`, `Latencia servidor 1`, `Jitter servidor 1`, `Perdidas servidor 1`, `Latencia servidor 2`, `Jitter servidor 2`, `Perdidas servidor 2`, `Latencia servidor 3`, `Jitter servidor 3`, `Perdidas servidor 3`,`Capacidad ethernet 1`, `Capacidad ethernet 2`, `Potencia wifi6 2.4GHz cerca`, `Potencia wifi6 2.4GHz medio`,`Potencia wifi6 2.4GHz lejos`, `Potencia wifi6 5GHz cerca`,`Potencia wifi6 5GHz medio`,`Potencia wifi6 5GHz lejos`, `Potencia wifi5 5GHz cerca`, `Potencia wifi5 5GHz medio`, `Potencia wifi5 5GHz lejos`, `Capacidad wifi6 2.4GHz cerca`,`Capacidad wifi6 2.4GHz medio`,`Capacidad wifi6 2.4GHz lejos`, `Capacidad wifi6 5GHz cerca`,`Capacidad wifi6 5GHz medio`,`Capacidad wifi6 5GHz lejos`, `Capacidad wifi5 5GHz cerca`, `Capacidad wifi5 5GHz medio`, `Capacidad wifi5 5GHz lejos`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    # Preparar datos para la inserción
    lista = ['Huawei']  # Inicializa la lista con el fabricante
    for i in datos:
        lista.append(str(i))  # Agrega cada dato a la lista como una cadena
    tupla = tuple(lista)  # Convierte la lista en una tupla para la inserción

    # Ejecutar la primera sentencia SQL
    cursor1.execute(sql, tupla)

    # Preparar y ejecutar la segunda sentencia SQL
    tupla = tuple(valores)  # Convierte los valores en una tupla
    cursor1.execute(sq2, tupla)

    # Confirmar los cambios y cerrar la conexión
    conexion1.commit()
    conexion1.close()

def umbrales(redes, potencias, velocidades, tiempos_medios, jitter_medios, perdidos, ethernet, wifi):
    """
    Evalúa el cumplimiento de diversos parámetros de rendimiento de routers o puntos de acceso
    según umbrales predefinidos y registra los resultados en la base de datos.

    Args:
        redes (list): Lista de nombres de redes perteneciente al router evaluado.
        potencias (list): Lista de listas que contienen las potencias medidas de las redes.
        velocidades (list): Lista de velocidades de descarga y carga medidas.
        tiempos_medios (list): Lista de latencias medidas a varios servidores.
        jitter_medios (list): Lista de valores de jitter medidos a varios servidores.
        perdidos (list): Lista de valores de paquetes perdidos a varios servidores.
        ethernet (list): Lista de listas que contienen las capacidades de los puertos Ethernet.
        wifi (list): Lista de listas que contienen las capacidades WiFi medidas.

    Returns:
        None
    """
    commit = True  # Variable para controlar el compromiso de los datos
    base = []  # Lista para almacenar el cumplimiento de parámetros
    valores = ['Huawei']  # Inicializa la lista de valores con el fabricante
    # Listas para almacenar los resultados de las evaluaciones
    res_potencias = []
    res_velocidades = []
    res_tiempos = []
    res_jitter = []
    res_perdidos = []
    res_ethernet = []
    res_wifi = []

    # Definición de umbrales para las evaluaciones
    umbral_potencias = [-50, -60, -70]
    umbral_velocidades = 50
    umbral_tiempos = [50, 50, 10]
    umbral_jitter = 30
    umbral_perdidos = 1
    umbral_ethernet = [900, 900]
    umbral_wifi = [[50, 50], [400, 400], [350, 350]]

    # Evaluación de velocidades
    for i in range(2):
        res_velocidades.append(velocidades[i] >= umbral_velocidades)
        valores.append(velocidades[i])

    # Evaluación de latencias, jitter y paquetes perdidos
    for i in range(3):
        res_tiempos.append(tiempos_medios[i] <= umbral_tiempos[i])
        res_jitter.append(jitter_medios[i] <= umbral_jitter)
        res_perdidos.append(perdidos[i] <= umbral_perdidos)
        valores.append(tiempos_medios[i])
        valores.append(jitter_medios[i])
        valores.append(perdidos[i])

    # Evaluación de capacidades de Ethernet
    for i in range(len(ethernet)):
        res_ethernet.append((ethernet[i][0] >= umbral_ethernet[0]) and (ethernet[i][1] >= umbral_ethernet[1]))
        valores.append(ethernet[i][0])

    # Evaluación de potencias
    for j in range(len(redes)):
        for i in range(len(potencias)):
            valores.append(potencias[i][j])
            res_potencias.append(potencias[i][j] >= umbral_potencias[i])

    # Evaluación de capacidades WiFi
    for j in range(len(redes)):
        for i in range(len(wifi)):
            valores.append(wifi[i][j][0])
            res_wifi.append((wifi[i][j][0] >= umbral_wifi[j][0]) and (wifi[i][j][1] >= umbral_wifi[j][1]))

    # Impresión de los resultados de cumplimiento
    print("\n" + "=" * 80)
    print_with_color("** CUMPLIMIENTO DE PARAMETROS **", "green")

    # Evaluación de velocidad de descarga
    if res_velocidades[0]:
        print_with_color('Velocidad descarga: SI CUMPLE', 'green')
        base.append('Si cumple')
    else:
        print_with_color('Velocidad descarga: NO CUMPLE', 'red')
        base.append('No cumple')

    # Evaluación de velocidad de carga
    if res_velocidades[1]:
        print_with_color('Velocidad carga: SI CUMPLE', 'green')
        base.append('Si cumple')
    else:
        print_with_color('Velocidad carga: NO CUMPLE', 'red')
        base.append('No cumple')

    # Evaluación de latencias, jitter y paquetes perdidos
    for i in range(3):
        if res_tiempos[i]:
            print_with_color(f'Latencia {i + 1}: SI CUMPLE', 'green')
            base.append('Si cumple')
        else:
            print_with_color(f'Latencia {i + 1}: NO CUMPLE', 'red')
            base.append('No cumple')
        if res_jitter[i]:
            print_with_color(f'Jitter {i + 1}: SI CUMPLE', 'green')
            base.append('Si cumple')
        else:
            print_with_color(f'Jitter {i + 1}: NO CUMPLE', 'red')
            base.append('No cumple')
        if res_perdidos[i]:
            print_with_color(f'Perdidos {i + 1}: SI CUMPLE', 'green')
            base.append('Si cumple')
        else:
            print_with_color(f'Perdidos {i + 1}: NO CUMPLE', 'red')
            base.append('No cumple')

    # Evaluación de capacidades de Ethernet
    for i in range(len(res_ethernet)):
        if res_ethernet[i]:
            print_with_color(f'Capacidad ethernet {i + 1}: SI CUMPLE', 'green')
            base.append('Si cumple')
        else:
            print_with_color(f'Capacidad ethernet {i + 1}: NO CUMPLE', 'red')
            base.append('No cumple')

    # Evaluación de potencias
    for i in range(len(res_potencias)):
        parametro = 'cerca' if i % 3 == 0 else 'medio' if i % 3 == 1 else 'lejos'
        if res_potencias[i]:
            print_with_color(f'Potencia {redes[i // 3]} {parametro}: SI CUMPLE', 'green')
            base.append('Si cumple')
        else:
            print_with_color(f'Potencia {redes[i // 3]} {parametro}: NO CUMPLE', 'red')
            base.append('No cumple')

    # Evaluación de capacidades WiFi
    for i in range(len(res_wifi)):
        parametro = 'cerca' if i % 3 == 0 else 'medio' if i % 3 == 1 else 'lejos'
        if res_wifi[i]:
            print_with_color(f'Capacidad {redes[i // 3]} {parametro}: SI CUMPLE', 'green')
            base.append('Si cumple')
        else:
            print_with_color(f'Capacidad {redes[i // 3]} {parametro}: NO CUMPLE', 'red')
            base.append('No cumple')

    # Compromiso de los resultados en la base de datos
    if commit:
        commit_base(base, valores)

def present_results(redes, potencias, velocidades, tiempos, perdidos, jitter, n_packets, ethernet, wifi):
    """
    Imprime todos los resultados obtenidos de las diferentes pruebas realizadas

    Args:
        redes (list): Lista de nombres de redes pertenecientes al router evaluado.
        potencias (list): Lista de listas que contienen las potencias medidas de las redes.
        velocidades (list): Lista de velocidades de descarga y carga medidas.
        tiempos_medios (list): Lista de latencias medidas a varios servidores.
        jitter_medios (list): Lista de valores de jitter medidos a varios servidores.
        perdidos (list): Lista de valores de paquetes perdidos a varios servidores.
        ethernet (list): Lista de listas que contienen las capacidades de los puertos Ethernet.
        wifi (list): Lista de listas que contienen las capacidades WiFi medidas.

    Returns:
        None
    """

    print("\n" + "="*80)
    print_with_color("** RESULTADOS DE PRUEBAS **", "green")
    print("="*80)
    res_potencias = []
    res_velocidades = []
    tiempos_medios = []
    jitter_medios = []
    res_perdidos = []
    res_ethernet = []
    res_wifi = []

    # Velocidad de conexión
    print("\n" + "-"*80)
    print_with_color("VELOCIDAD DEL INTERNET", "blue")
    print("-"*80)
    print(f"Velocidad de descarga: {velocidades[0]:.2f} Mbps")
    print(f"Velocidad de carga: {velocidades[1]:.2f} Mbps")
    res_velocidades.append(round(velocidades[0], 4))
    res_velocidades.append(round(velocidades[1], 4))

    # Latencia y jitter
    for i in range(3):
        print("\n" + "-"*80)
        print_with_color(f"PRUEBA DE LATENCIA {i + 1}", "blue")
        print("-"*80)
        ping_promedio = sum(tiempos[i]) / len(tiempos[i]) * 1000
        jitter_promedio = sum(jitter[i]) / len(jitter[i]) * 1000
        print(f"Paquetes totales: {n_packets}")
        print(f"Paquetes perdidos: {perdidos[i]} = {perdidos[i] / n_packets * 100:.4f} %")
        print(f"Ping máximo: {max(tiempos[i]) * 1000:.2f} ms")
        print(f"Ping mínimo: {min(tiempos[i]) * 1000:.2f} ms")
        print(f"Ping promedio: {ping_promedio:.2f} ms \n")
        print(f"Jitter máximo: {max(jitter[i]) * 1000:.2f} ms")
        print(f"Jitter mínimo: {min(jitter[i]) * 1000:.2f} ms")
        print(f"Jitter promedio: {jitter_promedio:.2f} ms")
        res_perdidos.append(round((perdidos[i] / n_packets * 100), 4))
        tiempos_medios.append(round(ping_promedio, 4))
        jitter_medios.append(round(jitter_promedio, 4))

    # Capacidad de los puertos ethernet
    for i in range(len(ethernet)):
        print("\n" + "-"*80)
        print_with_color(f"CAPACIDAD DEL PUERTO ETHERNET {i + 1}", "blue")
        print("-"*80)

        print(f"Ancho de banda enviado: {ethernet[i]['end']['sum_sent']['bits_per_second'] / 1e6:.2f} Mbps")
        print(f"Ancho de banda recibido: {ethernet[i]['end']['sum_received']['bits_per_second'] / 1e6:.2f} Mbps")
        res_ethernet.append([round((ethernet[i]['end']['sum_sent']['bits_per_second'] / 1e6), 4),
                             round((ethernet[i]['end']['sum_received']['bits_per_second'] / 1e6), 4)])

    # Pruebas wifi
    for j in range(len(wifi)):
        res_potenciast = []
        res_wifit = []
        print("\n" + "-"*80)
        print_with_color(f"PRUEBA DE Wifi #{j + 1}", "blue")
        print("-"*80)
        
        # Potencia de la señal
        print_with_color("POTENCIA", "blue")
        for i in range(len(redes)):
            promedio = int(sum(potencias[j][i]) / len(potencias[j][i]))
            print(f"Valores medidos en {redes[i]}: ", potencias[j][i])
            print(f"Máximo: {max(potencias[j][i])} dBm")
            print(f"Mínimo: {min(potencias[j][i])} dBm")
            print(f"Promedio: {promedio} dBm")
            res_potenciast.append(round(promedio, 4))
        
        for i in range(len(wifi[j])):
            print_with_color(f"CAPACIDAD DE LA RED: {redes[i]}", "blue")
            print(f"Ancho de banda enviado: {wifi[j][i]['end']['sum_sent']['bits_per_second'] / 1e6:.2f} Mbps")
            print(f"Ancho de banda recibido: {wifi[j][i]['end']['sum_received']['bits_per_second'] / 1e6:.2f} Mbps")
            res_wifit.append([round((wifi[j][i]['end']['sum_sent']['bits_per_second'] / 1e6), 4),
                              round((wifi[j][i]['end']['sum_received']['bits_per_second'] / 1e6), 4)])
        res_potencias.append(res_potenciast)
        res_wifi.append(res_wifit)

    print("\n" + "="*80)
    print_with_color("FIN DE LOS RESULTADOS", "green")
    print("="*80)

    umbrales(redes, res_potencias, res_velocidades, tiempos_medios, jitter_medios, res_perdidos, res_ethernet, res_wifi)

def get_RSSI(redes, n_pruebas):
    """
    Obtiene la medición de la potencia de señal recibida (RSSI) de las redes indicadas

    Args:
        redes (list): Lista de nombres de redes pertenecientes al router evaluado.
        n_pruebas (int): Número de mediciones que se van a realizar

    Returns:
        potencias(list): Lista de listas que contiene todas las mediciones de potencia en dBm de las redes indicadas
    """
    print('Midiendo la potencia del Wifi')
    potencias = []
    
    # Inicializar la lista de potencias para cada red
    for i in range(len(redes)):
        red = []
        potencias.append(red)
    
    # Realizar las mediciones
    for i in range(n_pruebas):
        iface.scan()  # Iniciar el escaneo
        time.sleep(8)  # Esperar 8 segundos para completar el escaneo
        
        print("-"*13)
        print('Medicion:', i + 1)
        print("-"*13)
        
        scan_results = iface.scan_results()  # Obtener los resultados del escaneo
        for network in scan_results:
            if network.ssid in redes:  # Verificar si el SSID está en la lista de redes
                for j in range(len(redes)):
                    if network.ssid == redes[j] and len(potencias[j]) < i + 1:
                        potencias[j].append(network.signal)  # Añadir la potencia de señal
                        print(f"SSID: {network.ssid}, Potencia de la señal: {network.signal} dBm")
        
        # Añadir -96 dBm si la red no se encontró
        for k in range(len(redes)):
            if len(potencias[k]) < i + 1:
                potencias[k].append(-96)
    
    return potencias

def test_internet_speed():
    """
    Realiza un test de velocidad de la conexión a internet

    Args:
        None

    Returns:
        download_speed (float) Número que contiene la velocidad de descarga medida en Mbps
        upload_speed (float) Número que contiene la velocidad de carga medida en Mbps
    """
    try:
        st = speedtest.Speedtest()
        print("Probando velocidad del internet...")
        download_speed = st.download() / 1000000  # Convertir a Mbps
        upload_speed = st.upload() / 1000000  # Convertir a Mbps
        print("Prueba finalizada")

    except speedtest.SpeedtestException as e:   
        print("An error occurred during the speed test:", str(e)) 
        download_speed = 0
        upload_speed = 0

    return [download_speed, upload_speed]

def latencia(duracion):
    """
    Mide el retardo, jitter y paquetes perdidos entre la máquina y tres servidores diferentes, uno interno y dos externos

    Args:
        duracion(int): Tiempo en segundos que van a durar las pruebas realizadas

    Returns:
        tiempos(list): Lista de listas que contiene todos los retardos medidos hacia los tres servidores
        perdidos(list): Lista que contiene el número de paquetes perdidos hacia cada uno de los servidores
        jitter(list): Lista que contiene todos los valores de jitter medidos hacia los tres servidores
        n_packets(int): Número total de paquetes enviados hacia cada servidor

    """
    print('Midiendo latencia...')
    n_packets = 0
    tiempos = []
    perdidos = []
    jitter = []
    
    # Inicializar listas para tiempos, paquetes perdidos y jitter
    for i in range(3):
        tiempo = []
        perdido = 0
        jitt = []
        jitter.append(jitt)
        tiempos.append(tiempo)
        perdidos.append(perdido)
    
    inicio = time.time()
    final = 0
    
    # Medir latencia
    while (final - inicio) < duracion:
        n_packets += 1
        if (n_packets) % 100 == 0:
            print('Paquetes enviados: {:d}    Tiempo transcurrido: {:.2f} s'.format(n_packets, final - inicio))
        
        response = [0, 0, 0]
        response[0] = ping('1.1.1.1', timeout=1)  # Medir latencia a 1.1.1.1
        response[1] = ping('8.8.8.8', timeout=1)  # Medir latencia a 8.8.8.8
        response[2] = ping('66.231.74.241', timeout=1)  # Medir latencia a 66.231.74.241
        
        # Almacenar los tiempos de respuesta y contar paquetes perdidos
        for j in range(3):
            if response[j] is None:
                perdidos[j] += 1
            else:
                tiempos[j].append(response[j])
        
        final = time.time()
    
    # Calcular jitter
    for i in range(3):
        for j in range(1, len(tiempos[i])):
            jitter[i].append(abs(tiempos[i][j] - tiempos[i][j - 1]))
    
    return tiempos, perdidos, jitter, n_packets

class IperfError(Exception):
    """Raised when iperf execution fails"""

def run_iperf3_client(server_ip, tiempo, cliente, **kwargs):    
    """
    Ejecuta el programa iperf3 para medir la capacidad de los puertos ehternet y las redes wifi de los routers
    
    Args:
        server_ip(string): Cadena que contiene la ip del servidor iperf3 al que se va a conectar
        tiempo(int): Tiempo en segundos que va a durar la prueba
        cliente(string): Cadena que contiene la ip de la interfaz por la cuál se van a realizar las pruebas

    Returns:
        iperf3(json): JSON que contiene todas las mediciones realizadas

    """
    
    # Establece la duración de la prueba en segundos
    t = '-t' + str(tiempo)
    
    # Establece la dirección IP del cliente para la prueba
    b = '-B' + str(cliente)
    
    # Crea la lista de argumentos para el comando iperf3
    iperf3_args = ['-J', '-c', server_ip, b, '-P 5', t]  # -J para salida JSON, -c para cliente, -P 5 para múltiples flujos

    # Si se especifica la opción 'reverse', añade el argumento '-R' para hacer la prueba en reversa
    if kwargs.get('reverse', False):
        iperf3_args.append('-R')

    try:
        # Llama a iperf3 usando los argumentos especificados
        iperf3 = local['iperf3']
        return iperf3(*iperf3_args)  # Ejecuta el comando y devuelve los resultados
    except CommandNotFound as err:
        # Maneja el caso en que iperf3 no se encuentra en el sistema
        logging.error("%s not found", err.program)
        raise IperfError(err)  # Lanza un error personalizado
    except ProcessExecutionError as err:
        # Maneja el caso en que el comando falla durante la ejecución
        logging.error("%s exited with %d", err.argv[0], err.retcode)
        raise IperfError(err)  # Lanza un error personalizado

def connect_wifi(ssid, password):
    """
    Conecta a la computadora a una red wifi específica
    Args:
        ssid(string): Cadena que contiene el nombre de la red wifi a la que se quiere conectar
        password(string): Cadena que contiene la contraseña de la red wifi a la que se quiere conectar

    Returns:
        None
    """
    # Desconecta la interfaz de la red actual
    iface.disconnect()
    time.sleep(2)  # Espera 2 segundos para asegurarse de que se desconecte

    # Verifica si la interfaz está desconectada
    if iface.status() == const.IFACE_DISCONNECTED:
        # Crea un nuevo perfil de red para la conexión WiFi
        profile = pywifi.Profile()
        profile.ssid = ssid  # Establece el SSID de la red
        profile.auth = const.AUTH_ALG_OPEN  # Establece el algoritmo de autenticación
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # Establece el método de autenticación WPA2-PSK
        profile.cipher = const.CIPHER_TYPE_CCMP  # Establece el tipo de cifrado
        profile.key = password  # Establece la contraseña de la red

        # Añade el perfil de red a la interfaz
        temp_profile = iface.add_network_profile(profile)
        iface.connect(temp_profile)  # Intenta conectar usando el perfil
        time.sleep(12)  # Espera 12 segundos para que la conexión se establezca

        # Verifica el estado de la conexión
        if iface.status() == const.IFACE_CONNECTED:
            print(f"Conectado a la red: {ssid}")  # Mensaje de éxito
        else:
            print(f"Error al conectar a la red: {ssid}")  # Mensaje de error si no se pudo conectar
    else:
        print("Error: No se pudo desconectar de la red existente.")  # Mensaje si no se pudo desconectar de la red actual

#---------------------------------------------------------------------
#                       Inicio del programa
#---------------------------------------------------------------------


# Inicializa una variable de condición para controlar el bucle
condicion = 'si'  
# Establece la contraseña de la red WiFi
network_password = "prueba1234"  
# Crea una instancia de PyWiFi para manejar conexiones WiFi
wifii = pywifi.PyWiFi()  
# Selecciona la primera interfaz de red disponible
iface = wifii.interfaces()[0]  

# Bucle que se ejecuta hasta que la condición sea 'salir'
while condicion != 'salir':
    # Prueba la velocidad de la conexión a Internet y guarda los resultados
    velocidades = test_internet_speed()  

    # Define una lista de redes WiFi a evaluar
    redes = ['HUAWEI-Prueba', 'HUAWEI-Prueba_5G', 'HUAWEI-Prueba_5G_Wi-Fi5']  
    # Establece la duración de la prueba de latencia en segundos
    tiempo_ping = 300
    # Realiza pruebas de latencia y obtiene tiempos, paquetes perdidos y jitter
    tiempos, perdidos, jitter, n_packets = latencia(tiempo_ping)  

    ethernet = []  
    # Establece la dirección IP del servidor iperf3
    server_ip = '192.168.3.3'  
    print('Probando la capacidad del puerto ethernet')  
    # Establece la duración de la prueba de iperf3 para la conexión Ethernet
    tiempo_iperf1 = 60
    # Establece la dirección IP de la interfaz Ethernet
    ethernetip = '192.168.3.2'  
    # Realiza dos pruebas en el puerto Ethernet
    for i in range(2):
        print('Puerto ethernet', i + 1)  # Indica el número del puerto que se está probando
        # Llama a la función iperf3 y guarda el resultado
        result = run_iperf3_client(server_ip, tiempo_iperf1, ethernetip)  
        # Carga el resultado en formato JSON
        result_json = json.loads(result)  
        ethernet.append(result_json)  # Guarda los resultados de las pruebas Ethernet
        time.sleep(1)  # Espera un segundo entre pruebas

    wifi = []  # Lista para almacenar resultados de pruebas WiFi
    potencias = []  # Lista para almacenar potencias de señal
    tiempo_iperf2 = 120  # Establece la duración de la prueba de iperf3 para la conexión WiFi
    wifiip = '192.168.3.5'  # Establece la dirección IP de la interfaz WiFi
    pruebas_wifi = 3  # Establece el número de pruebas WiFi a realizar
    n_muestras = 15  # Número de muestras para la potencia de señal

    # Realiza pruebas WiFi según el número especificado
    for k in range(pruebas_wifi):
        if k > 0:
            input("Presione enter para realizar la siguiente prueba")  # Espera al usuario antes de continuar
        print("-" * 20)  # Separador visual
        print('Prueba de wifi #', k + 1)  # Indica el número de prueba de WiFi
        print("-" * 20)
        print('Probando la capacidad del Wifi')  # Mensaje informativo

        wifia = []  # Lista para almacenar resultados de pruebas WiFi en la iteración actual
        # Conecta y prueba cada red en la lista de redes
        for i in range(len(redes)):
            connect_wifi(redes[i], network_password)  # Conecta a la red WiFi
            # Llama a la función iperf3 y guarda el resultado
            result = run_iperf3_client(server_ip, tiempo_iperf2, wifiip)  
            result_json = json.loads(result)  # Carga el resultado en formato JSON
            wifia.append(result_json)  # Guarda los resultados de las pruebas WiFi
            time.sleep(2)  # Espera 2 segundos entre pruebas

        # Obtiene la potencia de la señal WiFi para cada red
        potencias.append(get_RSSI(redes, n_muestras))  
        wifi.append(wifia)  # Guarda los resultados de las pruebas WiFi

    # Presenta todos los resultados recopilados
    present_results(redes, potencias, velocidades, tiempos, perdidos, jitter, n_packets, ethernet, wifi)  
    # Pregunta al usuario si desea realizar otra prueba o salir
    condicion = input('Presione Enter para probar el siguiente router \nIngrese "salir" para finalizar \n').lower()  
