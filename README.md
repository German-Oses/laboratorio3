# Laboratorio 3: aplicación inteligente adaptativa

**Integrantes:** German Oses, Joshua Villavicencio y Fernando Figueroa  
**Asignatura:** Ingeniería Web Avanzada, OII436-1  
**Fecha:** 9 de noviembre de 2026  
**Repositorio:** https://github.com/German-Oses/laboratorio3

## Descripción del trabajo

La aplicación recomienda recursos de aprendizaje a partir de los intereses de cada
usuario. Por ejemplo, alguien que declara interés en Python y datos recibe recursos
distintos de quien busca contenidos sobre Angular. Además, cuando el usuario marca
un recurso con «Me interesa», el programa incorpora esa preferencia a su perfil y
vuelve a calcular las recomendaciones en la misma sesión.

El trabajo se desarrolló sobre el material base del laboratorio. Las cuatro
funciones de `motor.py` están completas y se utilizan desde la aplicación de
consola. Se conservaron `app.py`, el catálogo y los perfiles iniciales del material
para poder ejecutar las pruebas con los mismos datos.

## Cómo ejecutar la aplicación

La versión utilizada fue Python 3.12.14 en Windows. El proyecto depende de NumPy,
Pandas y scikit-learn; `requirements.txt` incluye las versiones instaladas y las
dependencias que necesitan estas bibliotecas.

