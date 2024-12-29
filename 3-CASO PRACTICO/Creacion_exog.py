import pandas as pd
from astral.sun import sun
from astral import LocationInfo
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.compose import make_column_selector
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import FunctionTransformer

# Codificación cíclica de las variables de calendario y luz solar
# ==============================================================================
def codificacion_ciclica(datos: pd.Series, longitud_ciclo: int) -> pd.DataFrame:
    """
    Codifica una variable cíclica con dos nuevas variables: seno y coseno.
    Se asume que el valor mínimo de la variable es 0. El valor máximo de la
    variable se pasa como argumento.
      
    Parameters
    ----------
    datos : pd.Series
        Serie con la variable a codificar.
    longitud_ciclo : int
        La longitud del ciclo. Por ejemplo, 12 para meses, 24 para horas, etc.
        Este valor se utiliza para calcular el ángulo del seno y coseno.

    Returns
    -------
    resultado : pd.DataFrame
        Dataframe con las dos nuevas características: seno y coseno.

    """

    seno = np.sin(2 * np.pi * datos/longitud_ciclo)
    coseno = np.cos(2 * np.pi * datos/longitud_ciclo)
    resultado =  pd.DataFrame({
                  f"{datos.name}_seno": seno,
                  f"{datos.name}_coseno": coseno
              })

    return resultado
    
