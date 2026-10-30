# Rooftop-Solar Net-Metering Interconnection Screening Agent

Agentic AI mini-project (26CD7PEAAI), B.E. CSE (Data Science), BMSCE, Sem VII, 2026-27. Instructor: Dr. Kalyan Nagaraj.

| Member | USN |
|---|---|
| Shreejit Shah (Team Lead) | 1BM23CD057 |
| Achintya Karma | 1BM23CD004 |
| Yash Sharma | 1BM23CD070 |
| Soham Padhi | 1BM23CD059 |

**Decision supported:** *"Is this rooftop-solar application complete and admissible for an officer's review, and if not, exactly what is missing or blocking it, with the SOP clause for each point?"* Output is **advisory**; an officer approves everything (human-in-the-loop).

## Run it (Python 3.10+, standard library only, no API key, no internet)
```bash
git clone <repo-url> && cd solar-screener
python run_demo.py                      # guided live demo, press Enter between parts
python -m unittest discover -s tests -v # 10 tests (set PYTHONPATH=src first, see below)
```
Other commands (set the path first: macOS/Linux `export PYTHONPATH=src`, Windows PowerShell `$env:PYTHONPATH="src"`):
```bash
python -m screener.cli screen data/demo/demo_gap_and_recovery.json --show-trace   # one application, full trace
python -m screener.cli eval                                                         # 3-variant A/B on 75-case golden set -> results/
python -m screener.make_data                                                        # regenerate data (seeded, deterministic)
python -m screener.cli queue                                                        # officer review queue
python scripts/make_trace_screenshots.py                                            # regenerate trace screenshots in docs/
```
Optional real-LLM mode (grading and query rewriting by a model; **untested so far**):
`ANTHROPIC_API_KEY=... python -m screener.cli screen <app.json> --llm anthropic` (or `--llm openai` with `OPENAI_BASE_URL` for Ollama).

## What the live demo shows (`run_demo.py`)
1. **Agentic RAG + planning + tool use:** weak retrieval is caught by the grader, the query is rewritten, the right clause is found; the plan is extended after the fast-track band is retrieved; a failed transformer lookup is recovered.
2. **Early stop:** HT consumer is out of scope.
3. **Ablation:** same file through single-shot RAG, basic agent, full agent.
4. **Durable workflow:** crash, then resume from checkpoint.
5. **Evaluation:** 75-case golden set.

## Observability: traces
Every run emits a JSONL trace (`traces/examples/`). Screenshots of real traces are in `docs/`:
- `trace_1_agentic_rag_loop.png` - feedback loop: retrieve, grade, rewrite, retrieve again
- `trace_2_replan_and_tool_recovery.png` - planning (re-plan) + tool use + tool-error recovery
- `trace_3_variants.png` - same application, three variants

## Feedback loops
1. **Retrieval loop:** grade -> rewrite (max 2) -> re-retrieve -> abstain.
2. **Tool-error loop:** lookup fails -> reflect -> normalise id -> retry.
3. **Reflection loop:** citation audit downgrades ungrounded findings to UNVERIFIED.
4. **Officer loop:** drafts go to a review queue; decisions are recorded; resubmissions recall prior outcomes (memory).

## Course checklist mapping
| Concept | Where |
|---|---|
| Tool use | `src/screener/tools.py` |
| Agentic RAG | `agent.py::_agentic_retrieve`, `retriever.py`, `checks.py`, `llm.py` |
| Planning / reasoning | `agent.py::run` (plan-and-execute, re-planning) |
| Observability | `tracing.py` |
| Evaluation + experiment | `evaluate.py`, `oracle.py`, `results/` |
| Human-in-the-loop, guardrails | `hitl.py`, input validation, step and rewrite caps, citation audit |
| Durable workflow, memory | checkpoint/resume in `agent.py`, `memory.py` |
| Multi-agent | deliberately not used (one decision, one evidence trail) |

## Layout
```
src/screener/   agent, checks, retriever, llm, tools, tracing, hitl, memory, oracle, evaluate, make_data, cli
data/           synthetic SOP (sop/), DT register, golden_set.json, demo applications
tests/          unit tests (oracle agreement, no false-PASS, early stop, rewrite and tool recovery, budget, validation, resume, memory/HITL)
results/        experiment_results.json, sensitivity.json, predictions, results.md
traces/examples sample JSONL traces
docs/           figures, trace screenshots, report, design document
deck/, scripts/ slide builders and figure/PDF scripts
```

## Honest caveats
1. The SOP and feeder register are **synthetic/illustrative**. Replace with real BESCOM/KERC documents before any real claim. Clause C1.3 is flagged in the SOP as stricter than national Rule 11(7A).
2. The golden set is synthetic and labelled by `oracle.py`, which shares rules with the SOP text. 100% on it is an in-distribution ceiling, not real-world accuracy.
3. The offline MockLLM's rewrite step knows each check's canonical intent, which flatters the full variant. The real-LLM mode is the proper test.
4. kW is treated as kVA (unity power factor) in transformer loading.
