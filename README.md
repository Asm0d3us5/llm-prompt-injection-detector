# LLM Prompt Injection Detection & Analysis Platform

A hybrid (rule-based + ML) detection system for identifying and categorizing
prompt injection attacks against LLMs, with MITRE ATLAS technique mapping.

## Status: Week 1 complete — data foundation

- `data/hf_combined.csv` — 1092 labeled samples from HuggingFace
  (`deepset/prompt-injections` + `JasperLS/prompt-injections`)
- `data/manual_samples.csv` — 68 hand-crafted samples across a 6-category
  taxonomy (direct_injection, indirect_injection, jailbreak, token_smuggling,
  prompt_leaking, role_hijack) plus benign/false-positive-bait examples
- `data/atlas_map.json` — maps each category to its MITRE ATLAS technique ID
- `data/train.csv` / `data/eval.csv` — final split, no overlap between sources

## Next: Week 2 — hybrid detection engine (rule-based + ML classifier)
