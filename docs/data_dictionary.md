# Data dictionary

Exact original names are preserved in raw data. This is a column-complete dictionary generated from both original files; its machine-readable version is [data_dictionary.csv](../reports/tables/data_dictionary.csv).

E denotes the selected event day. Corrected daily order: unsuffixed E-7 through `.6` E-1. Weekly order: unsuffixed E-7..E-1, `.1` E-14..E-8, `.2` E-21..E-15. The 2024 source README takes precedence over the uncorrected 2021 PDF and conflicting secondary papers.

Subjective values are released on a 0-1 numerical scale, with -0.01 as the daily rest sentinel. Original questionnaire anchors, transformations from another scale, and instrument validation are not supplied. Do not multiply by 10 and call this Borg RPE. Zero can be a valid value and is not automatically imputed. Training success has athlete-specific response patterns; examine the usage audit.

`strength training` is described as a presence indicator in the README, but the paper and observed values suggest counts; retain original values and flag values >1 rather than silently binarizing. The files contain no running duration column despite duration being recorded upstream. No explicit easy-zone distance, HRV, sleep, wellness, sex, age, diagnosis, or injury severity column is available. Do not invent these variables or link sex to IDs.

Observed extrema below are audit facts, not verified physiological limits. Weekly ratio values can be enormous near zero denominator. These are preserved but quarantined.

