# Directorio 3-CASO PRACTICO
Este directorio incluye todos los archivos necesarios para que un técnico del servicio *Bicing* pueda diseñar las rutas de reposicionamiento que deben seguir los trabajadores. Además, contiene un ejemplo práctico que muestra los resultados obtenidos para el día 5 de octubre de 2023, en el turno comprendido entre las 08:00 h y las 16:00 h.

## EJECUCIÓN

Los archivos necesarios para calcular las predicciones y generar las rutas son: 

* ```Calculo_prediccion.ipynb:``` *notebook* que calcula la predicción de cantidad de bicicletas de cada estación, utilizando modelos previamente entrenados.

* ```Calculo_rutas.ipynb:``` *notebook* que diseña las rutas de reposicionamiento basándose en las predicciones generadas.

* ```Creacion_exog.py:``` *script* encargado de crear las variables exógenas necesarias para mejorar la precisión de las predicciones.

* ```Funciones_nearest_probabilidad.py:``` contiene las funciones para implementar el algoritmo constructvo *Nearest Neighbour con probabilidades*.

## RESULTADOS

Los resultados obtenidos tras ejecutar los *notebooks* y *scripts* anteriores, se almacenan en los siguiente archivos:

* ```Predicciones.csv:``` archivo que contiene las previsiones de disponibilidad de bicicletas en cada estación durante el turno especificado. Este archivo es la salida de ```Calculo_prediccion.ipynb``` y se utiliza en ```Calculo_rutas.ipynb```.

* ```camion_i.csv:``` archivo que detalla las rutas asignadas al camión $i$, donde $i = 1, \ldots , n$, siendo $n$ el número total de camiones disponibles. Indica las estaciones a visitar, el momento de visita y la cantidad de bicicletas en el camión tras la visita. Estos archivos son la salida de ```Calculo_rutas.ipynb```.

