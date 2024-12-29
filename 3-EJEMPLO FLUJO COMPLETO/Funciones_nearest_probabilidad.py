import pandas as pd
import math
import plotly.graph_objects as go
import random 
from plotly.subplots import make_subplots

#OPTIMIZACIÓN
def funcion_objetivo(prediccion, capacidad_dict, limite_inferior=1, limite_superior=3/4):
    """
    Calcula la cantidad de horas en las que las estaciones están en riesgo de quedarse vacías
    o llenas en función de las predicciones y la capacidad de cada estación.

    Parámetros:
    - prediccion (pd.DataFrame): DataFrame con las predicciones de ocupación para cada estación (columnas) en diferentes horas (filas).
    - capacidad_dict (dict): Diccionario con las capacidades de cada estación, donde las claves son los nombres de las estaciones.
    - limite_inferior (int, opcional): Valor mínimo para considerar que una estación está en riesgo de quedarse vacía. Por defecto es 1.
    - limite_superior (float, opcional): Proporción máxima de la capacidad de una estación antes de considerarla llena. Por defecto es 3/4 (75%).

    Retorna:
    - suma (int): Número total de horas en las que las estaciones están en riesgo de quedarse vacías o llenas.

    El resultado se imprime en formato amigable con punto como separador de miles.
    """
    suma = 0
    
    for station in prediccion.columns:
        capacidad_estacion = capacidad_dict.get(station, 0)
        if capacidad_estacion == 0:
            print(f'Se desconoce la capacidad de la estación {station}')
            continue  

        limite_superior_estacion = int(limite_superior * capacidad_estacion)
        suma += ((prediccion[station] <= limite_inferior) | (prediccion[station] >= limite_superior_estacion)).sum()

    formatted_suma = f"{suma:,.0f}".replace(",", ".")
    print(f'La cantidad de horas con estaciones en riesgo de estar desabastecidas o saturadas es: {formatted_suma}.')

    return suma


def verificar_restriccion(j, t, restriccion):
    """
    Verifica si una estación está restringida para su visita en un tiempo dado
    """
    iteracion = restriccion[(restriccion['tiempo visita'] >= t - 60) & (restriccion['tiempo visita'] <= t + 60)]
    return any(j == row['visita'] for _, row in iteracion.iterrows())

def seleccion_top5(lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena):
    """"
    Selecciona las 2 O 5 estaciones más cercanas (menores tiempos) de las listas de estaciones vacías y llenas.
    """
    # Ordenar por tiempos y seleccionar los 2 o 5 menores para estaciones vacías (ajustar el parámetro)
    top_5_vacías = sorted(zip(lista_tiempos_vacía, lista_estaciones_vacía))[:2] 
    lista_tiempos_vacía_top_5, lista_estaciones_vacía_top_5 = zip(*top_5_vacías) if top_5_vacías else ([], [])
    # Ordenar por tiempos y seleccionar los 2 o 5 menores para estaciones llenas
    top_5_llenas = sorted(zip(lista_tiempos_llena, lista_estaciones_llena))[:2]
    lista_tiempos_llena_top_5, lista_estaciones_llena_top_5 = zip(*top_5_llenas) if top_5_llenas else ([], [])
    
    return lista_tiempos_vacía_top_5, lista_estaciones_vacía_top_5, lista_tiempos_llena_top_5, lista_estaciones_llena_top_5

def asignar_probabilidades(lista_tiempos_vacía_top_5, lista_estaciones_vacía_top_5, lista_tiempos_llena_top_5, lista_estaciones_llena_top_5):
    """
    Asigna probabilidades a las estaciones seleccionadas (vacías y llenas) según su orden (más cercanas tienen mayor probabilidad).
    """
    n_vacías = len(lista_tiempos_vacía_top_5)
    n_llenas = len(lista_tiempos_llena_top_5)
    
    pesos_vacías = list(range(n_vacías, 0, -1)) 
    pesos_llenas = list(range(n_llenas, 0, -1)) 
    
    probabilidades_vacías = [peso / sum(pesos_vacías) for peso in pesos_vacías] if pesos_vacías else []
    probabilidades_llenas = [peso / sum(pesos_llenas) for peso in pesos_llenas] if pesos_llenas else []
    
    estaciones_vacías_prob = list(zip(lista_estaciones_vacía_top_5, probabilidades_vacías))
    estaciones_llenas_prob = list(zip(lista_estaciones_llena_top_5, probabilidades_llenas))
    
    return estaciones_vacías_prob, estaciones_llenas_prob

