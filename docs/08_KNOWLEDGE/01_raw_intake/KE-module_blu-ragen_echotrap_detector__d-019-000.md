---
module_id: KE-module_blu-ragen_echotrap_detector__d-019-000
title: RAGEN EchoTrap Detector (D-019-73)
category: module_blueprint
---

# RAGEN EchoTrap Detector (D-019-73)

RAGEN EchoTrap Detector (D-019-73)
- 4 signals: reward_variance_collapse + gradient_spike + policy_entropy_decay + output_homogeneity
- EchoTrapScore > 0.7 → PAUSE self-evolution + inject external signal + human review
- Faithfulness check: perturbation test → if behavior unchanged → experience NOT faithfully used
- Collapse Recovery: revert to checkpoint + inject diversity noise + human reviews
