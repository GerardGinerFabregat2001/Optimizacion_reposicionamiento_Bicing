# Optimización de la distribución de las estaciones y de las bicicletas de *Bicing* Barcelona 

Este repositorio contiene el código principal utilizado en el Trabajo de Fin de Máster titulado **"Optimización de la distribución de las estaciones y de las bicicletas de *Bicing* Barcelona"**. El proyecto incluye análisis descriptivos y la creación y evaluación de modelos predictivos y de optimización para mejorar la distribución de bicicletas en el sistema *Bicing* de Barcelona.

## Contenido del repositorio

* **1-DATOS:** conjunto de datos utilizados para el análisis y desarrollo de modelos. También incluye los resultados obtenidos durante el mismo.
* **2-CODIGO:** *scripts* y *notebooks* utilizados en el proyecto.
* **3-CASO PRACTICO:** *scripts* y *notebooks* que el técnico de *Bicing* debería ejecutar para diseñar las rutas de reposicionamiento.
* **4-DIAGRAMAS:** contiene imágenes que se han utilizado en el trabajo para clarificar explicaciones del mismo.
* **README.md:** archivo con información general sobre el proyecto y el repositorio.

## Fuentes de datos

Este proyecto utiliza información obtenida de las siguientes fuentes:

* **Open Data Barcelona:** información sobre el uso y la disponibilidad de bicicletas en el sistema Bicing de Barcelona e información adicional como la población por distritos de la ciudad.
* **Geoportal de Barcelona:** información geográfica de la ciudad de Barcelona.
* **AEMET:** datos meteorológicos proporcionados por la Agencia Estatal de Meteorología.
* **Google Maps:** a través de la API de Google, se obtienen las distancias entre estaciones y el tiempo necesario para ir de una a otra con un vehículo.

## Objetivos del proyecto

* **Análisis descriptivo:** exploración de los datos para comprender patrones y tendencias en el uso del sistema *Bicing*. Asimismo, se evalúa la vulnerabilidad de los distritos en términos de accesibilidad con la creación de métricas.
* **Modelos predictivos:** desarrollo de modelos para predecir la saturación y desabastecimiento de bicicletas en diferentes estaciones y momentos.
* **Modelos de optimización:** implementación de algoritmos para diseñar rutas eficientes en función de las necesidades del sistema. El objetivo es minimizar la cantidad de situaciones en las que una estación se encuentra en riesgo de estar desabastecida o saturada de bicicletas.

## Requisitos

Para evitar posibles conflictos entre librerías y versiones de Python, se deben seguir los siguientes pasos:

* **Instalar las dependencias:** se deben instalar las versiones de las librerías especificadas en el archivo ```requirements.txt```.
* **Instalar versión de Python 3.11.x:** se ha utilizado la versión 3.11.9 y se recomienda utilizar cualquier versión 3.11.x, ya que algunas librerías utilizadas en este proyecto no han sido actualizadas para versiones posteriores de Python.



## Uso
Para utilizar este proyecto en tu máquina local, sigue los pasos listados a continuación:
1. Abre una terminal en tu PC.
2. Ejecuta el siguiente comando para clonar el repositorio.

```bash
git clone https://github.com/GerardGinerFabregat2001/Optimizacion_reposicionamiento_Bicing.git
```
3. Crea un entorno virtual (por ejemplo, usando venv):
```bash
py -3.11 -m venv env
```
4. Activa el entorno virtual:
    * En Windows:
    ```bash
    env\Scripts\activate
    ```
    * En macOS/Linux:
    ```bash
    source env/bin/activate
    ```
5. Instala las dependencias necesarias desde el archivo ```requirements.txt```:
```bash 
pip install -r Optimizacion_reposicionamiento_Bicing\requirements.txt
```

**Ejecución de código**

El proyecto está dividido en dos bloques principales:

1. **Replicación del análisis:**
para ello, se deben ejecutar los *notebooks* del directorio 2-CODIGO. Este directorio incluye los análisis descriptivos y las evaluaciones de los modelos predictivos y de optimización desarrollados, así como los procesos de creación de dichos modelos.


2. **Caso práctico:**
la mayor aportación de este proyecto recae en el uso de los modelos de predicción entrenados y la obtención de rutas a partir de las predicciones, utilizando el algoritmo de optimización seleccionado. En el directorio 3-CASO PRACTICO, se incluyen únicamente los *scripts* y *notebooks* necesarios para ello, junto con los resultados obtenidos para un caso concreto.

## Conclusiones
Los resultados reflejan que es necesario realizar un seguimiento contínuo en el servicio y que es posible mejorar la satisfacción de los usuarios a partir del reposicionamiento proactivo de bicicletas, ya que reduce los problemas de saturación y desabastecimiento de bicicletas que sufren ciertas estaciones en momentos puntuales.

## Autor
Este proyecto ha sido desarrollado por Gerard Giner Fabregat como parte de su Trabajo de Fin de Máster, y pueden contactar con él a través de [Linkedin](https://es.linkedin.com/in/gerard-giner-fabregat-8bbb7231a).
