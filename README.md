# Laboratorio 3: aplicación inteligente adaptativa

## Identificación

- Integrantes: German Oses, Joshua Villavicencio y Fernando Figueroa.
- Asignatura: Ingeniería Web Avanzada, OII436-1, segundo semestre de 2026.
- Fecha de ejecución: 9 de noviembre de 2026.
- Repositorio GitHub: https://github.com/German-Oses/laboratorio3

Recomendador de recursos de aprendizaje por consola. Utiliza TF-IDF de etiquetas,
similitud del coseno y actualización automática del perfil ante «Me interesa».
Se completaron las cuatro funciones de `motor.py`; `app.py` y los archivos de datos
se conservan tal como fueron entregados. No se requiere Angular.

## Entorno y reproducción

Validado con **Python 3.12.14 en Windows**, dentro de un entorno virtual separado.
Las versiones exactas de las dependencias y sus dependencias transitivas están en
`requirements.txt`, generado con `python -m pip freeze` en ese entorno.
Dependencias principales: NumPy 2.5.4, Pandas 3.1.1 y scikit-learn 1.9.1.

Desde una copia del repositorio, abrir una terminal en la carpeta que contiene `app.py`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -c "import sys; print(sys.version); print(sys.executable)"
python app.py --comprobar
python app.py --demo
python -m unittest -v
python app.py
```

Si Windows reconoce el intérprete como `py`, usar `py -3.12 -m venv .venv`.
En CMD se activa con `.venv\Scripts\activate.bat`; en macOS/Linux,
con `source .venv/bin/activate`. También se puede omitir la activación e invocar
`.venv\Scripts\python.exe app.py --demo` directamente en Windows.

En la ejecución que generó estas evidencias se usó directamente el intérprete
`work/venv/Scripts/python.exe`, sin activar la shell. El Python integrado del entorno
de trabajo no pudo completar `ensurepip`; se creó el entorno y se instalaron las
dependencias usando el pip del intérprete base con `--python` dirigido al entorno.
Esto es una particularidad del entorno de trabajo, no un requisito del proyecto.
La instalación requirió acceso a PyPI y una carpeta temporal con permiso de escritura.
No se incluyen el entorno virtual ni las dependencias instaladas en la entrega.

`--comprobar` informó **12 recursos, 4 usuarios y una matriz de 12 × 17**.
`--demo` parte siempre de perfiles nuevos, imprime T1–T4 y sobrescribe las evidencias.
Devuelve código 0 si todas cumplen y 1 si alguna falla. El modo interactivo conserva
el estado en memoria; al reiniciar recupera los intereses iniciales del JSON.

Para reproducir manualmente: elegir `u1`, `r` para recomendar, `m` y `R04` para valorar;
`u` cambia de usuario, `c` muestra el catálogo y `s` finaliza. R04 se puede seleccionar
aunque no esté entre las tres primeras recomendaciones. Un ID desconocido muestra
un aviso y no modifica perfiles ni historiales.

## Datos y decisiones del motor

`datos/recursos.csv` conserva los 12 IDs y etiquetas originales. Solo **etiquetas**
interviene en TF-IDF; título y descripción presentan los recursos. El ID permite
identificarlos y resolver empates. La carga elimina espacios exteriores y rechaza
columnas requeridas ausentes, catálogo vacío, campos vacíos e IDs duplicados con
`ValueError`; no inventa datos ni elimina duplicados silenciosamente.

`datos/perfiles.json` contiene los intereses iniciales: u1 `python datos pandas`,
u2 `angular componentes interfaces`, u3 vacío y u4 `zzxyz123`. Cada usuario tiene
su propio vector e historial. Los dos últimos perfiles producen vectores cero,
puntuaciones cero y ninguna recomendación. Se muestra:
«No hay coincidencias positivas. Declare intereses presentes en el catálogo.»

- `crear_perfil`: reutiliza `transform` del vectorizador ajustado y devuelve una fila 1D.
- `calcular_puntuaciones`: calcula `cosine_similarity([perfil], matriz)[0]` en el orden del catálogo.
- `recomendar`: filtra puntuaciones positivas, ordena por puntuación descendente e ID ascendente y devuelve hasta tres resultados por defecto, usando `construir_resultado`.
- `actualizar_perfil`: normaliza `0.4 * perfil_actual + 0.6 * vector_recurso` con norma L2 y devuelve un vector 1D nuevo.

El índice se ajusta una sola vez. Se comparan siempre los mismos 12 candidatos,
incluido R04 después de valorarlo. Se conservan los números sin redondear para los
cálculos; solo la presentación se redondea. La regla 0,6 es didáctica, no optimizada.

## Pruebas T1–T4

Resultados obtenidos ejecutando esta implementación, registrados en
`evidencias/reporte_demo.json` y `evidencias/puntuaciones_antes_despues.csv`.

| Caso | Entrada o interacción | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|
| T1 | Recomendar inicialmente a u1 y u2 | Hasta tres resultados positivos, orden descendente, empates por ID e intereses diferenciados | u1: R02 (1,0000), R12 (0,4965), R03 (0,4326). u2: R07 (1,0000), R08 (0,5677), R09 (0,3087). El test adicional confirma desempate por ID con filas desordenadas. | Cumple |
| T2 | u1 valora R04 y vuelve a recomendar en la misma ejecución | Cambia su vector, sube R05, R04 encabeza el ranking y permanecen los 12 candidatos | u1: R04 (0,8752), R02 (0,6880), R09 (0,4958); R05 sube de 0 a 0,437777; se registra un evento y se conservan R01–R12. | Cumple |
| T3 | Consultar u2 después de actualizar u1 | Vector, historial y puntuaciones de u2 sin cambios | Las cuatro comprobaciones del reporte son verdaderas; historial vacío y ranking R07, R08, R09 intactos. | Cumple |
| T4 | Recomendar para u3 y u4 | Lista vacía, puntuaciones cero y mensaje informativo sin fallar | Ambos producen `[]`, todas las puntuaciones cero y el mensaje indicado arriba. | Cumple |

T1 confirma personalización inicial según los intereses; T2 demuestra adaptación
causada por una interacción; T3 verifica aislamiento por usuario; T4 evita atribuir
relevancia arbitraria cuando no hay información reconocida.

`python -m unittest -v` ejecutó además **3 pruebas, todas correctas**: desempates,
filtro de ceros y límites de resultados; rechazo de un ID inexistente sin cambios;
y normalización, entradas intactas y efecto de actualizaciones sucesivas.

## Recomendaciones y perfil antes y después

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

**R09 no fue valorado:** sube de 0 a 0,495760 y entra en el tercer puesto porque sus
etiquetas `angular web api` comparten los nuevos términos `web` y `api` incorporados
al perfil a partir de R04 (`python web api`). No se añade `angular` al perfil de u1.
**R05 tampoco fue valorado:** sube de 0 a 0,437777 por esos mismos términos compartidos.
Esto demuestra propagación del efecto a otros candidatos, no solo una promoción del
recurso elegido. R02 baja de 1 a 0,688010 porque el perfil deja de coincidir exactamente
con `python datos pandas`; la normalización redistribuye los pesos.

## Respuestas a las seis preguntas conceptuales

### 1. Contenido y perfil del usuario

El contenido está en `datos/recursos.csv`: ID, título, descripción y etiquetas.
Para calcular similitudes se utilizan únicamente las etiquetas. El perfil inicial
está en `datos/perfiles.json`, en el campo `intereses` de cada usuario; `nombre`
sirve para identificarlo en la interfaz. Durante la sesión, `estado` contiene el
vector actual y `historial` sus eventos. Los intereses originales se conservan
como punto de partida; el vector puede evolucionar sin cambiar el archivo JSON.

### 2. fit_transform y transform

`fit_transform` aprende del catálogo el vocabulario, el orden de sus columnas y los
pesos IDF, y construye sus vectores. `transform` representa los intereses en ese
mismo espacio. Ajustar otro vectorizador por usuario podría cambiar dimensiones,
orden de términos y pesos IDF: los vectores dejarían de ser comparables, incluso
si por casualidad tuvieran el mismo número de columnas.

### 3. Diferentes recomendaciones y significado de 0,80

u1 y u2 tienen diferentes términos y pesos en sus vectores. Al compararlos con el
mismo catálogo, sus direcciones coinciden con recursos distintos: datos/Python
frente a componentes/interfaces/Angular. Una similitud de 0,80 mide proximidad
angular entre las representaciones; **no significa un 80 % de probabilidad de gusto**.
No existe un modelo probabilístico calibrado con valoraciones reales ni se está
midiendo comprensión semántica del contenido.

### 4. Modificación manual y adaptación

Editar los intereses iniciales requiere intervención manual y define otro punto de
partida. Aquí el evento «Me interesa» sobre R04 dispara `registrar_interes`, que
actualiza automáticamente el vector actual de u1 mediante `actualizar_perfil` y
añade el evento a su historial. El efecto observable es el cambio de pesos, de
puntuaciones (incluyendo R05 y R09) y del ranking durante la misma ejecución;
u2 y el JSON inicial no cambian.

### 5. Ciclo MAPE-K

| Etapa | Correspondencia concreta en la implementación |
|---|---|
| Monitorizar | `interactivo` recoge el usuario activo y el ID del recurso al seleccionar `m`; `registrar_interes` registra el evento «Me interesa». |
| Analizar | `obtener_indice` valida el recurso; sus características TF-IDF aportan la señal de preferencia. `calcular_puntuaciones` permite evaluar la afinidad antes y después. |
| Planificar | La política fija combina 0,4 del perfil actual con 0,6 del recurso, dentro de `actualizar_perfil`, para obtener el perfil candidato normalizado. |
| Ejecutar | `registrar_interes` asigna el nuevo vector a `estado[usuario_id]`; `recomendar` recalcula la selección y la consola la muestra. |
| Conocimiento | Catálogo, vocabulario y pesos IDF, matriz TF-IDF, intereses iniciales, vectores actuales e historiales separados por usuario. |

Es una correspondencia conceptual con MAPE-K: las etapas están integradas en
funciones y datos de la aplicación, no en cinco servicios independientes.

### 6. Limitación y mejora concreta

El mecanismo solo reconoce coincidencias léxicas del vocabulario: un sinónimo o
un tema ausente puede producir un vector nulo aunque el interés sea relevante.
Una mejora concreta sería usar embeddings de las etiquetas junto con título y
descripción, generados por un mismo modelo para recursos e intereses. Exigiría
incorporar y fijar la versión de ese modelo, reemplazar la vectorización TF-IDF,
recalcular el índice y validar un umbral de similitud con pares de consultas y
recursos evaluados por personas. Esto permitiría evaluar afinidad semántica, pero
no convertiría por sí solo la similitud en una probabilidad de gusto.

## Problemas detectados y límites

No hubo incumplimientos funcionales en T1–T4 ni en las pruebas adicionales.
Se resolvieron las dificultades de preparación del entorno descritas arriba.
El valor de R02 inicial se registra como `1.0000000000000002`: es error de precisión
de punto flotante; la consola lo muestra como 1,0000. Se preserva la evidencia real
sin reemplazarla por una cifra esperada. Los perfiles legibles del JSON están
redondeados a seis decimales por la función auxiliar original; las puntuaciones del
CSV se escriben sin redondeo explícito.

El estado se pierde al cerrar la aplicación, por diseño del laboratorio. No hay
aprendizaje supervisado, persistencia de valoraciones ni evaluación con usuarios
reales. Los cuatro casos verifican el catálogo didáctico; no demuestran calidad
universal de las recomendaciones.

## Archivos y entrega en GitHub

- `motor.py`: cuatro funciones implementadas y utilizadas por `app.py`.
- `app.py`: consola, comprobación y demostración T1–T4 originales.
- `datos/recursos.csv` y `datos/perfiles.json`: datos originales.
- `evidencias/reporte_demo.json`: ejecución real con perfiles, rankings, eventos y comprobaciones.
- `evidencias/puntuaciones_antes_despues.csv`: comparación de los 12 recursos.
- `test_motor.py`: comprobaciones adicionales reproducibles.
- `requirements.txt`: dependencias con versiones exactas.
- `.gitignore`: excluye entorno, cachés, dependencias y secretos.
- `enlace_repositorio.txt`: URL del repositorio para adjuntar en la plataforma de entrega.

Repositorio de entrega: https://github.com/German-Oses/laboratorio3

Adjuntar `enlace_repositorio.txt` en la plataforma de entrega. El repositorio es
público para permitir acceso a la docente. El ZIP es una copia de respaldo;
la entrega solicitada se realiza por enlace al repositorio.
