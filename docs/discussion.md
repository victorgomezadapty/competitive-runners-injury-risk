# Discusión científica: qué aporta una evaluación longitudinal rigurosa

**Actualización bibliográfica:** 2026-10-26. **Revisión editorial:** 2026-10-27. Esta síntesis narrativa contextualiza los resultados del proyecto; no es una revisión sistemática, una guía clínica ni una validación externa. [Métodos de búsqueda](literature_search.md) · [Bibliografía exportable](references.bib).

**English abstract.** This project studies training histories before selected injury-log events in competitive runners. Its contribution is a reproducible, athlete-aware and time-aware evaluation framework. Modest held-out ranking, uncertain calibration gains, source-conditioned selection and substantial review burden limit clinical interpretation. Complementary datasets inform software interfaces and research questions without supplying missing measurements for unrelated participants.

## Hallazgo principal

La contribución es metodológica: conservar el orden temporal, separar atletas, auditar las etiquetas y mostrar el coste de revisar alertas. La referencia fija de Phase 2 obtuvo average precision (AP) de 0.0222 en observaciones futuras de atletas conocidos, 0.0201 en atletas no vistos de distintos periodos y 0.0200 en atletas no vistos del periodo posterior. El último análisis incluyó 7,596 filas seleccionadas y 122 etiquetas positivas, fracción 0.0161 y ROC-AUC 0.5456. Son señales modestas dentro de la muestra publicada; no equivalen a probabilidad clínica de lesión mañana. Los resultados completos y los intervalos están en [Phase 2](../reports/phase_02_summary.md).

El intervalo de AP por remuestreo de atletas en el diseño combinado fue aproximadamente 0.0148–0.0430. Es condicional a los modelos ajustados: no incluye volver a entrenarlos ni la dependencia compartida de un mismo equipo. Los tres diseños evalúan poblaciones y periodos diferentes; restar sus métricas no identifica causalmente una cantidad de fuga de información.

La ampliación final añade comparaciones sobre eventos emparejados y sensibilidades de particiones y ponderación. Debe interpretarse con sus denominadores y todas sus alternativas, conservando la referencia anterior. Cambiar el conjunto de eventos puede cambiar AP aunque no cambie el algoritmo; elegir únicamente el resultado más favorable sería engañoso. Véanse los [resultados finales completos](../reports/final_analysis/pooled_metrics.csv).

## La etiqueta determina lo que se puede investigar

