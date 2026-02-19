# Citation Styles for Systems Conference Papers

## Overview

Systems conference papers use numbered citation styles. The two primary formats are IEEE (used by USENIX venues like OSDI and NSDI) and ACM (used by ACM venues like SIGCOMM, MOBICOM, and SOSP). Both use numbered references in square brackets.

## Choosing the Right Style

| Venue | Citation Style | Template |
|-------|---------------|----------|
| OSDI, NSDI, ATC | USENIX (IEEE-like) | USENIX LaTeX template |
| SIGCOMM, MOBICOM, SOSP | ACM | ACM sigconf template |
| EuroSys | ACM | ACM sigconf template |

**Default**: Use the LaTeX template provided by the venue. The template's bibliography style file (`.bst`) handles citation formatting automatically.

## IEEE Style

### Overview
- Used in engineering and computer science
- Numbered citations in square brackets
- References listed numerically in order of first appearance

### In-Text Citations

**Format**: Numbers in square brackets

**Examples:**
```
Several systems have demonstrated this approach [1].

The algorithm was described by Dean and Ghemawat [2] and later improved [3], [4].

Multiple implementations [1]-[4] have been proposed.

Borg [5] and Kubernetes [6] both support container scheduling.
```

**Systems convention**: Name the system when citing:
```
Good:  "Borg [5] uses a centralized scheduler..."
Poor:  "The system described in [5] uses a centralized scheduler..."
```

### Reference List Format

**Conference Papers (most common in systems):**
```
[1] A. A. Author, B. B. Author, and C. C. Author, "Paper title," in Proc.
    USENIX OSDI, City, Year, pp. XX-XX.
```

**Example:**
```
[1] Y. Fu, L. Xue, Y. Huang, A.-O. Brabete, D. Ustiugov, Y. Patel, and
    L. Mai, "ServerlessLLM: Low-latency serverless inference for large language
    models," in Proc. USENIX OSDI, Santa Clara, CA, 2024, pp. 135-152.
```

**Journal Articles:**
```
[2] A. A. Author, B. B. Author, and C. C. Author, "Title of article,"
    Journal Name, vol. X, no. X, pp. XX-XX, Month Year.
```

**Books:**
```
[3] A. A. Author, Book Title, Edition. City, State: Publisher, Year.
```

**Online Sources:**
```
[4] A. A. Author. "Title." Website. URL (accessed Mon. Day, Year).
```

**ArXiv Preprints:**
```
[5] A. A. Author, B. B. Author, and C. C. Author, "Title," arXiv preprint
    arXiv:XXXX.XXXXX, Year.
```

### Special Features
- Abbreviated first and middle names (initials only)
- Uses "and" before last author
- "vol." and "no." before volume and issue
- "pp." before page range
- Month abbreviations: Jan., Feb., Mar., Apr., May, Jun., Jul., Aug., Sep., Oct., Nov., Dec.

## ACM Style

### Overview
- Used by ACM conferences (SIGCOMM, MOBICOM, SOSP, EuroSys)
- The ACM sigconf template uses `acmart.cls` with `\bibliographystyle{ACM-Reference-Format}`
- Numbered citations in square brackets
- References listed alphabetically by first author surname (NOT by order of appearance)

### In-Text Citations

**Format**: Numbers in square brackets, same as IEEE
```
Several systems [1, 3, 7] have addressed this problem.

MapReduce [8] and Spark [15] pioneered large-scale data processing.
```

### Reference List Format

**Conference Papers:**
```
[1] First Author, Second Author, and Third Author. Year. Paper Title.
    In Proceedings of Conference Name (ABBREV 'Year). Publisher, City, Pages.
    https://doi.org/xx.xxxx
```

**Example:**
```
[1] Yao Fu, Leyang Xue, Yeqi Huang, Andrei-Octavian Brabete, Dmitrii
    Ustiugov, Yuvraj Patel, and Luo Mai. 2024. ServerlessLLM: Low-Latency
    Serverless Inference for Large Language Models. In Proceedings of the
    18th USENIX Symposium on Operating Systems Design and Implementation
    (OSDI '24). USENIX Association, Santa Clara, CA, 135-152.
```