Después de descargar o clonar el repositorio, se debe abrir una terminal en la
carpeta que contiene `app.py`. En PowerShell, la preparación es la siguiente:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -c "import sys; print(sys.version); print(sys.executable)"
python app.py --comprobar
```

Si el comando disponible es `py`, se puede crear el entorno con
`py -3.12 -m venv .venv`. En CMD se activa con
`.venv\Scripts\activate.bat`, y en macOS o Linux con `source .venv/bin/activate`.
También es posible ejecutar directamente el Python del entorno, por ejemplo:
`.venv\Scripts\python.exe app.py --demo` en Windows.

La comprobación de los datos mostró 12 recursos, 4 usuarios y una matriz TF-IDF de
12 filas por 17 términos. Para ejecutar los casos T1–T4 y generar las evidencias:

```powershell
python app.py --demo
```

Este modo parte de los perfiles iniciales y guarda los resultados en `evidencias/`.
Cada ejecución reemplaza el reporte JSON y el CSV de comparación. Para usar la
consola de forma manual se ejecuta:

```powershell
python app.py
```

Primero se elige un usuario. La opción `r` muestra recomendaciones; `c` muestra el
catálogo; `m` permite indicar «Me interesa» escribiendo el ID de un recurso; `u`
cambia de usuario y `s` termina la ejecución. Para repetir la prueba de adaptación,
se elige u1, se consultan sus recomendaciones y luego se valora R04 con la opción
`m`. Se puede seleccionar cualquier recurso del catálogo, aunque no aparezca entre
las primeras recomendaciones.

Los perfiles y sus historiales se mantienen mientras la aplicación está abierta.
Al reiniciarla, se cargan otra vez los intereses de `datos/perfiles.json`.

## Funcionamiento del recomendador

El catálogo está en `datos/recursos.csv`. Cada fila contiene un ID, un título, una
descripción y etiquetas. Para calcular la similitud se usan solamente las etiquetas;
el título y la descripción ayudan a presentar el recurso. La carga elimina espacios
al principio y al final de los campos y rechaza columnas faltantes, campos vacíos,
un catálogo vacío o IDs repetidos. Esto evita que un mismo ID pueda referirse a dos
recursos diferentes.

Al iniciar, `construir_indice` ajusta un único vectorizador TF-IDF al catálogo.
`crear_perfil` utiliza ese vectorizador para transformar los intereses en un vector
numérico de una dimensión. Luego, `calcular_puntuaciones` compara el perfil con
cada fila del catálogo mediante similitud del coseno.

La función `recomendar` selecciona hasta tres resultados con puntuación positiva y
los ordena de mayor a menor. Si dos puntuaciones son iguales, se utiliza el ID en
orden ascendente. Cada resultado incluye su título, la puntuación con cuatro
decimales y una explicación de los términos compartidos. Los valores usados para
calcular y ordenar no se redondean.

Cuando se registra «Me interesa», `actualizar_perfil` combina el vector actual con
el del recurso seleccionado:

```python
mezcla = 0.4 * perfil + 0.6 * vector_recurso
nuevo_perfil = normalize([mezcla])[0]
```

La interacción reciente recibe un peso de 0,6, tal como pide el laboratorio. Después
se normaliza la mezcla para que tenga norma L2 unitaria. El nuevo vector se guarda
solo para el usuario activo, junto con el evento en su historial. Se comparan de
nuevo los mismos 12 recursos, incluido el que acaba de valorar.

## Pruebas realizadas

Las pruebas se ejecutaron con los perfiles originales: u1 tiene los intereses
`python datos pandas`; u2, `angular componentes interfaces`; u3 tiene intereses
vacíos y u4 contiene `zzxyz123`, que no aparece en el vocabulario.

| Caso | Entrada o interacción | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|
| T1 | Recomendar inicialmente a u1 y u2 | Hasta tres resultados positivos, orden descendente, empates por ID e intereses diferenciados | u1: R02 (1,0000), R12 (0,4965), R03 (0,4326). u2: R07 (1,0000), R08 (0,5677), R09 (0,3087). El test adicional confirma desempate por ID con filas desordenadas. | Cumple |
| T2 | u1 valora R04 y vuelve a recomendar en la misma ejecución | Cambia su vector, sube R05, R04 encabeza el ranking y permanecen los 12 candidatos | u1: R04 (0,8752), R02 (0,6880), R09 (0,4958); R05 sube de 0 a 0,437777; se registra un evento y se conservan R01–R12. | Cumple |
| T3 | Consultar u2 después de actualizar u1 | Vector, historial y puntuaciones de u2 sin cambios | Las cuatro comprobaciones del reporte son verdaderas; historial vacío y ranking R07, R08, R09 intactos. | Cumple |
| T4 | Recomendar para u3 y u4 | Lista vacía, puntuaciones cero y mensaje informativo sin fallar | Ambos producen `[]`, todas las puntuaciones cero y el mensaje indicado arriba. | Cumple |


Los resultados de T1 muestran que el perfil inicial influye en la selección: u1
recibe contenidos relacionados con datos y Python, mientras que u2 recibe recursos
sobre Angular. En T2, la valoración de R04 modifica el perfil de u1 y cambia tanto
el orden como las puntuaciones. T3 comprueba que ese cambio no afecta a u2.

En T4, el programa no encuentra términos que pueda comparar para u3 y u4. Ambos
reciben una lista vacía y el mensaje «No hay coincidencias positivas. Declare
intereses presentes en el catálogo.». Así se evita completar la lista con recursos
que tienen puntuación cero.

También se incluyeron tres pruebas adicionales en `test_motor.py`: una comprueba
el desempate por ID, el filtro de ceros y el límite de resultados; otra verifica
que un ID desconocido no cambie el estado; y la tercera revisa la normalización y
las actualizaciones sucesivas del perfil. Las tres pasaron. Se ejecutan con:

```powershell
python -m unittest -v
```

## Análisis de la adaptación

Antes de valorar R04, el recurso que mejor coincide con u1 es R02, porque tiene
exactamente las etiquetas de sus intereses iniciales. Después de la valoración,
el perfil incorpora `api` y `web`, y aumenta el peso de `python`. Esto hace que
R04 pase al primer lugar y que aparezca R09 entre los tres primeros resultados.

### u1 antes de valorar R04

| Puesto | ID | Título | Similitud | Explicación |
|---|---|---|---:|---|
| 1 | R02 | Análisis de datos con Pandas | 1.0000 | Términos compartidos: datos, pandas, python. |
| 2 | R12 | Conectar Python con datos SQL | 0.4965 | Términos compartidos: datos, python. |
| 3 | R03 | Gráficos con Python | 0.4326 | Términos compartidos: datos, python. |

### u1 después de valorar R04

| Puesto | ID | Título | Similitud | Explicación |
|---|---|---|---:|---|
| 1 | R04 | API web con Python | 0.8752 | Términos compartidos: api, python, web. |
| 2 | R02 | Análisis de datos con Pandas | 0.6880 | Términos compartidos: datos, pandas, python. |
| 3 | R09 | Consumir una API desde Angular | 0.4958 | Términos compartidos: api, web. |

### u2, sin cambios antes y después de la interacción de u1

| Puesto | ID | Título | Similitud | Explicación |
|---|---|---|---:|---|
| 1 | R07 | Componentes e interfaces en Angular | 1.0000 | Términos compartidos: angular, componentes, interfaces. |
| 2 | R08 | Formularios e interfaces en Angular | 0.5677 | Términos compartidos: angular, interfaces. |
| 3 | R09 | Consumir una API desde Angular | 0.3087 | Términos compartidos: angular. |

### Pesos del perfil de u1

| Término | Antes | Después |
|---|---:|---:|
| api | 0.000000 | 0.446269 |
| datos | 0.465091 | 0.232455 |
| pandas | 0.753247 | 0.376477 |
| python | 0.465091 | 0.637116 |
| web | 0.000000 | 0.446269 |

Los otros 12 términos tienen peso cero en ambos estados. Antes, el historial de u1
está vacío; después contiene `{"numero": 1, "accion": "Me interesa", "recurso": "R04"}`.
Los intereses iniciales del JSON no se reescriben. Se actualiza el vector actual y
se recalcula el ranking en la misma sesión.

### Puntuaciones de los mismos 12 candidatos

| ID | Antes | Después | Diferencia |
|---|---:|---:|---:|
| R01 | 0.186096 | 0.254928 | +0.068832 |
| R02 | 1.000000 | 0.688010 | -0.311990 |
| R03 | 0.432619 | 0.404430 | -0.028189 |
| R04 | 0.251037 | 0.875178 | +0.624141 |
| R05 | 0.000000 | 0.437777 | +0.437777 |
| R06 | 0.000000 | 0.437777 | +0.437777 |
| R07 | 0.000000 | 0.000000 | +0.000000 |
| R08 | 0.000000 | 0.000000 | +0.000000 |
| R09 | 0.000000 | 0.495760 | +0.495760 |
| R10 | 0.205290 | 0.102605 | -0.102685 |
| R11 | 0.205290 | 0.102605 | -0.102685 |
| R12 | 0.496522 | 0.464168 | -0.032353 |

R09 es un caso que permite ver el efecto de la actualización en otro recurso: sube de 0 a 0,495760 y entra en el tercer puesto porque sus
etiquetas `angular web api` comparten los nuevos términos `web` y `api` incorporados
al perfil a partir de R04 (`python web api`). No se añade `angular` al perfil de u1.
R05 también cambia sin haber sido valorado: sube de 0 a 0,437777 por esos mismos términos compartidos.
El cambio llega a otros recursos porque se vuelve a comparar todo el catálogo con el nuevo perfil. R02 baja de 1 a 0,688010 porque el perfil deja de coincidir exactamente
con `python datos pandas`; la normalización redistribuye los pesos.

## Preguntas conceptuales

### 1. ¿Qué información describe los recursos y qué información forma el perfil del usuario?

Los recursos se describen en `datos/recursos.csv`. Aunque cada uno tiene título,
descripción y etiquetas, las características que utiliza el recomendador son las
palabras de las etiquetas. Por su parte, `datos/perfiles.json` contiene el nombre
y los intereses iniciales de cada usuario.

Durante la ejecución, esos intereses se representan mediante un vector que se
guarda en `estado`. El programa mantiene además un historial independiente por
usuario. Por eso el perfil no se limita al texto inicial: su vector puede cambiar
con las valoraciones, sin necesidad de editar el JSON.

### 2. ¿Por qué se usa fit_transform en el catálogo y transform en los intereses?

Se usa `fit_transform` con el catálogo porque primero hay que aprender qué palabras
existen y qué peso tiene cada una. Una vez definido ese vocabulario, `transform`
permite representar los intereses usando las mismas columnas y los mismos pesos
IDF. Esto es necesario para comparar ambos vectores.

Si se ajustara otro vectorizador para cada usuario, una columna podría representar
una palabra distinta o tener otro peso. Incluso podrían obtenerse vectores de
diferente tamaño. En esas condiciones, la comparación con el catálogo perdería
sentido.

### 3. ¿Por qué cambian las recomendaciones entre usuarios? ¿Una similitud de 0,80 equivale a un 80 % de probabilidad de gusto?

El catálogo es el mismo, pero cada usuario se compara con él a partir de intereses
diferentes. En las pruebas, u1 comparte términos con recursos de Python y datos,
mientras que u2 coincide más con contenidos de Angular e interfaces. Por eso sus
primeros resultados son distintos.

Un valor de 0,80 indica que los vectores tienen una dirección parecida en el espacio
TF-IDF. No equivale a una probabilidad de gusto: el programa no ha aprendido esa
relación a partir de valoraciones reales ni calcula una probabilidad calibrada.

### 4. ¿En qué se diferencia cambiar manualmente los intereses de la adaptación implementada?

Cambiar el texto de intereses en el JSON significa definir manualmente otro punto
de partida. En cambio, la adaptación ocurre mientras se utiliza la aplicación:
el usuario marca R04 con «Me interesa» y el programa actualiza su vector actual.

El evento pasa por `registrar_interes`, que llama a `actualizar_perfil` y guarda
la interacción en el historial de u1. El efecto se observa al volver a recomendar:
R04 pasa al primer lugar y también cambian recursos como R05 y R09. Los intereses
iniciales del archivo y el estado de u2 se conservan.

### 5. ¿Cómo se relaciona la implementación con MAPE-K?

La etapa de **monitorización** corresponde a recoger la acción «Me interesa» en la
consola e identificar al usuario y al recurso. Para **analizar** esa información,
se valida el ID con `obtener_indice` y se utiliza el vector TF-IDF del recurso como
señal de los temas que interesan al usuario.

La **planificación** está en la regla de actualización: combinar el perfil actual
con el recurso usando los pesos 0,4 y 0,6. La **ejecución** ocurre cuando
`registrar_interes` guarda el nuevo vector y se recalculan las recomendaciones.
Finalmente, el **conocimiento** está formado por el catálogo, el vocabulario y sus
pesos IDF, la matriz de recursos, los perfiles y los historiales. En esta aplicación
las etapas están repartidas entre funciones y datos del programa.

### 6. ¿Qué limitación tiene el mecanismo y cómo podría mejorarse?

Una limitación es que depende de las palabras que aparecen en el catálogo. Por
ejemplo, un interés expresado con un sinónimo puede quedar sin coincidencias aunque
se relacione con un recurso. El caso de u4 muestra qué sucede cuando no se reconoce
ninguno de los términos ingresados.

Una mejora sería incorporar un diccionario de sinónimos del área de programación y
normalizar tanto las etiquetas como los intereses antes de vectorizarlos. Ese
diccionario tendría que definir equivalencias revisadas, por ejemplo entre
«gráficas» y «graficos», y se necesitarían nuevas pruebas para comprobar
que las equivalencias no introduzcan recomendaciones incorrectas. El resto del
cálculo con TF-IDF y coseno podría mantenerse.

## Problemas encontrados

La preparación del entorno presentó dificultades con `ensurepip` y con los permisos
de la carpeta temporal. Se resolvió instalando las dependencias en el entorno
virtual desde el pip del intérprete base, usando una carpeta temporal con permiso
de escritura. Las evidencias se generaron ejecutando directamente el Python de ese
entorno, ubicado en `work/venv/Scripts/python.exe` durante la preparación.

En los resultados, la similitud inicial de R02 aparece en el CSV como
`1.0000000000000002`. Esa pequeña diferencia respecto de 1 se debe a la precisión
de los números de punto flotante; en la consola se muestra como `1.0000`. Los
valores originales se conservaron en las evidencias. Los pesos del perfil que
muestra el reporte están redondeados a seis decimales por la función auxiliar.

No se detectaron fallos en T1–T4 ni en las pruebas adicionales. Aun así, estas
pruebas corresponden al catálogo del laboratorio y no permiten afirmar cómo se
comportaría el recomendador con cualquier conjunto de recursos. Además, el estado
se conserva solo durante la sesión, por lo que cerrar la aplicación elimina las
valoraciones realizadas.

## Archivos de la entrega

El código está en `motor.py` y `app.py`, y los datos originales se encuentran en
`datos/`. El archivo `evidencias/reporte_demo.json` contiene los perfiles, las
recomendaciones, los eventos y las comprobaciones de la demostración.
`evidencias/puntuaciones_antes_despues.csv` registra las puntuaciones de los mismos
12 recursos antes y después de valorar R04. Ambos archivos fueron generados por
la ejecución de la implementación.

El repositorio incluye también las pruebas adicionales, este informe,
`requirements.txt` y `.gitignore`. El entorno virtual, las cachés y las dependencias
instaladas quedan fuera de la entrega. El archivo `enlace_repositorio.txt` contiene
la URL del repositorio público para adjuntarlo en la plataforma del curso.