def simular_eleccion(estaciones_vacías_prob, estaciones_llenas_prob, lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena):
    """
    Simula la elección de una estación basada en las probabilidades,
    eligiendo primero entre vacías y llenas si ambas listas están disponibles,
    o priorizando la que no esté vacía.
    """
    if not estaciones_vacías_prob and not estaciones_llenas_prob:
        return None, None, None

    if not estaciones_vacías_prob:
        tipo_elegido = 'llena'
    elif not estaciones_llenas_prob:
        tipo_elegido = 'vacía'
    else:
        # Elegir entre vacías y llenas con igual probabilidad si ambas están disponibles
        tipo_elegido = random.choices(['vacía', 'llena'], weights=[0.5, 0.5])[0]

    if tipo_elegido == 'vacía':
        # Selección dentro de las estaciones vacías
        estaciones_vacías, probabilidades_vacías = zip(*estaciones_vacías_prob)
        estacion_vencedora = random.choices(estaciones_vacías, weights=probabilidades_vacías)[0]
        tiempo_vencedor = lista_tiempos_vacía[lista_estaciones_vacía.index(estacion_vencedora)]
    else:
        # Selección dentro de las estaciones llenas
        estaciones_llenas, probabilidades_llenas = zip(*estaciones_llenas_prob)
        estacion_vencedora = random.choices(estaciones_llenas, weights=probabilidades_llenas)[0]
        tiempo_vencedor = lista_tiempos_llena[lista_estaciones_llena.index(estacion_vencedora)]

    return estacion_vencedora, tiempo_vencedor, tipo_elegido




def encontrar_estaciones_cercanas(posicion, t, estaciones, capacidad, tiempos_viaje, prediccion, num_minutes, restriccion, posicion_inicial, limite_inferior, limite_superior):
    """Encuentra las estaciones más cercanas que se llenarán o quedarán vacías."""
    lista_tiempos_vacía = []
    lista_estaciones_vacía = []
    lista_tiempos_llena = []
    lista_estaciones_llena = []
    lista_tiempos_vacía_flexible = []
    lista_estaciones_vacía_flexible = []
    lista_tiempos_llena_flexible = []
    lista_estaciones_llena_flexible = []
    flexible_inferior = 2 
    flexible_superior = 2/3
    for j in estaciones:
        if verificar_restriccion(j, t, restriccion) or posicion == j:
            continue
        
        station_capacity = capacidad.loc[capacidad['Station'] == j, 'Capacidad'].values[0]
        tiempo = int(tiempos_viaje.loc[posicion, j])
        tiempo_inicio = t + tiempo
        tiempo_nueva_vuelta = tiempos_viaje.loc[j, posicion_inicial]
        
        if tiempo_inicio + 2 + tiempo_nueva_vuelta >= (num_minutes - 60):
            continue
        
        # Verificar estaciones que quedarán vacías
        if prediccion[j][math.ceil(tiempo_inicio / 60)] <= limite_inferior:
            lista_tiempos_vacía.append(tiempo)
            lista_estaciones_vacía.append(j)

        # Verificar estaciones que quedarán vacías
        if (prediccion[j][math.ceil(tiempo_inicio / 60)] <= flexible_inferior) & (prediccion[j][math.ceil(tiempo_inicio / 60)] > limite_inferior):
            lista_tiempos_vacía_flexible.append(tiempo)
            lista_estaciones_vacía_flexible.append(j)
        
        # Verificar estaciones que se llenarán
        if prediccion[j][math.ceil(tiempo_inicio / 60)] >= int(limite_superior * station_capacity):
            lista_tiempos_llena.append(tiempo)
            lista_estaciones_llena.append(j)

        # Verificar estaciones que se llenarán
        if (prediccion[j][math.ceil(tiempo_inicio / 60)] >= int(flexible_superior * station_capacity)) & (prediccion[j][math.ceil(tiempo_inicio / 60)] < int(limite_superior * station_capacity)):
            lista_tiempos_llena_flexible.append(tiempo)
            lista_estaciones_llena_flexible.append(j)

    if not lista_estaciones_vacía and not lista_estaciones_llena:
        # print('1')
        return  lista_tiempos_vacía_flexible, lista_estaciones_vacía_flexible, lista_tiempos_llena_flexible, lista_estaciones_llena_flexible
    elif not lista_estaciones_vacía:
        # print('2')
        return lista_tiempos_vacía_flexible, lista_estaciones_vacía_flexible, lista_tiempos_llena, lista_estaciones_llena
    elif not lista_estaciones_llena:
        #  print('3')
        return lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena_flexible, lista_estaciones_llena_flexible
    else:
        #  print('4')
        return lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena
   