El estudio original de Lövdal y colaboradores comunicó ROC-AUC 0.724 y 0.678 para las representaciones Day y Week. Son referencias históricas, no objetivos intercambiables con nuestros experimentos. Las decisiones de normalización, selección, representación y evaluación cambian la pregunta. El indicador publicado refleja incapacidad para completar entrenamiento programado por lesión; no distingue diagnóstico, tejido, severidad o inicio clínico. [Lövdal et al., 2021](https://doi.org/10.1123/ijspp.2020-0518).

Los controles sanos se seleccionaron exigiendo buena condición antes y después del evento; también se excluyeron etiquetas próximas a otras lesiones. Por tanto, 583 etiquetas entre 42,766 filas Day representan una fracción de una muestra seleccionada, no incidencia por persona-tiempo. Evitar predictores futuros no deshace esa selección original. La [definición exacta](injury_definition.md) y la [fuente de datos](https://doi.org/10.34894/UWU9PV) limitan cualquier interpretación posterior.

También importa una corrección documental: el README revisado asigna las columnas Day sin sufijo a E−7 y `.6` a E−1. Seguimos esos bytes originales y comprobamos concordancia entre ventanas solapadas. El registro de errata se cita por separado; el mapeo concreto procede del README corregido, no se deduce del título de la errata. Invertir los días alteraría tendencias y explicaciones temporales. [README corregido](https://dataverse.nl/api/access/datafile/422690?format=original), [errata IJSPP, 2024](https://doi.org/10.1123/ijspp.2024-0251).

## Carga y lesión forman parte de un sistema más amplio

Bittencourt y colaboradores proponen interpretar la lesión mediante relaciones dinámicas entre determinantes. Este marco justifica estudiar exposición, recuperación e historia conjuntamente, pero no demuestra que una red neuronal sea superior ni que las variables disponibles representen el sistema completo. Aquí faltan síntomas, capacidad tisular, sueño, ambiente e historia clínica verificada. La ausencia de esas mediciones limita la interpretación; no permite inventarlas o transferirlas de otras personas. [Bittencourt et al., 2016](https://doi.org/10.1136/bjsports-2015-095850).

En los contrastes descriptivos de este proyecto, la distancia semanal fue mayor y los días de descanso menores antes de las etiquetas retenidas. La recuperación percibida también fue ligeramente mayor, no menor. No procede presentar una recuperación baja como hallazgo confirmado. Son asociaciones afectadas por selección, hábitos de registro y observaciones correlacionadas; no prueban que modificar una variable evite lesiones.

Impellizzeri y colaboradores distinguen asociación pronóstica de efecto causal y señalan dificultades conceptuales y estadísticas del cociente agudo:crónico. Por ello usamos sumas y diferencias interpretables, conservamos extremos y no convertimos ACWR en una zona clínica universal de seguridad. [Impellizzeri et al., 2020](https://doi.org/10.1123/ijspp.2019-0864).

Su reanálisis posterior cuestiona la información protectora atribuida a la carga crónica y el valor del cociente frente a referencias simples. Esto respalda comparar cambios de carga con carga absoluta y modelos constantes. No demuestra que todo cambio longitudinal sea inútil. [Impellizzeri et al., 2021](https://doi.org/10.1007/s40279-020-01378-6).

## Cambio individual y diferencias entre personas

Curran y Bauer explican que una asociación entre personas puede diferir de una asociación dentro de la misma persona. Un atleta que habitualmente entrena más no equivale a otro que supera súbitamente su nivel habitual. Esto motiva nuestras referencias personales históricas; para predicción, calcularlas con temporadas futuras introduciría información que todavía no existiría. [Curran y Bauer, 2011](https://doi.org/10.1146/annurev.psych.093008.100356).

La sensibilidad personal de Phase 2 utiliza historia previa, demora explícita de disponibilidad y un mínimo de días observados. Fue posible en 27,096 de 42,766 registros, por lo que la cobertura es selectiva. AP 0.0238 en atletas conocidos coexistió con menor ROC-AUC que la referencia principal: no demuestra personalización eficaz. Separar nivel previo y desviación como predictores tampoco equivale a estimar efectos causales intraindividuales mediante un modelo de medidas repetidas.

## Relación con trabajo reciente sobre la misma fuente

Qiao y Tian estudian clasificación independiente por atleta, calibración y modelos temporales sobre estos mismos datos. Es una referencia metodológica, no evidencia de una cohorte externa. Su sección 3.1 describe el orden de sufijos Day en sentido contrario al README corregido. Por ello no copiamos su orden temporal ni interpretamos sus atribuciones por día como validación de nuestro código. Diferencias de arquitectura, preprocesamiento y particiones impiden una comparación numérica directa. [Qiao y Tian, 2026](https://doi.org/10.3389/fpubh.2026.1936365).

Con 74 atletas, miles de ventanas repetidas no se convierten en miles de personas independientes. Comparaciones emparejadas, estabilidad y auditoría de la fuente pueden aportar más que mayor complejidad algorítmica. Un test con atletas distintos del mismo equipo sigue sin validar transferencia a corredores recreativos, otros países o servicios clínicos.

## Eventos raros, calibración y carga de revisión

Saito y Rehmsmeier muestran la utilidad de precision–recall en clasificación desequilibrada. Aquí AP utiliza la definición no interpolada de scikit-learn; no es el área trapezoidal PR. Depende de la fracción positiva evaluada. ROC-AUC se conserva como complemento, pero puede coexistir con numerosas falsas alertas. Las referencias constantes por partición pueden tener AP agrupada distinta de la prevalencia agrupada. [Saito y Rehmsmeier, 2015](https://doi.org/10.1371/journal.pone.0118432).

Van Calster y colaboradores distinguen discriminación y calibración. En nuestros resultados, la calibración sigmoide independiente mejora algunas pérdidas y empeora otras. Un Brier pequeño es esperable con positivos escasos y debe contrastarse con una referencia de frecuencia. Ni ese valor ni una curva aparente convierten probabilidades condicionadas a la selección en riesgo clínico individual. [Van Calster et al., 2019](https://doi.org/10.1186/s12916-019-1466-7).

La utilidad operativa exige mirar denominadores. En el diseño Phase 2 de atletas no vistos y periodo posterior, el umbral elegido para revisar 10% de los registros de calibración marcó 1,082 de 7,596 registros de test: 14.24 por cada 100 seleccionados. Capturó 18 de 122 positivos, con 1,064 falsos positivos, precisión 1.66% y sensibilidad 14.75%: unas 60 revisiones por etiqueta capturada. No son alertas por mes real de seguimiento ni por lesión clínica incidente. La web permite explorar este intercambio; no establece categorías clínicas arbitrarias.

## Transparencia y aplicabilidad

TRIPOD+AI recomienda describir claramente propósito, datos, métodos y resultados de modelos predictivos, incluidos regresión y aprendizaje automático. Motiva documentar disponibilidad temporal, preprocesamiento, incertidumbre y reproducción. No hemos realizado una evaluación externa ítem por ítem: citar la guía no es certificación de cumplimiento o preparación clínica. [Collins et al., 2024](https://doi.org/10.1136/bmj-2023-078378).

PROBAST+AI distingue calidad del desarrollo, sesgo de la evaluación y aplicabilidad. Estos aspectos siguen limitados por una sola cohorte seleccionada, calibración con pocos eventos y ausencia de validación prospectiva independiente. Usamos sus conceptos para identificar problemas, sin asignar una valoración formal de bajo riesgo de sesgo. [Moons et al., 2025](https://doi.org/10.1136/bmj-2024-082505).

## Qué añaden las fuentes complementarias

Wu y colaboradores aportan una cohorte de corredores con dominios multidisciplinares y seguimiento semanal. Los libros públicos inspeccionados aquí carecen de claves explícitas de participante y tiempo, y su endpoint difiere. Se conservan como referencia separada: no inferimos cronología por el orden de filas, reconstruimos identidades ni los incorporamos a validación por atleta. Un AUC publicado mayor en otra tarea no demuestra rendimiento equivalente de este proyecto. [Wu et al., 2026](https://doi.org/10.1038/s41746-026-02413-y), [auditoría local](complementary_data_profile.md).

SoccerMon permite preparar adaptadores de sueño, bienestar, sesiones y recuperación en fútbol femenino de élite. No completa esas mediciones en los corredores neerlandeses. El descriptor diferencia 162 reportes de lesión que contienen 306 entradas de lesión/localización: reportes, entradas anatómicas y eventos clínicos incidentes no son denominadores equivalentes. Deben conservarse escalas y disponibilidad específicas de cada fuente. [Midoglu et al., 2024](https://doi.org/10.1038/s41597-024-03386-x).

## Relevancia para el proyecto público

El producto defendible es un explorador educativo de investigación: trayectorias corregidas, datos documentados, validación, calibración y coste de revisión. No diagnostica, estima efectos de tratamientos ni promete prevención. Antes de uso real se necesitarían registros continuos representativos, marcas de disponibilidad, vigilancia completa de resultados y evaluación prospectiva con atletas y profesionales.

Esta discusión es síntesis nueva con referencias enlazadas. No reproduce figuras o textos extensos de artículos. La licencia del dataset original, las licencias de fuentes complementarias y los derechos de los artículos son independientes. Los resultados y gráficos propios deben atribuir la fuente de datos; los artículos y diseños de terceros se enlazan sin republicarlos bajo la licencia del código.
