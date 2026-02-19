# doi2bib3 Detailed Reference Guide

## Installation

### pip (recommended)
```bash
pip install --user doi2bib3
```

### From source
```bash
git clone https://github.com/archisman-panigrahi/doi2bib3.git
cd doi2bib3
pip install .
```

### Verify installation
```bash
doi2bib3 10.1038/nphys1170
```

## Public API

### `fetch_bibtex(identifier, timeout=15, normalize=True) -> str`

The primary entry point. Accepts any supported identifier format and returns a BibTeX string.

**Parameters:**
- `identifier` (str): DOI, arXiv ID, URL, or paper title
- `timeout` (int): HTTP request timeout in seconds (default: 15)
- `normalize` (bool): Apply BibTeX normalization (default: True)

**Returns:** BibTeX-formatted string

**Raises:** `DOIError` for invalid or unresolvable identifiers

**Examples:**
```python
from doi2bib3 import fetch_bibtex

# DOI
bib = fetch_bibtex('10.1038/nphys1170')

# arXiv (resolves to published DOI if available)
bib = fetch_bibtex('2411.08091')
bib = fetch_bibtex('arXiv:2411.08091')
bib = fetch_bibtex('https://arxiv.org/abs/2411.08091')

# Legacy arXiv
bib = fetch_bibtex('hep-th/9901001')

# Publisher URL
bib = fetch_bibtex('https://www.pnas.org/doi/10.1073/pnas.2305943120')

# Paper title (fuzzy search via Crossref)
bib = fetch_bibtex('Attention is all you need')

# Raw BibTeX without normalization
bib = fetch_bibtex('10.1038/nphys1170', normalize=False)
```

## Internal Functions

These are available from `doi2bib3.backend` and `doi2bib3.utils` for advanced use.

### Backend Functions (`doi2bib3.backend`)

**`normalize_doi(doi_input: str) -> str`**
Extracts and validates a DOI from various input formats. Accepts bare DOIs, `doi:` prefixed strings, and HTTP URLs. Validates against the pattern `10.xxxx/yyyy`. Raises `DOIError` for invalid input.

**`get_bibtex_from_doi(doi: str, timeout: int = 15) -> str`**
Core resolution function. Detects arXiv IDs, attempts doi.org content negotiation, falls back to Crossref transform, then Crossref search. Returns raw BibTeX string.

**`arxiv_to_doi(arxivid: str, timeout: int = 15) -> Optional[str]`**
Queries arXiv API for the published DOI associated with an arXiv paper. Returns `None` if no DOI is linked.

**`crossref_search_for_doi(query: str, timeout: int = 15) -> Optional[str]`**
Searches Crossref API by query string. Parses publisher pages for DOI metadata as fallback. Returns the highest-scored DOI match.

**`DOIError`**
Custom exception raised for invalid DOI formats or resolution failures.

### Utility Functions (`doi2bib3.utils`)

**`normalize_bibtex(bib_str: str) -> str`**
Comprehensive BibTeX normalization:
- Regenerates citation key as `AuthorLastname_FirstTitleWord_Year`
- Standardizes page ranges (unicode dashes to `--`)
- Fetches article numbers for APS journals
- Decodes URLs and removes DOI field when URL is present
- Encodes special characters to LaTeX

**`abbreviate_journal_name(journal: str) -> str`**
Replaces full journal names with standard abbreviations using bundled replacement dictionaries (APS and Nature journals).

**`protect_capitalized_words(title: str) -> str`**
Wraps capitalized words in braces to prevent BibTeX style files from lowercasing them. Preserves already-braced content and handles hyphenated words.

**`encode_special_chars(value: str) -> str`**
Converts Unicode characters to LaTeX escape sequences (e.g., `ö` to `\"{o}`).

**`insert_dollars(title: str) -> str`**
Wraps LaTeX math commands in dollar signs for proper rendering in BibTeX titles.

**`save_bibtex_to_file(bib_str: str, path: str, append: bool = False) -> None`**
Writes BibTeX to a file. Uses append mode when the file already exists.

**`cli_doi2bib3(argv=None)`**
Programmatic CLI invocation. Useful for testing or scripting.

## CLI Reference

```
doi2bib3 IDENTIFIER [-o OUTPUT_FILE]
```

**Arguments:**
- `IDENTIFIER`: DOI, arXiv ID, URL, or paper title (required)
- `-o, --out OUTPUT_FILE`: Write BibTeX to file instead of stdout. Appends if file exists.

**Exit codes:**
- 0: Success
- Non-zero: Resolution failure or invalid input

## Resolution Strategy Details

### Step 1: arXiv Detection
The tool checks if the input matches any arXiv pattern:
- Modern format: `YYMM.NNNNN[vN]` (e.g., `2411.08091`, `2411.08091v2`)
- Legacy format: `subject-class/YYMMNNN` (e.g., `hep-th/9901001`)
- URL forms: `arxiv.org/abs/...`, `arxiv.org/pdf/...`, `arxiv.org/html/...`
- Prefixed: `arXiv:...`