def ejecución_simulación(lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena):
    """ 
    Ejecuta el flujo completo de selección de estaciones y simulación.
    """
    lista_tiempos_vacía_top_5, lista_estaciones_vacía_top_5, lista_tiempos_llena_top_5, lista_estaciones_llena_top_5 = seleccion_top5(
        lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena
    )

    estaciones_vacías_prob, estaciones_llenas_prob = asignar_probabilidades(
        lista_tiempos_vacía_top_5, lista_estaciones_vacía_top_5, lista_tiempos_llena_top_5, lista_estaciones_llena_top_5
    )

    estacion_vencedora, tiempo_vencedor, tipo_elegido = simular_eleccion(
        estaciones_vacías_prob, estaciones_llenas_prob, 
        lista_tiempos_vacía_top_5, lista_estaciones_vacía_top_5, 
        lista_tiempos_llena_top_5, lista_estaciones_llena_top_5
    )

    return estacion_vencedora, tiempo_vencedor, tipo_elegido


def procesar_estaciones(camion, lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena, capacidad, prediccion, tiempos_viaje, capacidad_camion, visitas_estaciones, tiempo_estaciones):
    """Procesa el envío de bicicletas a estaciones vacías o retiro de estaciones llenas."""
    estacion_vencedora, tiempo_vencedor, tipo_elegido = ejecución_simulación(lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena)
    posicion = camion["posicion"]
    bicicletas_camion = camion["bicicletas_camion"]
    t = camion["t"]

    if tipo_elegido == 'llena':
        station_capacity_retirar = capacidad.loc[capacidad['Station'] == posicion, 'Capacidad'].values[0]
        retirar = int(station_capacity_retirar / 3)
    if tipo_elegido == 'vacía':
        station_capacity_añadir = capacidad.loc[capacidad['Station'] == posicion, 'Capacidad'].values[0]
        añadir = int(station_capacity_añadir / 3)

    if tipo_elegido == 'llena' and bicicletas_camion + retirar <= capacidad_camion:
        realizar_retiro(camion, estacion_vencedora, retirar, tiempo_vencedor, prediccion, tiempos_viaje, capacidad, visitas_estaciones, tiempo_estaciones)
    elif tipo_elegido == 'vacía' and bicicletas_camion >= añadir:
        realizar_envio(camion, estacion_vencedora, añadir, tiempo_vencedor, prediccion, tiempos_viaje, capacidad, visitas_estaciones, tiempo_estaciones)
    elif tipo_elegido == "llena" and bicicletas_camion + retirar > capacidad_camion:
        if lista_estaciones_vacía:
            procesar_estaciones(camion, lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena, capacidad, prediccion, tiempos_viaje, capacidad_camion, visitas_estaciones, tiempo_estaciones)
        else: 
            manejar_fallo(camion, estacion_vencedora, tipo_elegido, tiempos_viaje, prediccion)
    elif tipo_elegido == 'vacía' and bicicletas_camion < añadir:
        if lista_estaciones_llena:
            procesar_estaciones(camion, lista_tiempos_vacía, lista_estaciones_vacía, lista_tiempos_llena, lista_estaciones_llena, capacidad, prediccion, tiempos_viaje, capacidad_camion, visitas_estaciones, tiempo_estaciones)
        else:
            manejar_fallo(camion, estacion_vencedora, tipo_elegido, tiempos_viaje, prediccion)
    else:
        manejar_fallo(camion, estacion_vencedora, tipo_elegido, tiempos_viaje, prediccion)

def realizar_retiro(camion, estacion, cantidad, distancia, prediccion, tiempos_viaje, capacidad, visitas_estaciones, tiempo_estaciones):
    """Actualiza datos tras el retiro de bicicletas."""
    visitas_estaciones.append(estacion)
    tiempo_estaciones.append(camion["t"]+distancia)
    actualizar_prediccion(prediccion, estacion, capacidad, cantidad, tiempo_actual=camion["t"] + distancia, sumar=False)
    actualizar_datos_camion(camion, estacion, distancia, cantidad, sumar=True, tiempos_viaje=tiempos_viaje)


