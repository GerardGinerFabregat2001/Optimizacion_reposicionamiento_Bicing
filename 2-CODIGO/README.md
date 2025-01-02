# Directorio 2-CODIGO

Este directorio contiene 4 carpetas:

## 1-TRATAMIENTO DE DATOS

Esta carpeta incluye los *notebooks* necesarios para transformar los datos originales provenientes de la carpeta 1-DATOS ORIGINALES en los datos limpios y estructurados que se almacenan en la carpeta 2-DATOS PROCESADOS.

## 2-ANALISIS DESCRIPTIVO
Esta carpeta contiene los *notebooks* utilizados para realizar análisis exploratorios y descriptivos de los datos procesados. 

* **Localización de estaciones:** visualización de la distribución geográfica de las estaciones.
* **Vulnerabilidad por distritos:** evaluación y representación de la vulnerabilidad de los distritos de la ciudad en términos de accesibilidad al sistema de bicicletas.
* **Patrones de desabastecimiento y saturación:** análisis de comportamiento de las estaciones, identificando tendencias y patrones mediante técnicas de *clustering*.

## 3-PREDICCION

Esta carpeta contiene los archivos creados para abordar la previsión de desabastecimiento y saturación de bicicletas en las estaciones, utilizando técnicas avanzadas de modelado predictivo. El flujo de trabajo está diseñado para evaluar, seleccionar y aplicar modelos que permitan anticipar patrones de uso.

En primer lugar, se han evaluado diversos enfoques de predicción. Como ejemplo, se muestra la creación de modelos predictivos para una de las estaciones de la ciudad, empleando diferentes técnicas como modelos SARIMA, *gradient boosting* y LSTM.

Tras identificar la técnica con mejor rendimiento, se crean los modelos para todas las estaciones de la ciudad mediante el archivo ```Creacion_modelos.ipynb```. Una vez entrenados, estos modelos pueden ejecutarse para obtener predicciones utilizando el archivo ```Ejecucion_modelos.ipynb```.

Además, para mejorar la precisión de las predicciones, los modelos incorporan variables exógenas. Estas variables se generan a través del archivo ```Creacion_exog.py```.

## 4-OPTIMIZACION

Para diseñar las rutas de reposicionamiento que deben seguir los trabajadores del servicio *Bicing*, se han evaluado y comparado dos algoritmos constructivos:

* **Nearest Neighbour:** diseña rutas basándose en la elección del punto más cercano y considerando la urgencia de visita, es decir, dando prioridad a aquellas estaciones en las que se prevé que no habrá bicicletas disponibles o que tendrán un exceso de ellas.
* **Nearest Neighbour con probabilidades:** introduce un componente probabilístico para diversificar las rutas y explorar soluciones alternativas.

Esta carpeta incluye:

* Las funciones necesarias para implementar ambos algoritmos, disponibles en los archivos ```.py```.
* Ejemplos prácticos para ejecutar estas funciones, proporcionados en los archivos ```.ipynb```.
