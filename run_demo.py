"""One-command demo for reviews. Run from the project folder:  python run_demo.py   (press Enter between parts)"""
import json, sys, tempfile, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from screener.agent import ScreeningAgent, CrashSimulated

def pause(msg):
    print("\n" + "=" * 78 + "\n" + msg + "\n" + "=" * 78)
    try: input("[Enter to run] ")
    except EOFError: pass

def show(ev):
    keep = {"plan", "replan", "thought", "retrieve", "grade", "rewrite", "extract", "action", "observation", "finding", "reflect", "decision", "guardrail"}
    for e in ev:
        if e["kind"] in keep:
            body = {k: v for k, v in e.items() if k not in ("run_id", "step", "t", "kind")}
            print(f"[{e['step']:02d}] {e['kind']:<11} {json.dumps(body)[:150]}")

def load(name): return json.loads((ROOT / "data/demo" / name).read_text())

pause("PART 1: Agentic RAG + re-planning + tool-error recovery (14 kW, 'family member living rent-free', mistyped DT id)")
r = ScreeningAgent("agentic_full").run(load("demo_gap_and_recovery.json"))
show(r["trace"]); print("\n" + r["explanation"]); print("metrics:", r["metrics"])

pause("PART 2: Early stop - HT consumer is out of scope (agent stops sensibly)")
r = ScreeningAgent("agentic_full").run(load("demo_out_of_scope.json"))
show(r["trace"]); print("\n" + r["explanation"])

pause("PART 3: Same application, weaker variants - single-shot RAG silently misses the defect")
app = load("demo_gap_and_recovery.json")
for v in ("naive", "agentic_basic", "agentic_full"):
    r = ScreeningAgent(v).run(app); print(f"{v:<14} -> {r['verdict']:<13} codes={r['codes']}")

pause("PART 4: Durable workflow - crash after 4 checks, then resume from checkpoint")
d = tempfile.mkdtemp()
ag = ScreeningAgent("agentic_full", ckpt_dir=d)
try: ag.run(app, crash_after=4)
except CrashSimulated as e: print("CRASH:", e)
r = ag.run(app, resume=True)
print("resumed; already done:", [e for e in r["trace"] if e["kind"] == "resume"][0]["already_done"]); print("verdict:", r["verdict"])
shutil.rmtree(d, ignore_errors=True)

pause("PART 5: Evaluation - 3-variant A/B on the 75-case golden set")
from screener.evaluate import run_experiment, to_markdown
res, _ = run_experiment(out_dir=tempfile.mkdtemp()); print(to_markdown(res))