def realizar_envio(camion, estacion, cantidad, distancia, prediccion, tiempos_viaje, capacidad, visitas_estaciones, tiempo_estaciones):
    """Actualiza datos tras el envío de bicicletas."""
    visitas_estaciones.append(estacion)
    tiempo_estaciones.append(camion["t"]+distancia)
    actualizar_prediccion(prediccion, estacion, capacidad, cantidad, tiempo_actual=camion["t"] + distancia, sumar=True)
    actualizar_datos_camion(camion, estacion, distancia, cantidad, sumar=False, tiempos_viaje=tiempos_viaje)


def manejar_fallo(camion, estacion_vencedora, tipo_elegido, tiempos_viaje, prediccion):
    """Maneja el caso donde no se puede realizar un envío ni un retiro."""
    actualizar_tiempo_camion(camion, prediccion, tiempos_viaje)


def actualizar_prediccion(prediccion, estacion, capacidad, cantidad, tiempo_actual, sumar=True):
    """Actualiza la predicción de disponibilidad en una estación."""
    station_capacity = capacidad.loc[capacidad['Station'] == estacion, 'Capacidad'].values[0]
    
    for k in range(math.ceil(tiempo_actual / 60), prediccion.shape[0]):
        if sumar:
            prediccion[estacion][k] = min(prediccion[estacion][k] + cantidad, station_capacity)
        else:
            prediccion[estacion][k] = max(prediccion[estacion][k] - cantidad, 0)


def actualizar_datos_camion(camion, estacion, distancia, cantidad, sumar, tiempos_viaje):
    """Actualiza los datos del camión tras realizar un envío o retiro."""
    camion["bicicletas_camion"] += cantidad if sumar else -cantidad
    camion["posicion"] = estacion
    camion["t"] += distancia + 2
    camion["tiempo visita estaciones"].append(camion["t"] - 2)
    camion["ruta"].append(estacion)
    camion["bicicletas_iteracion"].append(camion["bicicletas_camion"])
    camion["tiempo_vuelta"] = int(tiempos_viaje.loc[camion["posicion"], "1.0"])


def actualizar_tiempo_camion(camion, prediccion, tiempos_viaje):
    """Actualiza el tiempo del camión en caso de no realizar ninguna acción."""
    if math.ceil(camion["t"] / 60) == prediccion.shape[0] - 1:
        camion["tiempo_vuelta"] = 60
        camion["param"] = True
    else:
        camion["tiempo_vuelta"] = int(tiempos_viaje.loc[camion["posicion"], "1.0"])
    camion["t"] += 5

# GRÁFICO
def graficar_rutas_camiones(todas_localizaciones, colores=['red', 'green', 'blue'], zoom=10.75, ancho=500, alto=600):
    """
    Grafica las rutas de los camiones en un mapa usando Plotly.

    Args:
        todas_localizaciones (DataFrame): DataFrame con las columnas 'camion_id', 'lat', 'lon', y 'station_id'.
        colores (list): Lista de colores para cada camión. Se usará uno por cada camion_id único.
        zoom (float): Nivel de zoom inicial del mapa.
        ancho (int): Ancho de la figura.
        alto (int): Alto de la figura.

    Returns:
        plotly.graph_objects.Figure: Figura con subplots para las rutas de los camiones.
    """
    camiones_unicos = todas_localizaciones["camion_id"].unique()
    n_camiones = len(camiones_unicos)

    # Crear subplots, una columna por cada camión, especificando el tipo 'mapbox' para cada subplot
    fig = make_subplots(
        rows=1, 
        cols=n_camiones, 
        subplot_titles=[f"Ruta del camión {i+1}" for i in range(n_camiones)],
        horizontal_spacing=0.1,
        specs=[[{"type": "mapbox"} for _ in range(n_camiones)]]  
    )
    # Personalizar tamaño de fuente de los títulos de los subplots
    for i in range(n_camiones):
        fig.layout.annotations[i].update(font=dict(size=20))  


    for i, camion_id in enumerate(camiones_unicos):
        localizacion_camion = todas_localizaciones[todas_localizaciones["camion_id"] == camion_id]
        latitudes = localizacion_camion['lat'].tolist()
        longitudes = localizacion_camion['lon'].tolist()

        # Agregar puntos de las estaciones
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=longitudes,
            lat=latitudes,
            marker=dict(size=8, color=colores[i % len(colores)]),
            text=localizacion_camion['station_id'],
            name=f"Camión {i+1}",
            showlegend=False
        ), row=1, col=i + 1)

        # Agregar líneas entre las estaciones
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=longitudes + [longitudes[0]],  
            lat=latitudes + [latitudes[0]],
            line=dict(width=2, color=colores[i % len(colores)]),
            showlegend=False
        ), row=1, col=i + 1)

    # Configurar el diseño del mapa para todos los subplots
    fig.update_layout(
        width=ancho * n_camiones,  
        height=alto
    )

    # Configurar propiedades de mapbox
    for i in range(n_camiones):
        fig.update_layout(**{f"mapbox{i+1}": dict(
            style="carto-positron",
            center={
                "lat": todas_localizaciones['lat'].mean() + 0.008,
                "lon": todas_localizaciones['lon'].mean() + 0.008
            },
            zoom=zoom
        )})

    return fig

