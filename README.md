# The Afterlife of No

**Refusal, State Memory, and Serial Continuation in Choice of Romance**  
Shivam Gupta · Independent Researcher · 16 October 2026

An executable close reading of the public first episode of *Affairs of the Court: Choice of Romance* by Heather Albano and Adam Strong-Morse (Choice of Games). The study links opposite motive options with identical branch bodies, conditional memory of gift acceptance, and the boundary between romantic closure and serial continuation.

## Results and scope

- 12 public source files, 351,055 bytes, frozen by SHA-256 manifest.
- 10,000 baseline seeded traversals; 5,288 reach the focal poem menu.
- Two further 10,000-play intervention batches: 5,288 comparable reached-state pairs, zero downstream narrative-state mismatches, 27,756 later menu comparisons.
- 43 complete choice sequences in a bounded courtship passage.
- Four coherent observed character profiles, each tested over 101 score inputs: 17,372 local terminal executions.
- Zero disagreements with the independent Python transition model on destination and four checked values.

These are script properties and generated executions. They are not player data or estimates of population behavior. Enumeration is exhaustive only within the specified passage. The full manuscript discusses expressive agency and deliberate dramatic constraints as alternative readings of state equivalence.

## Contents

- `paper/`: full PDF, editable manuscript JSON, conference abstract, biography.
- `src/`: acquisition, engine instrumentation, exhaustive probe, independent analysis, source assertions, figure and PDF generation.
- `data/`: source manifest, reached-state seed inventory, complete scalar witness.
- `results/`: measured summaries and compressed traces. Traces contain source locations and scalar values, not full game prose.
- `figures/`: three vector figures and PNG previews.

## Reproduce

Use Python 3.9+, Node.js 22, Git, and curl. The experiment requires no Python third-party package. Figure generation requires matplotlib and numpy. PDF generation requires reportlab and the Georgia/Arial fonts; the supplied builder uses their standard macOS paths, which can be changed for other platforms.

```sh
python3 src/run_audit.py --cache /absolute/path/to/cache --runs 10000 --mode baseline
python3 src/run_audit.py --cache /absolute/path/to/cache --runs 10000 --mode coy
python3 src/run_audit.py --cache /absolute/path/to/cache --runs 10000 --mode stop
python3 src/source_checks.py --raw /absolute/path/to/cache/raw
```

The engine is pinned to `60a6c3ee7393c9ee7e42650b8e1642ae38e3cb6a`. For the local probe, run this command **from the cache's `engine/` directory**, substituting absolute paths:

```sh
node /absolute/path/to/repository/src/probe_local.js /absolute/path/to/cache/raw /absolute/path/to/repository/results/local.json
```

Then, from this repository:

```sh
python3 src/analyze.py
python3 src/figures.py
python3 src/build_paper.py
```

`analyze.py` reads either uncompressed or gzip-compressed full-play traces. The local probe also accepts the supplied compressed baseline trace.

The harness changes only the local Episode2 file to a terminal marker, recording arrival before any purchase flow. Original files remain in the cache. No purchased scene is fetched or executed. The supplied snapshot manifest is checked before execution: a changed publisher file causes a failure instead of silently changing the corpus.

The upstream engine emits three repeated Apple achievement-title-length warnings per complete play. These are existing metadata warnings in the source; all three 10,000-play batches finished with `RANDOMTEST PASSED`. The retained logs report the terminal result and warning count. Random traversal disables the engine's avoid-used-options heuristic.

## Interpretation and licensing

The paper distinguishes expressed intention, story-relevant executable state, and serial continuation. Diagnostic choice histories and a reader's memory are outside its equivalence claim. Royal relationship scores are not consent scores. Local score perturbations are sensitivity inputs, not claims that all such states are reachable in the complete game.

Code written for this study is MIT licensed. Copyright in the original game and ChoiceScript remains with their respective owners, under their respective terms. They are downloaded separately and are not included or relicensed here. The manuscript is an author's research manuscript, not an accepted conference publication. The IASPR submission is an abstract submission, not submission to a journal or to arXiv.