### Key Differences from IEEE
- Full first names (not just initials)
- Year appears immediately after authors
- Reference list sorted alphabetically, not by appearance order
- DOIs included when available
- Conference proceedings use "In Proceedings of..." format

## Systems-Specific Citation Conventions

### Cite Systems by Name

Always name the system when citing it. Readers remember system names, not reference numbers.

```
Good:
"Borg [5] and Kubernetes [6] both use container-level scheduling."
"ServerlessLLM [12] exploits locality-aware checkpoint loading."
"Like Megatron-LM [23], our system supports tensor parallelism."

Poor:
"Previous work [5, 6] uses container-level scheduling."
"The approach in [12] exploits locality-aware loading."
```

### Citation Density

| Paper Section | Citation Density | Purpose |
|--------------|-----------------|---------|
| Introduction | High (5-15 citations) | Establish context, cite related problems |
| Background | Moderate (5-10) | Cite foundational work, reference prerequisites |
| Design | Low (2-5) | Cite techniques/algorithms you build on |
| Implementation | Low (2-5) | Cite libraries, frameworks, tools used |
| Evaluation | Moderate (3-8) | Cite all baseline systems compared against |
| Related Work | High (15-25) | Comprehensive coverage of related systems |

**Total**: 30-50 references typical for a 12-page systems paper.

### Recency

- Systems is a fast-moving field; cite recent work (last 3-5 years) heavily
- Seminal/foundational works can be older (MapReduce, Paxos, etc.)
- For active areas (LLM serving, disaggregated memory), cite work from the last 1-2 years
- Avoid citing only old references in an active field; reviewers will notice

### Self-Citation

- Keep self-citations under 20% of total references
- In double-blind submissions, cite own work in third person
- Do not create citation patterns that reveal identity

## Special Publication Types

### ArXiv Preprints
Widely cited in systems research, especially for recent work not yet published.

**IEEE format:**
```
[5] Y. Fu et al., "ServerlessLLM: Locality-enhanced serverless inference for
    large language models," arXiv preprint arXiv:2401.14351, 2024.
```

**BibTeX:**
```bibtex
@article{fu2024serverlessllm,
  title={ServerlessLLM: Locality-Enhanced Serverless Inference for Large
         Language Models},
  author={Fu, Yao and Xue, Leyang and Huang, Yeqi and others},
  journal={arXiv preprint arXiv:2401.14351},
  year={2024}
}
```

### Conference Proceedings

**IEEE/USENIX format:**
```
[3] L. Mai et al., "KungFu: Making training in distributed machine learning
    adaptive," in Proc. USENIX OSDI, 2020, pp. 937-953.
```

**BibTeX for USENIX:**
```bibtex
@inproceedings{mai2020kungfu,
  title={KungFu: Making Training in Distributed Machine Learning Adaptive},
  author={Mai, Luo and Li, Guo and Wagenlander, Marcel and Fertakis,
          Konstantinos and Brabete, Andrei-Octavian and Pietzuch, Peter},
  booktitle={14th USENIX Symposium on Operating Systems Design and
             Implementation (OSDI 20)},
  pages={937--953},
  year={2020}
}
```

**BibTeX for ACM:**
```bibtex
@inproceedings{wagenlander2024tenplex,
  title={Tenplex: Dynamic Parallelism for Deep Learning using Parallelizable
         Tensor Collections},
  author={Wagenl{\"a}nder, Marcel and Li, Guo and Zhao, Bo and Mai, Luo
          and Pietzuch, Peter},
  booktitle={Proceedings of the 30th ACM Symposium on Operating Systems
             Principles (SOSP '24)},
  year={2024},
  publisher={ACM}
}
```

### RFCs and Internet Standards
Common in networking papers (SIGCOMM, NSDI).

