# Búsqueda bibliográfica narrativa

**Búsqueda:** 2026-10-26. **Edición:** 2026-10-27 (Asia/Riyadh). Objetivo: contextualizar selección de eventos, validación por atleta/tiempo, cambios individuales, calibración y límites de decisión. Es una búsqueda dirigida, no revisión sistemática: sin registro, exportación exhaustiva, cribado doble, diagrama PRISMA ni metaanálisis. No se afirma exhaustividad.

## Consultas realmente utilizadas

```text
site.bjsm.bmj.com Bittencourt complex systems approach sports injuries 2016 doi
site.bjsm.bmj.com Impellizzeri acute chronic workload ratio conceptual issues fundamental pitfalls 2020
site.bmj.com TRIPOD AI 2024 prediction model reporting statement
site.frontiersin.org 1936365 Qiao Tian athlete independent 2026
site.bmcmedicine.biomedcentral.com calibration Achilles heel predictive analytics 2019 Van Calster
site.journals.plos.org Saito Rehmsmeier precision recall ROC imbalanced 2015
site.pubmed.ncbi.nlm.nih.gov Curran Bauer disaggregation within person between person longitudinal models 2011
site.bmj.com PROBAST AI 2025 quality risk bias prediction models
"Erratum" "Injury Prediction in Competitive Runners" "846"
"Complex systems approach for sports injuries" Bittencourt 2016 1309 1314
"s41746-026-02413-y"
"s41597-024-03386-x" SoccerMon
"10.34894/UWU9PV" "CC0"
```

Se abrieron enlaces originales de revistas, PubMed/PMC, fuente de datos e instituciones, incluidos enlaces directos conocidos. Los resultados del buscador fueron subconjuntos ordenados; no se presenta un recuento total de estudios identificados. Se comprobó el README original adquirido y su manifiesto local.

## Criterios y matriz de evidencia

Se incluyeron fuentes que fundamentan un problema concreto del proyecto, prefiriendo el trabajo de los autores originales y los descriptores de datos. Se excluyeron blogs comerciales, afirmaciones no verificadas y estudios incompatibles presentados como validación externa. Los artículos conceptuales y metodológicos se distinguen de evidencia empírica de intervención.

| Clave BibTeX | Fuente y tipo | Uso y límite |
|---|---|---|
| lovdal_data_2024 | [Dataverse original](https://doi.org/10.34894/UWU9PV), dataset | Proveniencia y README corregido; no vigilancia completa |
| lovdal2021 | [IJSPP 2021](https://doi.org/10.1123/ijspp.2020-0518), estudio original | Endpoint, selección y referencia histórica; diseño distinto |
| lovdal_erratum2024 | [Errata 2024](https://doi.org/10.1123/ijspp.2024-0251), corrección | Existencia bibliográfica verificada; mapeo exacto obtenido del README |
| qiao2026 | [Frontiers 2026](https://doi.org/10.3389/fpubh.2026.1936365), estudio sobre misma fuente | Validación por atleta y modelos temporales; orden de lags discrepante, no adoptado |
| bittencourt2016 | [BJSM 2016](https://doi.org/10.1136/bjsports-2015-095850), propuesta conceptual narrativa | Complejidad; no prueba causal o de superioridad algorítmica |
| impellizzeri2020 | [IJSPP 2020](https://doi.org/10.1123/ijspp.2019-0864), crítica metodológica | Asociación frente a intervención y cocientes; no prueba sobre todas nuestras ventanas |
| impellizzeri2021 | [Sports Medicine 2021](https://doi.org/10.1007/s40279-020-01378-6), reanálisis | Cuestiona supuestos ACWR; otra fuente y diseño |
| vancalster2019 | [BMC Medicine 2019](https://doi.org/10.1186/s12916-019-1466-7), opinión metodológica | Calibración/discriminación; no valida probabilidades de corredores |
| saito2015 | [PLOS ONE 2015](https://doi.org/10.1371/journal.pone.0118432), estudio metodológico | Evaluación precision–recall; depende de prevalencia |
| curran2011 | [Annual Review 2011](https://doi.org/10.1146/annurev.psych.093008.100356), síntesis/propuesta metodológica | Efectos intra/entre personas; no evidencia causal en corredores |
| collins2024 | [TRIPOD+AI](https://doi.org/10.1136/bmj-2023-078378), guía | Transparencia; no certificación del proyecto |
| moons2025 | [PROBAST+AI](https://doi.org/10.1136/bmj-2024-082505), herramienta de evaluación | Calidad/sesgo/aplicabilidad; no valoración formal completada |
| wu2026 | [npj Digital Medicine](https://doi.org/10.1038/s41746-026-02413-y), otra cohorte | Dominios complementarios; sin claves explícitas en archivos públicos inspeccionados |
| midoglu2024 | [SoccerMon](https://doi.org/10.1038/s41597-024-03386-x), descriptor original | Bienestar y estructura de reportes; población y escalas distintas |

Total seleccionado: 14 registros, contando dataset y errata separadamente de artículos. [Bibliografía](references.bib).

## Acceso y verificaciones

Se consultó texto original disponible de Qiao, Saito, Van Calster, TRIPOD+AI y PROBAST+AI; Curran mediante PMC y Wu mediante PMC tras redirección de Nature. SoccerMon se comprobó con texto indexado del descriptor primario. Bittencourt se utilizó por su resumen original y registro editorial, sin afirmar evaluación exhaustiva del texto completo. La crítica ACWR se comprobó mediante registros originales/PubMed y el reanálisis en Springer.

El original de Lövdal está en [PubMed 33931574](https://pubmed.ncbi.nlm.nih.gov/33931574/); sus métodos ya se habían leído en la copia institucional durante Milestone 1. La errata está en [PubMed 38897576](https://pubmed.ncbi.nlm.nih.gov/38897576/): el DOI no se pudo leer completo en esta búsqueda. El README no se renderizó en la herramienta web, pero sus bytes originales adquiridos y verificados se leyeron localmente: revisión 2024-04-19, release 2.0 de 2024-06-05.

Se verificaron títulos y DOI en fuentes primarias, sin usar métricas de revista como evidencia de validez. Para listas largas, `and others` en BibTeX es deliberado. No se copiaron figuras, tablas o PDFs para estos documentos. Las licencias del dataset y artículos son distintas; las fuentes originales se atribuyen y enlazan.

## Incertidumbres que la búsqueda no resuelve

No identifica ensayo de modificación de entrenamiento guiado por nuestro modelo, utilidad clínica prospectiva, umbral validado o prueba de prevención. Persisten dudas sobre extremos, escalas constantes y disponibilidad real de mediciones. La discusión contextualiza resultados; no transforma evidencia observacional en recomendación causal.
