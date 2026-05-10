# Evaluation Comparison

Smoke-test metrics on a tiny sample dataset; not benchmark results.

| method | mock | EM | F1 | Hit@k | Multi-hop F1 | OOD refusal acc | Unsupported proxy | Avg latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | True | 0.000 | 0.256 | 0.800 | 0.389 | 0.000 | 0.200 | 0.073 |
| rerank | True | 0.000 | 0.263 | 0.800 | 0.389 | 0.000 | 0.200 | 0.001 |
| agentic | True | 0.000 | 0.195 | 0.800 | 0.099 | 1.000 | 0.000 | 0.002 |