```
[7] S. Floyd and V. Jacobson, "Random early detection gateways for congestion
    avoidance," IEEE/ACM Trans. Netw., vol. 1, no. 4, pp. 397-413, Aug. 1993.

[8] J. Postel, "Transmission Control Protocol," RFC 793, Sep. 1981.
```

**BibTeX:**
```bibtex
@misc{rfc793,
  title={Transmission Control Protocol},
  author={Postel, Jon},
  howpublished={RFC 793},
  year={1981}
}
```

### Software and Code Repositories

```
[9] "PyTorch," Meta AI. [Online]. Available: https://pytorch.org/

[10] M. Paszke et al., "PyTorch: An imperative style, high-performance deep
     learning library," in Proc. NeurIPS, 2019, pp. 8024-8035.
```

When citing a framework, prefer citing the associated paper if one exists.

## BibTeX Management

### Getting BibTeX Entries

**Best sources for systems papers:**
1. **DBLP** (dblp.org): Most reliable for CS conferences. Search by author or title.
2. **ACM Digital Library**: Official source for ACM conferences (SIGCOMM, MOBICOM, SOSP)
3. **USENIX Proceedings**: Official source for USENIX venues (OSDI, NSDI, ATC)
4. **Google Scholar**: Click "Cite" then "BibTeX" (verify accuracy)
5. **arXiv**: Click "Export BibTeX Citation" on abstract page

### BibTeX Tips

**Consistent entry keys**: Use a memorable pattern:
```
author-year-keyword: mai2020kungfu, fu2024serverlessllm
```

**Check entries for:**
- Correct venue name and abbreviation
- Complete page numbers
- Correct year (conference vs. arXiv date)
- Proper author name formatting (handle accented characters)
- DOI inclusion (required for ACM)

**During drafting**: Use placeholder citations to mark needed references:
```latex
\cite{TODO-scheduling-baseline}
```

### Reference Management Tools
- **Zotero**: Free, open-source, browser integration, BibTeX export
- **Mendeley**: Free, PDF annotation, BibTeX export
- **JabRef**: Free, Java-based, native BibTeX editor
- **BibDesk** (macOS): Native BibTeX management

### Verifying Citations Before Submission

1. Every `\cite{}` has a corresponding BibTeX entry
2. Every BibTeX entry is cited in the paper
3. No "?" marks in compiled PDF (missing references)
4. Venue names are consistent (don't mix "OSDI" and "USENIX OSDI")
5. Author names are correct (check special characters)
6. Page numbers and years are accurate
7. URLs are functional (for online sources)
8. DOIs are included where required (ACM venues)
9. References compile without BibTeX warnings

## DOI (Digital Object Identifier)

### When to Include
- **ACM venues**: DOIs required for published proceedings
- **USENIX venues**: DOIs optional but recommended
- **ArXiv preprints**: Use arXiv ID instead of DOI

### Format
```
https://doi.org/10.1145/3600006.3613165
```

### Finding DOIs
- ACM Digital Library: Listed on paper page
- CrossRef (crossref.org): Search by title
- DOI.org: Verify DOI resolves correctly

## Pre-Submission Citation Checklist

**Content:**
- [ ] 30-50 references for a 12-page paper
- [ ] Recent work cited (last 3-5 years for active areas)
- [ ] Self-citations under 20%
- [ ] All baseline systems in evaluation are cited
- [ ] Seminal foundational works included
- [ ] Systems cited by name, not just number

**Format:**
- [ ] Citation style matches venue template exactly
- [ ] All `\cite{}` resolved (no "?" in PDF)
- [ ] BibTeX entries consistent (venue names, author format)
- [ ] DOIs included where required
- [ ] Page numbers included for published papers
- [ ] ArXiv preprints formatted correctly

**Double-blind venues (SIGCOMM, MOBICOM, SOSP):**
- [ ] Own work cited in third person
- [ ] No self-identifying citation patterns
- [ ] Anonymous repository URLs (or omitted)