Definitions: [source README](https://dataverse.nl/api/access/datafile/422690?format=original), [study](https://doi.org/10.1123/ijspp.2020-0518). Units and numerical range are directly checked against the original files.

| Representation | Exact column | Window | Units | Definition | Observed range |
|---|---|---|---|---|---|
| day | `nr. sessions` | E-7 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km` | E-7 | km | Distance covered running that day | 0 to 55.9 |
| day | `km Z3-4` | E-7 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2` | E-7 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting` | E-7 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training` | E-7 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative` | E-7 | hours | Hours of alternative/cross training; type not released | 0 to 10.22 |
| day | `perceived exertion` | E-7 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess` | E-7 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery` | E-7 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `nr. sessions.1` | E-6 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km.1` | E-6 | km | Distance covered running that day | 0 to 55.9 |
| day | `km Z3-4.1` | E-6 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2.1` | E-6 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting.1` | E-6 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training.1` | E-6 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative.1` | E-6 | hours | Hours of alternative/cross training; type not released | 0 to 10.22 |
| day | `perceived exertion.1` | E-6 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess.1` | E-6 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery.1` | E-6 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `nr. sessions.2` | E-5 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km.2` | E-5 | km | Distance covered running that day | 0 to 55.9 |
| day | `km Z3-4.2` | E-5 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2.2` | E-5 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting.2` | E-5 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training.2` | E-5 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative.2` | E-5 | hours | Hours of alternative/cross training; type not released | 0 to 10.22 |
| day | `perceived exertion.2` | E-5 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess.2` | E-5 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery.2` | E-5 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `nr. sessions.3` | E-4 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km.3` | E-4 | km | Distance covered running that day | 0 to 57 |
| day | `km Z3-4.3` | E-4 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2.3` | E-4 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting.3` | E-4 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training.3` | E-4 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative.3` | E-4 | hours | Hours of alternative/cross training; type not released | 0 to 10.22 |
| day | `perceived exertion.3` | E-4 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess.3` | E-4 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery.3` | E-4 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `nr. sessions.4` | E-3 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km.4` | E-3 | km | Distance covered running that day | 0 to 55.9 |
| day | `km Z3-4.4` | E-3 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2.4` | E-3 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting.4` | E-3 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training.4` | E-3 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative.4` | E-3 | hours | Hours of alternative/cross training; type not released | 0 to 10 |
| day | `perceived exertion.4` | E-3 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess.4` | E-3 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery.4` | E-3 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `nr. sessions.5` | E-2 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km.5` | E-2 | km | Distance covered running that day | 0 to 55.9 |
| day | `km Z3-4.5` | E-2 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2.5` | E-2 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting.5` | E-2 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training.5` | E-2 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative.5` | E-2 | hours | Hours of alternative/cross training; type not released | 0 to 10 |
| day | `perceived exertion.5` | E-2 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess.5` | E-2 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery.5` | E-2 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `nr. sessions.6` | E-1 | sessions | Number of completed training sessions that day | 0 to 2 |
| day | `total km.6` | E-1 | km | Distance covered running that day | 0 to 55.9 |
| day | `km Z3-4.6` | E-1 | km | Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README) | 0 to 42.2 |
| day | `km Z5-T1-T2.6` | E-1 | km | Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions | 0 to 48 |
| day | `km sprinting.6` | E-1 | km | Distance covered sprinting; no numerical speed cut-point supplied | 0 to 40 |
| day | `strength training.6` | E-1 | logged count; review >1 | Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count | 0 to 2 |
| day | `hours alternative.6` | E-1 | hours | Hours of alternative/cross training; type not released | 0 to 20 |
| day | `perceived exertion.6` | E-1 | released rating 0-1 | Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE | -0.01 to 1 |
| day | `perceived trainingSuccess.6` | E-1 | released rating 0-1 | Self-estimated success of main session; released 0-1 scale | -0.01 to 1 |
| day | `perceived recovery.6` | E-1 | released rating 0-1 | Self-estimated restedness before session; released 0-1 scale | -0.01 to 1 |
| day | `Athlete ID` | event day E | identifier | Masked athlete identifier; numeric order is not a biological quantity | 0 to 73 |
| day | `injury` | event day E | binary | Retained injury flag (1) versus selected healthy event (0); see injury_definition.md | 0 to 1 |
| day | `Date` | event day E | relative days | Event day relative to first record in dataset; calendar origin unavailable | 0 to 2673 |
| week | `nr. sessions` | E-7..E-1 | sessions | Total completed training sessions in preceding week | 0 to 14 |
| week | `nr. rest days` | E-7..E-1 | days | Number of days without a training session in preceding week | 0 to 7 |
| week | `total kms` | E-7..E-1 | km | Total weekly running distance | 0 to 242 |
| week | `max km one day` | E-7..E-1 | km/day | Maximum running distance on one day of week | 0 to 131 |
| week | `total km Z3-Z4-Z5-T1-T2` | E-7..E-1 | km | Total weekly distance in Z3 or faster; includes sprint exposure in observed weekly aggregation, see reconciliation note | 0 to 100 |
| week | `nr. tough sessions (effort in Z5, T1 or T2)` | E-7..E-1 | sessions | Number of tough sessions containing Z5/T1/T2 effort | 0 to 6 |
| week | `nr. days with interval session` | E-7..E-1 | days | Number of days containing Z3-or-faster interval training | 0 to 7 |
| week | `total km Z3-4` | E-7..E-1 | km | Weekly running distance in Z3-4 | 0 to 79.8 |
| week | `max km Z3-4 one day` | E-7..E-1 | km/day | Maximum Z3-4 running distance in one day | 0 to 75 |
| week | `total km Z5-T1-T2` | E-7..E-1 | km | Weekly running distance in Z5/T1/T2 | 0 to 80 |
| week | `max km Z5-T1-T2 one day` | E-7..E-1 | km/day | Maximum Z5/T1/T2 distance in one day | 0 to 76 |
| week | `total hours alternative training` | E-7..E-1 | hours | Weekly hours of cross training | 0 to 52.5 |
| week | `nr. strength trainings` | E-7..E-1 | sessions | Number of logged strength trainings in week | 0 to 9 |
| week | `avg exertion` | E-7..E-1 | released rating 0-1 | Mean perceived exertion across weekly trainings; source aggregation retained | 0 to 0.98 |
| week | `min exertion` | E-7..E-1 | released rating 0-1 | Minimum perceived exertion across weekly trainings; source aggregation retained | 0 to 0.98 |
| week | `max exertion` | E-7..E-1 | released rating 0-1 | Maximum perceived exertion across weekly trainings; source aggregation retained | 0 to 1 |
| week | `avg training success` | E-7..E-1 | released rating 0-1 | Mean perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `min training success` | E-7..E-1 | released rating 0-1 | Minimum perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `max training success` | E-7..E-1 | released rating 0-1 | Maximum perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `avg recovery` | E-7..E-1 | released rating 0-1 | Mean perceived recovery across weekly trainings; source aggregation retained | 0 to 0.9 |
| week | `min recovery` | E-7..E-1 | released rating 0-1 | Minimum perceived recovery across weekly trainings; source aggregation retained | 0 to 0.9 |
| week | `max recovery` | E-7..E-1 | released rating 0-1 | Maximum perceived recovery across weekly trainings; source aggregation retained | 0 to 1 |
| week | `nr. sessions.1` | E-14..E-8 | sessions | Total completed training sessions in preceding week | 0 to 14 |
| week | `nr. rest days.1` | E-14..E-8 | days | Number of days without a training session in preceding week | 0 to 7 |
| week | `total kms.1` | E-14..E-8 | km | Total weekly running distance | 0 to 235 |
| week | `max km one day.1` | E-14..E-8 | km/day | Maximum running distance on one day of week | 0 to 130 |
| week | `total km Z3-Z4-Z5-T1-T2.1` | E-14..E-8 | km | Total weekly distance in Z3 or faster; includes sprint exposure in observed weekly aggregation, see reconciliation note | 0 to 106.2 |
| week | `nr. tough sessions (effort in Z5, T1 or T2).1` | E-14..E-8 | sessions | Number of tough sessions containing Z5/T1/T2 effort | 0 to 6 |
| week | `nr. days with interval session.1` | E-14..E-8 | days | Number of days containing Z3-or-faster interval training | 0 to 7 |
| week | `total km Z3-4.1` | E-14..E-8 | km | Weekly running distance in Z3-4 | 0 to 85 |
| week | `max km Z3-4 one day.1` | E-14..E-8 | km/day | Maximum Z3-4 running distance in one day | 0 to 75 |
| week | `total km Z5-T1-T2.1` | E-14..E-8 | km | Weekly running distance in Z5/T1/T2 | 0 to 80 |
| week | `max km Z5-T1-T2 one day.1` | E-14..E-8 | km/day | Maximum Z5/T1/T2 distance in one day | 0 to 76 |
| week | `total hours alternative training.1` | E-14..E-8 | hours | Weekly hours of cross training | 0 to 52.5 |
| week | `nr. strength trainings.1` | E-14..E-8 | sessions | Number of logged strength trainings in week | 0 to 9 |
| week | `avg exertion.1` | E-14..E-8 | released rating 0-1 | Mean perceived exertion across weekly trainings; source aggregation retained | 0 to 1 |
| week | `min exertion.1` | E-14..E-8 | released rating 0-1 | Minimum perceived exertion across weekly trainings; source aggregation retained | 0 to 1 |
| week | `max exertion.1` | E-14..E-8 | released rating 0-1 | Maximum perceived exertion across weekly trainings; source aggregation retained | 0 to 1 |
| week | `avg training success.1` | E-14..E-8 | released rating 0-1 | Mean perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `min training success.1` | E-14..E-8 | released rating 0-1 | Minimum perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `max training success.1` | E-14..E-8 | released rating 0-1 | Maximum perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `avg recovery.1` | E-14..E-8 | released rating 0-1 | Mean perceived recovery across weekly trainings; source aggregation retained | 0 to 0.9 |
| week | `min recovery.1` | E-14..E-8 | released rating 0-1 | Minimum perceived recovery across weekly trainings; source aggregation retained | 0 to 0.9 |
| week | `max recovery.1` | E-14..E-8 | released rating 0-1 | Maximum perceived recovery across weekly trainings; source aggregation retained | 0 to 1 |
| week | `nr. sessions.2` | E-21..E-15 | sessions | Total completed training sessions in preceding week | 0 to 14 |
| week | `nr. rest days.2` | E-21..E-15 | days | Number of days without a training session in preceding week | 0 to 7 |
| week | `total kms.2` | E-21..E-15 | km | Total weekly running distance | 0 to 235 |
| week | `max km one day.2` | E-21..E-15 | km/day | Maximum running distance on one day of week | 0 to 135 |
| week | `total km Z3-Z4-Z5-T1-T2.2` | E-21..E-15 | km | Total weekly distance in Z3 or faster; includes sprint exposure in observed weekly aggregation, see reconciliation note | 0 to 150 |
| week | `nr. tough sessions (effort in Z5, T1 or T2).2` | E-21..E-15 | sessions | Number of tough sessions containing Z5/T1/T2 effort | 0 to 6 |
| week | `nr. days with interval session.2` | E-21..E-15 | days | Number of days containing Z3-or-faster interval training | 0 to 7 |
| week | `total km Z3-4.2` | E-21..E-15 | km | Weekly running distance in Z3-4 | 0 to 85 |
| week | `max km Z3-4 one day.2` | E-21..E-15 | km/day | Maximum Z3-4 running distance in one day | 0 to 75 |
| week | `total km Z5-T1-T2.2` | E-21..E-15 | km | Weekly running distance in Z5/T1/T2 | 0 to 52.2 |
| week | `max km Z5-T1-T2 one day.2` | E-21..E-15 | km/day | Maximum Z5/T1/T2 distance in one day | 0 to 30 |
| week | `total hours alternative training.2` | E-21..E-15 | hours | Weekly hours of cross training | 0 to 67.33 |
| week | `nr. strength trainings.2` | E-21..E-15 | sessions | Number of logged strength trainings in week | 0 to 9 |
| week | `avg exertion.2` | E-21..E-15 | released rating 0-1 | Mean perceived exertion across weekly trainings; source aggregation retained | 0 to 0.98 |
| week | `min exertion.2` | E-21..E-15 | released rating 0-1 | Minimum perceived exertion across weekly trainings; source aggregation retained | 0 to 0.98 |
| week | `max exertion.2` | E-21..E-15 | released rating 0-1 | Maximum perceived exertion across weekly trainings; source aggregation retained | 0 to 1 |
| week | `avg training success.2` | E-21..E-15 | released rating 0-1 | Mean perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `min training success.2` | E-21..E-15 | released rating 0-1 | Minimum perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `max training success.2` | E-21..E-15 | released rating 0-1 | Maximum perceived training success across weekly trainings; source aggregation retained | 0 to 1 |
| week | `avg recovery.2` | E-21..E-15 | released rating 0-1 | Mean perceived recovery across weekly trainings; source aggregation retained | 0 to 0.9 |
| week | `min recovery.2` | E-21..E-15 | released rating 0-1 | Minimum perceived recovery across weekly trainings; source aggregation retained | 0 to 0.9 |
| week | `max recovery.2` | E-21..E-15 | released rating 0-1 | Maximum perceived recovery across weekly trainings; source aggregation retained | 0 to 1 |
| week | `Athlete ID` | event day E | identifier | Masked athlete identifier; numeric order is not a biological quantity | 0 to 73 |
| week | `injury` | event day E | binary | Retained injury flag (1) versus selected healthy event (0); see injury_definition.md | 0 to 1 |
| week | `rel total kms week 0_1` | E-21..E-1 subsets | ratio | Released weekly volume ratio; numerator and denominator specified in column name; zero-denominator handling not documented | 0 to 2.096e+08 |
| week | `rel total kms week 0_2` | E-21..E-1 subsets | ratio | Released weekly volume ratio; numerator and denominator specified in column name; zero-denominator handling not documented | 0 to 2.176e+08 |
| week | `rel total kms week 1_2` | E-21..E-1 subsets | ratio | Released weekly volume ratio; numerator and denominator specified in column name; zero-denominator handling not documented | 0 to 2.096e+08 |
| week | `Date` | event day E | relative days | Event day relative to first record in dataset; calendar origin unavailable | 0 to 2673 |
