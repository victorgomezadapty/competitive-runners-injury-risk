# Reproduction and publication

The user authorized a public project website, public GitHub source, Kaggle distribution and portfolio inclusion on 2026-10-26. Publication status and verified URLs are recorded in reports/publication_status.json; this document describes the workflow, not proof of successful external publication.

## Local research reproduction

Use Python 3.14 and install requirements.txt. `python scripts/reproduce.py --notebooks` downloads/verifies original data, computes descriptive and predictive results, builds the final exports, runs contracts and executes all authored notebooks. Add `--complementary` for the independent companion source profiles. Exact model-fitting protocols are under config/. Source and output hashes are retained in reports/phase_02/ and reports/final_analysis/. No original article, upstream executable notebook or complementary dataset is silently pooled into modeling.

The website uses static committed web/data.json, original HTML/CSS/JS and generated downloads. `cd web`, `npm test`, `npm run build`; serve web/dist/ using a local static server. No npm dependencies are required for the website build. Vercel uses the root vercel.json. A browser preview requires an HTTP server, not file://.

## Public release contents

GitHub contains authored code, reports, executed notebooks, manifests, licensing and the static website. Raw files remain ignored and are downloaded from the original source. CI downloads originals, checks scientific contracts and builds the site. The source is designed to be reproducible independently of GitHub/Vercel/Kaggle credentials.

Kaggle distribution is built into ignored release/kaggle_dataset/ by scripts/build_release.py. It contains the two unmodified CC0 original CSVs, corrected source README, source manifest, dedicated CC0 table exports, provenance and checksums. No copyrighted articles, third-party figures, upstream notebook, SoccerMon archive or Wu workbook is included. The companion authored notebook independently verifies this bundle and presents saved results; it does not claim to refit the full training pipeline. Its data source is the published bundle; internet and GPU are disabled.

Public upload commands (project owner's accounts only): `kaggle datasets create -p release/kaggle_dataset -u`, then `kaggle kernels push -p release/kaggle_notebook`. Subsequent versions should use platform versioning, not duplicate dataset creation. Do not place credentials in source, command arguments, web assets or release bundles.

## GitHub and Vercel

The intended repository is victorgomezadapty/competitive-runners-injury-risk. Vercel project: competitive-runners-injury-risk. Connect the GitHub repository through `vercel git connect --yes` from the linked checkout. Verify the provider association and a deployment triggered by a pushed commit; a standalone CLI deployment alone does not establish Git-driven deployment.

Before publishing, execute all 11 notebooks, run scientific contracts, verify source/output checksums, scan staged file names for secrets/raw article copies and inspect mobile/desktop plus interactive behavior, ES/EN and reduced motion. Store actual QA outcomes and links without implying unperformed checks.

## License boundaries

See [rights inventory](../DATA_LICENSE.md). Dataset permissions do not license associated publications. Source authorship, project analysis authorship and article authorship remain distinct. Literature discussion is original paraphrase with direct primary-source citations. Data licensing is not clinical authorization.
