# Cohort definition

The released Day and Week files each contain **74 unique masked athletes**, computed with `nunique()` on `Athlete ID`. There is no sex/age lookup or event-specialty column. IDs must not be mapped to sex or matched to another dataset.

The study's Subjects section describes 77 initial runners (27 women/50 men). Its Design section explains that filtering leaves 74 (27 women/47 men), matching our directly audited released count. Thus this is an initial-versus-retained cohort discrepancy, not evidence of three missing files. The university portal abstract still reports 77; PubMed and the PDF abstract report 74. The reported retained sex distribution is source-level metadata, not independently verifiable by athlete from these CSVs.

The population is one high-level Dutch middle/long-distance team, approximately 800 m through marathon, mostly national and some international competitors. Source collection is approximately 2012-2019. This is not a recreational-running cohort or external validation across clubs. A stable coach and common recording system may generate team-specific habits.

Selected event rows per athlete: min 43, median 426.5, IQR 269.0-753.0, max 1791. Selected event span (inclusive first-to-last retained day): median 801 days, range 43-2653. This is **not continuous observed follow-up**. Entry, dropout, time injured, missing logs and source exclusions cannot be fully separated.

There are 35,609 athlete-days without a selected event inside retained Day spans. They cannot be assigned healthy labels or rest. See [athlete summary](../reports/tables/day_athlete_summary.csv), [event gaps](../reports/tables/day_observation_gaps.csv), and [reconstructed history](../reports/tables/reconstructed_history_by_athlete.csv) for all athletes.

Sources: [study](https://doi.org/10.1123/ijspp.2020-0518), [university record](https://research.rug.nl/en/publications/injury-prediction-in-competitive-runners-with-machine-learning/), [Dataverse](https://doi.org/10.34894/UWU9PV).
