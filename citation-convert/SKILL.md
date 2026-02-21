---
name: citation-convert
description: "Fetch BibTeX citations from DOI, arXiv ID, journal URL, or paper title. Covers identifier resolution, BibTeX normalization, batch citation collection, and integration with LaTeX bibliography workflows."
---

# doi2bib3: BibTeX Citation Fetching

## Core Capabilities

### 1. Supported Input Formats

doi2bib3 accepts the following identifier types:

| Input Type | Examples |
|------------|----------|
| Bare DOI | `10.1038/nphys1170` |
| DOI URL | `https://doi.org/10.1038/nphys1170` |
| Modern arXiv ID | `2411.08091`, `arXiv:2411.08091` |
| Legacy arXiv ID | `hep-th/9901001`, `arXiv:hep-th/9901001` |
| arXiv URL | `https://arxiv.org/abs/2411.08091` |
| Publisher URL | `https://www.pnas.org/doi/10.1073/pnas.2305943120` |
| Paper title | `Attention is all you need` |

For arXiv inputs, doi2bib3 queries the arXiv API to find the associated DOI and fetches the published BibTeX. If no DOI exists, it falls back to Crossref search.

### 2. Command-Line Usage

Fetch a single citation and print to stdout:
```bash
doi2bib3 10.1038/nphys1170
```

Save to a file (appends if the file already exists):
```bash
doi2bib3 10.1038/nphys1170 -o references.bib
```

Fetch from an arXiv ID:
```bash
doi2bib3 2411.08091 -o references.bib
```

### 3. Python API

Use `fetch_bibtex` as the primary programmatic interface:

```python
from doi2bib3 import fetch_bibtex

# Basic fetch from DOI
bib = fetch_bibtex('10.1038/nphys1170')

# From arXiv ID
bib = fetch_bibtex('2411.08091')

# From publisher URL
bib = fetch_bibtex('https://www.pnas.org/doi/10.1073/pnas.2305943120')

# Disable normalization (return raw BibTeX from publisher)
bib = fetch_bibtex('10.1038/nphys1170', normalize=False)

# Custom timeout (default 15 seconds)
bib = fetch_bibtex('10.1038/nphys1170', timeout=30)
```

**`fetch_bibtex(identifier, timeout=15, normalize=True) -> str`**
- `identifier`: DOI, arXiv ID, URL, or paper title
- `timeout`: HTTP request timeout in seconds
- `normalize`: Apply BibTeX normalization (journal abbreviation, capitalization protection, special character encoding, citation key generation)
- Returns: BibTeX string
- Raises: `DOIError` for invalid or unresolvable identifiers

### 4. BibTeX Normalization

When `normalize=True` (the default), doi2bib3 applies the following transformations:
- **Citation key generation**: `AuthorLastname_FirstTitleWord_Year` format
- **Journal name abbreviation**: Full names replaced with standard abbreviations (APS, Nature journals)
- **Capitalization protection**: Wraps capitalized words in braces `{Word}` to prevent BibTeX lowercasing
- **LaTeX encoding**: Converts Unicode special characters to LaTeX escape sequences
- **Page range standardization**: Unicode dashes converted to ASCII double-dash `--`
- **Article number fetching**: For APS journals, retrieves article numbers from Crossref

### 5. Batch Workflows

Fetch multiple citations from a file containing one DOI per line:
```bash
while IFS= read -r doi; do
  doi2bib3 "$doi" -o references.bib
  sleep 1  # avoid rate limiting
done < doi_list.txt
```

Python batch processing with error handling:
```python
from doi2bib3 import fetch_bibtex
import time

dois = ['10.1038/nphys1170', '2411.08091', '10.1145/3600006.3613165']
entries = []
for doi in dois:
    try:
        entries.append(fetch_bibtex(doi))
    except Exception as e:
        print(f"Failed for {doi}: {e}")
    time.sleep(1)

with open('references.bib', 'w') as f:
    f.write('\n\n'.join(entries))
```

### 6. Resolution Strategy

doi2bib3 resolves identifiers through a fallback chain:

1. **arXiv detection** - If input matches arXiv pattern, query arXiv API for DOI
2. **DOI normalization** - Extract and validate DOI format (`10.xxxx/yyyy`)
3. **doi.org content negotiation** - Request BibTeX directly from doi.org
4. **Crossref transform** - Use Crossref API to convert DOI to BibTeX
5. **URL DOI extraction** - Scrape publisher pages for DOI metadata tags
6. **Crossref fuzzy search** - Search by title/query string as last resort

This chain ensures maximum coverage across publishers and identifier types.

### 7. Common Pitfalls to Avoid

- **Rate limiting**: Making many rapid requests triggers rate limits from doi.org or Crossref. Add `sleep 1` between batch requests.
- **arXiv-only papers**: Papers without a published DOI fall back to Crossref search, which may return incomplete metadata. Prefer DOIs when available.
- **Normalization artifacts**: Some publisher-specific fields may be altered by normalization. Use `normalize=False` if you need the raw entry.
- **Title search ambiguity**: Searching by title may return the wrong paper if the title is common. Always prefer DOIs or arXiv IDs over title search.

## Workflow for Citation Collection

**Stage 1: Gather identifiers**
1. Collect DOIs from DBLP, ACM Digital Library, or publisher pages
2. Collect arXiv IDs for preprints
3. Store identifiers in a text file (one per line)

**Stage 2: Fetch BibTeX**
1. Run doi2bib3 on each identifier to build `references.bib`
2. Use `normalize=True` for consistent citation keys
3. Add delays between requests to avoid rate limiting

**Stage 3: Integrate with LaTeX**
1. Reference entries using `\cite{AuthorLastname_FirstTitleWord_Year}`
2. Compile with `bibtex` or `biber`
3. Verify all citations resolve correctly

## Skill Combinations

- **doi2bib3 + academic-writing**: Fetch citations while drafting systems conference papers. Use doi2bib3 to collect BibTeX for all cited systems, baselines, and related work.
- **doi2bib3 + better-grep**: Search existing `.bib` files for duplicates before adding new entries. Use `rg "citation_key" references.bib` to check for existing entries.

## References

This skill includes a detailed reference file covering the full API surface and advanced usage patterns:

- `references/doi2bib3-guide.md`: Complete API documentation, internal functions, resolution strategy details, normalization specifics, batch processing patterns, error handling, and LaTeX workflow integration

Load this reference when working with advanced features or troubleshooting resolution failures.
