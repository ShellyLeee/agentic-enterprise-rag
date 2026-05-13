# Evaluation Comparison

Smoke-test metrics on a tiny sample dataset; not benchmark results.

| method | mock | EM | overall_f1 | answerable_f1 | simple_f1 | comparison_f1 | multi_hop_f1 | Hit@k | ood_refusal_accuracy | unsupported_rate | answer_rate | refusal_rate | false_refusals | false_answers | Avg latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | True | 0.000 | 0.256 | 0.318 | 0.331 | 0.200 | 0.389 | 0.800 | 0.000 | 0.200 | 1.000 | 0.000 | 0 | 4 | 0.000 |
| rerank | True | 0.000 | 0.263 | 0.318 | 0.331 | 0.200 | 0.389 | 0.800 | 0.000 | 0.200 | 1.000 | 0.000 | 0 | 4 | 0.000 |
| agentic_aggressive | True | 0.000 | 0.281 | 0.318 | 0.331 | 0.200 | 0.389 | 0.800 | 0.750 | 0.050 | 0.850 | 0.150 | 0 | 1 | 0.000 |