If detected, queries `http://export.arxiv.org/api/query?id_list={arxiv_id}` for the associated DOI.

### Step 2: DOI Normalization
Extracts DOI from the input. Accepts:
- Bare DOI: `10.1038/nphys1170`
- doi: prefix: `doi:10.1038/nphys1170`
- URL: `https://doi.org/10.1038/nphys1170`

Validates that the result matches the DOI pattern `10.\d{4,}/...`.

### Step 3: doi.org Content Negotiation
Sends an HTTP request to `https://doi.org/{doi}` with `Accept: application/x-bibtex` header. Most publishers respond with BibTeX directly.

### Step 4: Crossref Transform
If doi.org fails, tries `https://api.crossref.org/works/{doi}/transform/application/x-bibtex`.

### Step 5: Publisher Page Scraping
For URL inputs that aren't DOIs, scrapes the page for:
- `<meta name="citation_doi">` tags
- `<meta name="dc.identifier" scheme="doi">` tags
- DOI patterns in `href` attributes

### Step 6: Crossref Fuzzy Search
As a last resort, queries `https://api.crossref.org/works?query={input}` and returns the BibTeX for the highest-scored result.

## Normalization Details

### Citation Key Format
Generated as `AuthorLastname_FirstTitleWord_Year`:
- Author: Last name of the first author
- Title: First significant word from the title
- Year: Publication year

Example: `Einstein_Relativity_1905`

### Journal Abbreviation
Bundled replacement dictionaries cover:
- **APS journals**: Physical Review Letters, Physical Review A-E, Reviews of Modern Physics, etc.
- **Nature journals**: Nature, Nature Physics, Nature Materials, etc.

Matching is case-insensitive with exact-match priority.

### Capitalization Protection
Words starting with an uppercase letter are wrapped in braces:
- `GPU` becomes `{GPU}`
- `Monte-Carlo` becomes `{Monte}-{Carlo}`
- Already-braced words are preserved

### Special Character Encoding
Common conversions:
- `ö` → `\"{o}`
- `é` → `\'{e}`
- `ñ` → `\~{n}`
- `ü` → `\"{u}`

## Batch Processing Patterns

### Build .bib from DOI list file
```bash
# doi_list.txt: one DOI per line
while IFS= read -r doi; do
  echo "Fetching: $doi"
  doi2bib3 "$doi" -o references.bib
  sleep 1  # avoid rate limiting
done < doi_list.txt
```

### Python: Collect citations with error handling
```python
from doi2bib3 import fetch_bibtex
import time

identifiers = [
    '10.1145/3600006.3613165',   # SOSP paper
    '2411.08091',                 # arXiv preprint
    '10.1145/3230543.3230563',   # SIGCOMM paper
]

results = []
for ident in identifiers:
    try:
        bib = fetch_bibtex(ident)
        results.append(bib)
        print(f"OK: {ident}")
    except Exception as e:
        print(f"FAIL: {ident} - {e}")
    time.sleep(1)

with open('references.bib', 'w') as f:
    f.write('\n\n'.join(results))

print(f"Wrote {len(results)} entries to references.bib")
```

### Python: Fetch without normalization for manual editing
```python
from doi2bib3 import fetch_bibtex

# Get raw BibTeX to inspect publisher metadata
raw = fetch_bibtex('10.1145/3600006.3613165', normalize=False)
print(raw)

# Get normalized version for direct use
normalized = fetch_bibtex('10.1145/3600006.3613165', normalize=True)
print(normalized)
```

## Error Handling

### DOIError
Raised when:
- Input cannot be parsed as a valid DOI
- No DOI found for an arXiv paper and Crossref search fails
- All resolution backends fail

```python
from doi2bib3 import fetch_bibtex
from doi2bib3.backend import DOIError

try:
    bib = fetch_bibtex('invalid-identifier')
except DOIError as e:
    print(f"Resolution failed: {e}")
```

### Network Errors
Timeout or connectivity issues raise standard `requests` exceptions. Use the `timeout` parameter to control wait time:

```python
bib = fetch_bibtex('10.1038/nphys1170', timeout=30)  # longer timeout
```

## Integration with LaTeX Workflows

### Typical workflow
1. Identify papers to cite (DOIs from DBLP, arXiv, or publisher pages)
2. Fetch BibTeX entries with doi2bib3
3. Save to `references.bib`
4. Reference in LaTeX with `\cite{AuthorLastname_FirstTitleWord_Year}`
5. Compile with `bibtex` or `biber`

### With the acamedic-writing skill
When writing systems conference papers:
- Use doi2bib3 to fetch entries for all cited systems and baselines
- The normalized citation keys follow a consistent `Author_Title_Year` pattern
- Verify abbreviations match venue requirements (IEEE vs ACM)
- Check that all evaluation baselines have corresponding BibTeX entries

## Project Information

- **Repository**: https://github.com/archisman-panigrahi/doi2bib3
- **License**: GPL-3.0
- **Python**: 3.9+
- **Dependencies**: requests, bibtexparser