# LOCALIZACIÓN
def localizacion_segun_ruta(ruta, localizacion):
    """
    Filtra y organiza las coordenadas (latitud y longitud) de las estaciones que corresponden a una ruta específica,
    asegurando el orden de la ruta y eliminando estaciones sin datos de localización.
    """
    localizacion = localizacion.reset_index()
    localizacion = localizacion[['station_id', 'lat', 'lon']]
    localizacion['station_id'] = localizacion['station_id'].astype(str)
    localizacion = localizacion[localizacion['station_id'].isin(ruta)]

    ruta_df = pd.DataFrame({'station_id': ruta})

    localizacion = ruta_df.merge(localizacion, on='station_id', how='left')
    localizacion = localizacion.dropna(subset=['lat', 'lon'])
    localizacion = localizacion.reset_index(drop=True)

    return localizacion

# ANÁLISIS DESCRIPTIVO
def cantidad_estaciones(prediccion, capacidad_dict, limite_inferior=1, limite_superior=3/4):
    """
    Calcula las veces que cada estación estuvo vacía o llena en un período y
    genera un resumen.

    Parámetros:
    - prediccion (pd.DataFrame): DataFrame con las predicciones de ocupación para cada estación (columnas) en diferentes horas (filas).
    - capacidad_dict (dict): Diccionario con las capacidades de cada estación, donde las claves son los nombres de las estaciones.
    - limite_inferior (int, opcional): Valor mínimo para considerar que una estación está vacía. Por defecto es 1.
    - limite_superior (float, opcional): Proporción máxima de la capacidad de una estación antes de considerarla llena. Por defecto es 3/4 (75%).

    Retorna:
    - resumen (pd.DataFrame): DataFrame con estadísticas y valores binarios indicando si las estaciones estuvieron vacías o llenas.
    """
    vacios = []
    llenos = []

    for station in prediccion.columns:
        capacidad_estacion = capacidad_dict.get(station, 0)
        if capacidad_estacion == 0:
            print(f'Se desconoce la capacidad de la estación {station}')
            vacios.append(0)
            llenos.append(0)
            continue

        limite_superior_estacion = int(limite_superior * capacidad_estacion)

        suma_vacios = (prediccion[station] <= limite_inferior).sum()
        suma_llenos = (prediccion[station] >= limite_superior_estacion).sum()

        vacios.append(suma_vacios)
        llenos.append(suma_llenos)

    resumen = pd.DataFrame({
        'Station': prediccion.columns,
        'Veces vacío': vacios,
        'Veces lleno': llenos
    })

    resumen['Binaria vacío'] = (resumen['Veces vacío'] > 0).astype(int)
    resumen['Binaria lleno'] = (resumen['Veces lleno'] > 0).astype(int)
    resumen['Añadida'] = resumen['Binaria vacío'] + resumen['Binaria lleno']

    capacidad_df = pd.DataFrame.from_dict(capacidad_dict, orient='index', columns=['Capacidad']).reset_index()
    capacidad_df.rename(columns={'index': 'Station'}, inplace=True)
    resumen = resumen.merge(capacidad_df, on="Station", how="left")
    resumen = resumen[(resumen['Binaria vacío'] == 1) | (resumen['Binaria lleno'] == 1)]
    print(f'La cantidad de estaciones en riesgo de estar desabastecidas en algún momento del período son: {resumen["Binaria vacío"].sum()}')
    print(f'La cantidad de estaciones en riesgo de estar saturadas en algún momento del período son: {resumen["Binaria lleno"].sum()}')
    return resumen
