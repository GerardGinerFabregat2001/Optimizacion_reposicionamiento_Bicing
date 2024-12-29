import pandas as pd
import math
import plotly.graph_objects as go
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
    """Verifica si una estación está restringida en base al tiempo y visitas recientes."""
    iteracion = restriccion[(restriccion['tiempo visita'] >= t - 60) & (restriccion['tiempo visita'] <= t + 60)]
    return any(j == row['visita'] for _, row in iteracion.iterrows())


def encontrar_estaciones_cercanas(posicion, t, estaciones, capacidad, tiempos_viaje, prediccion, num_minutes, restriccion, posicion_inicial):
    """Encuentra las estaciones más cercanas que se llenarán o quedarán vacías."""
    closest_empty_station, closest_full_station = None, None
    min_distancia_empty, min_distancia_full = float('inf'), float('inf')
    
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
        if prediccion[j][math.ceil(tiempo_inicio / 60)] <= 1:
            if tiempo < min_distancia_empty:
                min_distancia_empty = tiempo
                closest_empty_station = j
        
        # Verificar estaciones que se llenarán
        if prediccion[j][math.ceil(tiempo_inicio / 60)] >= int(3 * station_capacity / 4):
            if tiempo < min_distancia_full:
                min_distancia_full = tiempo
                closest_full_station = j
    
    return closest_empty_station, min_distancia_empty, closest_full_station, min_distancia_full


def procesar_estaciones(camion, closest_empty_station, min_distancia_empty, closest_full_station, min_distancia_full, capacidad, prediccion, tiempos_viaje, capacidad_camion, visitas_estaciones, tiempo_estaciones):
    """Procesa el envío de bicicletas a estaciones vacías o retiro de estaciones llenas."""
    posicion = camion["posicion"]
    bicicletas_camion = camion["bicicletas_camion"]
    t = camion["t"]

    if closest_full_station:
        station_capacity_retirar = capacidad.loc[capacidad['Station'] == closest_full_station, 'Capacidad'].values[0]
        retirar = int(station_capacity_retirar / 3)
    if closest_empty_station:
        station_capacity_añadir = capacidad.loc[capacidad['Station'] == closest_empty_station, 'Capacidad'].values[0]
        añadir = int(station_capacity_añadir / 3)

    if closest_full_station and bicicletas_camion + retirar <= capacidad_camion:
        realizar_retiro(camion, closest_full_station, retirar, min_distancia_full, prediccion, tiempos_viaje, capacidad, visitas_estaciones, tiempo_estaciones)
    elif closest_empty_station and bicicletas_camion >= añadir:
        realizar_envio(camion, closest_empty_station, añadir, min_distancia_empty, prediccion, tiempos_viaje, capacidad, visitas_estaciones, tiempo_estaciones)
    else:
        manejar_fallo(camion, closest_empty_station, closest_full_station, tiempos_viaje, prediccion)

def realizar_retiro(camion, estacion, cantidad, distancia, prediccion, tiempos_viaje, capacidad,  visitas_estaciones, tiempo_estaciones):
    """Actualiza datos tras el retiro de bicicletas."""
    visitas_estaciones.append(estacion)
    tiempo_estaciones.append(camion["t"]+distancia)
    print(f"Camión {camion['id']}: la estación más cercana que se llenará es {estacion} y se visitará en {camion['t'] + distancia}."
          f" Se encuentra a una distancia de {distancia} minutos. Se retirarán {cantidad} bicicletas.")
    actualizar_prediccion(prediccion, estacion, capacidad, cantidad, tiempo_actual=camion["t"] + distancia, sumar=False)
    actualizar_datos_camion(camion, estacion, distancia, cantidad, sumar=True, tiempos_viaje=tiempos_viaje)


def realizar_envio(camion, estacion, cantidad, distancia, prediccion, tiempos_viaje, capacidad,  visitas_estaciones, tiempo_estaciones):
    """Actualiza datos tras el envío de bicicletas."""
    visitas_estaciones.append(estacion)
    tiempo_estaciones.append(camion["t"]+distancia)
    print(f"Camión {camion['id']}: la estación más cercana que se quedará vacía es {estacion} y se visitará en {camion['t'] + distancia}. "
          f" Se encuentra a una distancia de {distancia} minutos. Se añadirán {cantidad} bicicletas.")
    actualizar_prediccion(prediccion, estacion, capacidad, cantidad, tiempo_actual=camion["t"] + distancia, sumar=True)
    actualizar_datos_camion(camion, estacion, distancia, cantidad, sumar=False, tiempos_viaje=tiempos_viaje)


def manejar_fallo(camion, closest_empty_station, closest_full_station, tiempos_viaje, prediccion):
    """Maneja el caso donde no se puede realizar un envío ni un retiro."""
    if closest_full_station:
        print(f"Camión {camion['id']}: podría retirar bicicletas en {closest_full_station}, pero no tiene capacidad. No se puede realizar ninguna acción en {camion['t']}.")
    elif closest_empty_station:
        print(f"Camión {camion['id']}: podría añadir bicicletas en {closest_empty_station}, pero no tiene suficientes. No se puede realizar ninguna acción en {camion['t']}.")
    else:
        print(f"Camión {camion['id']}: no se encontraron estaciones llenas o vacías cercanas en tiempo {camion['t']}.")
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
    # Asegurarse de que 'station_id' sea una columna y no el índice
    localizacion = localizacion.reset_index()
    localizacion = localizacion[['station_id', 'lat', 'lon']]
    localizacion['station_id'] = localizacion['station_id'].astype(str)

    # Filtrar las estaciones presentes en la ruta
    localizacion = localizacion[localizacion['station_id'].isin(ruta)]

    # Crear un DataFrame basado en el orden de la ruta
    ruta_df = pd.DataFrame({'station_id': ruta})

    # Combinar para asegurar que el orden de la ruta se mantiene
    localizacion = ruta_df.merge(localizacion, on='station_id', how='left')

    # Eliminar filas con valores nulos en las coordenadas
    localizacion = localizacion.dropna(subset=['lat', 'lon'])

    # Resetear el índice para claridad
    localizacion = localizacion.reset_index(drop=True)

    return localizacion

# ANÁLISIS DESCRIPTIVO
def cantidad_estaciones(prediccion, capacidad_dict, limite_inferior=1, limite_superior=3/4):
    """
    Calcula las veces que cada estación estuvo vacía o llena en un período y
    genera un resumen con indicadores binarios y estadísticos.

    Parámetros:
    - prediccion (pd.DataFrame): DataFrame con las predicciones de ocupación para cada estación (columnas) en diferentes horas (filas).
    - capacidad_dict (dict): Diccionario con las capacidades de cada estación, donde las claves son los nombres de las estaciones.
    - limite_inferior (int, opcional): Valor mínimo para considerar que una estación está vacía. Por defecto es 1.
    - limite_superior (float, opcional): Proporción máxima de la capacidad de una estación antes de considerarla llena. Por defecto es 3/4 (75%).

    Retorna:
    - resumen (pd.DataFrame): DataFrame con estadísticas y valores binarios indicando si las estaciones estuvieron vacías o llenas,
      pero solo incluye las filas donde "Binaria vacío" = 1 o "Binaria lleno" = 1.
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
