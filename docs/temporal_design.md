# Temporal design

E = selected event day; t = E-1 = end of information available before the target. The existing target is the flag at E, not a seven-day outcome. The study phrases its question as the next training session; the released Date refers to an event day. We retain the explicit event-day endpoint and do not assume every day has a scheduled session.

Day Approach: seven consecutive daily feature blocks E-7..E-1 within each row. Corrected suffix order is 0..6 from oldest to newest. Week Approach: three weekly blocks, newest week 0, then 1 and 2. Weekly windows advance with each event day, not only at calendar-week boundaries.

## Two different longitudinal objects

1. **Event table**: selected injury/healthy days with embedded earlier history. Suitable for conditional retrospective classification after review.
2. **Retrospective exposure reconstruction**: de-duplicated athlete-training days recovered from embedded histories. Used for timelines and distributions only. A day can be recovered from a future source event row; its inclusion must not be treated as prospective availability.

No raw continuous training log is provided. Retained-date gaps can arise from injury filtering, missing/anomalous data removal, absent logging or attendance, and other selection. These cannot be disentangled. The relative Date origin is not released as a calendar date. Negative reconstructed indices are legitimate earlier history, not fabricated pre-2012 dates.

## Phase 2 validation design proposal, not executed

- A: Known-athlete future estimation. Use explicit global relative-day cutoffs; report athletes with sufficient history on each side. Retain temporal order and a separate calibration period. Do not use a random row split.
- B: Unseen-athlete estimation. Outer athlete-disjoint groups; all outcomes from a held-out athlete remain outside fitting/tuning/calibration. Personal adaptation, if later considered, must use only prior unlabeled information and be evaluated as a separate protocol.
- C: Athlete-disjoint plus time-constrained validation if enough events remain. Do not infer recruitment order from numeric masked IDs.

For temporal boundaries, purge training events whose exposure histories overlap test exposure histories. At least a 7-day or 21-day input-span embargo, according to the representation, is required under a strict non-overlap design; account for longer future outcome horizons separately. Non-overlapping test histories are a useful sensitivity analysis, not an automatic replacement for the intended deployment estimand.

No new horizon is created from absent event days. A complete incident-injury registry would be needed for reliable 3/7-day outcomes, lead-time evaluation, false alerts per true athlete-month, or prospective operational calibration. Label-selected controls already use future fitness; fold-level safeguards do not repair that upstream selection.
