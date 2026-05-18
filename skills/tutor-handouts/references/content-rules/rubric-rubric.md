# Rules — Rubric Construction (Meta-rubric)

A grading rubric inside an H3 assignment is "good" iff ALL of these rules pass.
Use `RR-N` rule IDs in quality checklist references.

## Rules

1. **RR-1 (Concrete check per row)** — Every row in the rubric table has a
   concrete check that can be evaluated mechanically. Examples of acceptable
   checks:
   - `./checker.py` exits 0
   - `make test` exits 0
   - All 4 functional tests pass
   - Performance ≥ 80% of reference at N=2^22
   - Generated PDF compiles without errors

   NOT acceptable as the sole check:
   - "code is clean"
   - "good design"
   - "well-organized"
   - "demonstrates understanding"

2. **RR-2 (Concrete check OR concrete sub-criteria for subjective items)** —
   If a row uses a subjective term ("clean", "well-organized", "thoughtful"),
   it MUST be paired with concrete sub-criteria in the same row, e.g.:
   - "Code quality (clean): no functions > 100 lines, no globals, no commented-out blocks"
   - "Writeup quality: ≤ 3 pages, contains a labeled architecture diagram, contains a results table"

3. **RR-3 (Points sum to 100)** — The sum of all per-row points MUST equal
   exactly 100. Sub-totals must also reconcile.

4. **RR-4 (Partial credit boundaries explicit)** — For any test-count check
   (e.g., "N functional tests pass"), the rubric MUST give explicit partial-
   credit boundaries:
   - "3/5 functional tests pass = 6 pts"
   - "4/5 = 8 pts"
   - "5/5 = 10 pts"
   NOT "partial credit at TA discretion".

5. **RR-5 (No 'extra credit > total')** — Extra-credit rows are allowed but
   their total MUST be ≤ 15% of the assignment total.

6. **RR-6 (booktabs table form)** — Rendered as a `booktabs` LaTeX table with
   `\toprule`, `\midrule`, `\bottomrule`. Never as a bulleted list.

7. **RR-7 (Three columns minimum)** — Table MUST have at least:
   - Description (left)
   - Check (middle — the concrete criterion)
   - Points (right, numeric)

## Example: Good Rubric

```latex
\begin{rubricbox}
\begin{tabularx}{\linewidth}{lXr}
  \toprule
  \textbf{Item} & \textbf{Check} & \textbf{Pts} \\
  \midrule
  Compilation & \texttt{make starter} exits 0 & 5 \\
  Correctness & \texttt{make test}: 5/5 functional tests pass (3/5=6 pts, 4/5=8 pts, 5/5=10 pts) & 10 \\
  Performance & \texttt{make bench} ≥ 70\% of reference on H100 (60--70\%=8 pts, 70--80\%=12 pts, ≥80\%=15 pts) & 15 \\
  Correctness invariants & Implementation maintains atomicity per Correctness §5 & 10 \\
  Writeup & PDF, ≤ 3 pp, contains labeled architecture diagram and benchmark table & 10 \\
  \bottomrule
\end{tabularx}
\textit{Total: 50 pts (plus 50 pts from other sections, summing to 100 across the assignment).}
\end{rubricbox}
```

## Example: Bad Rubric (what NOT to emit)

```latex
\begin{itemize}
  \item Good code quality (10 pts)
  \item Correctness (50 pts)
  \item Clear writeup (10 pts)
  \item Performance (30 pts, TA discretion)
\end{itemize}
```

Violations:
- RR-1: no concrete checks
- RR-2: "good", "clear" without sub-criteria
- RR-4: "TA discretion" instead of partial-credit boundaries
- RR-6: bulleted list instead of `booktabs` table
- RR-7: missing Check column

## Enforcement

The skill MUST regenerate any rubric that violates any RR-N rule. The quality
checklist gate for rubrics has explicit per-rule checks.