def calculo_variables_exogenas(datos):

    # Definir los días festivos de 2022-2023
    dias_festivos = pd.to_datetime([
        '2022-01-01',  # Año Nuevo
        '2022-01-06',  # Reyes Magos
        '2022-04-15',  # Viernes Santo
        '2022-04-18',  # Lunes de Pascua
        '2022-06-06',  # Lunes de Pascua Granada
        '2022-06-24',  # Sant Joan
        '2022-08-15',  # La Asunción
        '2022-09-24',  # La Mercè
        '2022-09-26',  # Fiesta local
        '2022-10-12',  # Fiesta Nacional de España
        '2022-11-01',  # Día de Todos los Santos
        '2022-12-06',  # La Constitución
        '2022-12-08',  # Inmaculada Concepción
        '2022-12-26',  # San Esteban
        '2023-01-01',  # Año Nuevo
        '2023-01-06',  # Reyes Magos
        '2023-04-07',  # Viernes Santo
        '2023-04-10',  # Lunes de Pascua
        '2023-05-01',  # Día del Trabajo
        '2023-06-05',  # Lunes de Pascua Granada
        '2023-06-24',  # Sant Joan
        '2023-08-15',  # La Asunción
        '2023-09-11',  # Diada (Fiesta Nacional de Catalunya)
        '2023-09-25',  # Día de la Mercè
        '2023-10-12',  # Fiesta Nacional de España
        '2023-11-01',  # Día de Todos los Santos
        '2023-12-06',  # Día de la Constitución
        '2023-12-08',  # Día de la Purísima
        '2023-12-25',  # Navidad
        '2023-12-26'   # Sant Esteve
    ])
    # Asegurarse de que el índice es de tipo datetime (si no lo es ya)
    indice = pd.to_datetime(datos.index)
    
    # Crear las variables
    datos['HORA'] = indice.hour
    datos['DIA'] = indice.dayofweek + 1
    datos['SEMANA'] = indice.isocalendar().week
    datos['MES'] = indice.month

    dias_festivos_horarios = pd.date_range(start=dias_festivos.min(), end=dias_festivos.max(), freq='h')
    dias_festivos_horarios = dias_festivos_horarios[dias_festivos_horarios.normalize().isin(dias_festivos)]
    datos['FESTIVO'] = indice.isin(dias_festivos_horarios).astype(int)

    # Variables basadas en el calendario
    # ==============================================================================
    variables_calendario = pd.DataFrame(index=indice)
    variables_calendario['mes'] = variables_calendario.index.month
    variables_calendario['semana_anyo'] = variables_calendario.index.isocalendar().week
    variables_calendario['dia_semana'] = variables_calendario.index.day_of_week + 1
    variables_calendario['hora_dia'] = variables_calendario.index.hour + 1
    
    # Variables basadas en la luz solar (Adaptado para Barcelona)
    # ==============================================================================
    location = LocationInfo(
        name      = 'Barcelona',
        region    = 'Spain',
        timezone  = 'Europe/Madrid',  # Zona horaria de Barcelona
        latitude  = 41.3851,          # Latitud de Barcelona
        longitude = 2.1734            # Longitud de Barcelona
    )
    
    hora_amanecer = [
        sun(location.observer, date=date, tzinfo=location.timezone)['sunrise'].hour
        for date in indice
    ]
    hora_anochecer = [
        sun(location.observer, date=date, tzinfo=location.timezone)['sunset'].hour
        for date in indice
    ]
    variables_solares = pd.DataFrame({
                             'hora_amanecer': hora_amanecer,
                             'hora_anochecer': hora_anochecer}, 
                             index = indice
                         )
    variables_solares['horas_luz_solar'] = (
        variables_solares['hora_anochecer'] - variables_solares['hora_amanecer']
    )
    variables_solares["es_de_dia"] = np.where(
        (indice.hour >= variables_solares["hora_amanecer"])
        & (indice.hour < variables_solares["hora_anochecer"]),
        1,
        0,
    )
    
    # Variables basadas en festivos
    # ==============================================================================
    variables_festivos = datos[['FESTIVO']].astype(int)
    variables_festivos['festivo_dia_anterior'] = variables_festivos['FESTIVO'].shift(24)
    variables_festivos['festivo_dia_siguiente'] = variables_festivos['FESTIVO'].shift(-24)
    
    # Merge all exogenous variables
    # ==============================================================================
    variables_exogenas = pd.concat([
        variables_calendario,
        variables_solares,
        variables_festivos
    ], axis=1)


    mes_encoded = codificacion_ciclica(variables_exogenas['mes'], longitud_ciclo=12)
    semana_anyo_encoded = codificacion_ciclica(variables_exogenas['semana_anyo'], longitud_ciclo=52)
    dia_semana_encoded = codificacion_ciclica(variables_exogenas['dia_semana'], longitud_ciclo=7)
    hora_dia_encoded = codificacion_ciclica(variables_exogenas['hora_dia'], longitud_ciclo=24)
    hora_amanecer_encoded = codificacion_ciclica(variables_exogenas['hora_amanecer'], longitud_ciclo=24)
    hora_anochecer_encoded = codificacion_ciclica(variables_exogenas['hora_anochecer'], longitud_ciclo=24)
    
    variables_ciclicas = pd.concat([
                                mes_encoded,
                                semana_anyo_encoded,
                                dia_semana_encoded,
                                hora_dia_encoded,
                                hora_amanecer_encoded,
                                hora_anochecer_encoded
                            ], axis=1)  
    
    variables_exogenas = pd.concat([variables_exogenas, variables_ciclicas], axis=1)

    # Interacción entre variables exógenas
    # ==============================================================================
    transformer_poly = PolynomialFeatures(
        degree           = 2,
        interaction_only = True,
        include_bias     = False
    ).set_output(transform="pandas")
    
    poly_cols = [
        'mes_seno',
        'mes_coseno',
        'semana_anyo_seno',
        'semana_anyo_coseno',
        'dia_semana_seno',
        'dia_semana_coseno',
        'hora_dia_seno',
        'hora_dia_coseno',
        'hora_amanecer_seno',
        'hora_amanecer_coseno',
        'hora_anochecer_seno',
        'hora_anochecer_coseno',
        'horas_luz_solar',
        'es_de_dia',
        'festivo_dia_anterior',
        'festivo_dia_siguiente',
        'FESTIVO'
    ]
    
    variables_poly = transformer_poly.fit_transform(variables_exogenas[poly_cols].dropna())
    variables_poly = variables_poly.drop(columns=poly_cols)
    variables_poly.columns = [f"poly_{col}" for col in variables_poly.columns]
    variables_poly.columns = variables_poly.columns.str.replace(" ", "__")
    variables_exogenas = pd.concat([variables_exogenas, variables_poly], axis=1)

    return variables_exogenas
