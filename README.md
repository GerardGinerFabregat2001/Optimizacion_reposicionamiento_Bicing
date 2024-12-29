# Optimización del reposicionamiento en el sistema *Bicing* de Barcelona

Este repositorio contiene el código principal utilizado en el Trabajo de Fin de Máster titulado "Optimización de la distribución de las estaciones y de las bicicletas de *Bicing* Barcelona". El proyecto abarca análisis descriptivos, técnicas predictivas y modelos de optimización para mejorar la distribución de bicicletas en el sistema *Bicing* de Barcelona.

## Contenido del repositorio

* **1-DATOS:** conjunto de datos utilizados para el análisis y desarrollo de modelos. También incluye los resultados obtenidos durante el mismo.
* **2-CODIGO:** *scripts* y *notebooks* que implementan los análisis y modelos desarrollados.
* **README.md:** archivo con información general sobre el proyecto y el repositorio.

## Fuentes de datos

Este proyecto utiliza información obtenida de las siguientes fuentes:

* **Open Data Barcelona:** información sobre el uso y la disponibilidad de bicicletas en el sistema Bicing de Barcelona e información adicional como la población por distritos de la ciudad.
* **Geoportal BCN:** información geográfica  del Ayuntamiento de Barcelona.
* **AEMET:** datos meteorológicos proporcionados por la Agencia Estatal de Meteorología.
* **Google Maps:** a través de la API de Google, se obtienen las distancias entre estaciones y el tiempo necesario para ir de una a otra con un vehículo.

## Estructura del proyecto

* **Análisis descriptivo:** exploración de los datos para comprender patrones y tendencias en el uso del sistema *Bicing*. Asismismo, se evalúa la vulnerabilidad de los distritos en términos de accesibilidad con la creación de métricas.
* **Técnicas predictivas:** desarrollo de modelos para predecir la demanda de bicicletas en diferentes estaciones y momentos.
* **Modelos de optimización:** implementación de algoritmos para diseñar rutas eficientes en función de las necesidades del sistema. El objetivo es minimizar la cantidad de situaciones en las que una estación se encuentra en riesgo de estar desabastecida o saturada de bicicletas.

## Requisitos

Para ejecutar correctamente este proyecto, es necesario tener instalado Python 3.x y varias librerías adicionales. Entre ellas, hay dos que requieren especial atención debido a sus versiones específicas:

* **Skforecast**: versión 0.13.0
* **Tensorflow**: versión 2.16.2

Además de estas dos, otras librerías generales como **pandas**, **numpy**, **scikit-learn**, **matplotlib**, y **scipy** son necesarias para tareas de análisis de datos, visualización y preprocesamiento.

<!-- Se recomienda crear un entorno virtual para gestionar las dependencias y garantizar que las versiones instaladas no entren en conflicto con otros proyectos:-->

## Uso

* Clona este repositorio en tu máquina local.

```bash
git clone https://github.com/GerardGinerFabregat2001/Optimizacion_reposicionamiento_Bicing.git
```
* Navega al directorio del proyecto.

* Accede al directorio 2-CODIGO y ejecuta los scripts o notebooks según el análisis o modelo que desees explorar.

## Autor
Este proyecto ha sido desarrollado por Gerard Giner Fabregat como parte de su Trabajo de Fin de Máster, y pueden contactar con él a través de [Linkedin](https://es.linkedin.com/in/gerard-giner-fabregat-8bbb7231a).
