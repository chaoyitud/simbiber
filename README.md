
# BibTeX Processing Tool

The BibTeX Processing Tool provides functionalities for simplifying, deduplicating, updating, and generating new IDs for BibTeX entries.

## Features:

- **Update BibTeX with DBLP**: This tool can update the entries in your BibTeX file using data from DBLP.
  
- **Deduplication**: The tool offers deduplication of BibTeX entries based on their IDs or titles.
  
- **Simplification**: Simplify the BibTeX entries by removing unnecessary fields.
  
- **Generate New IDs**: It can generate new IDs for BibTeX entries.

- **Logging**: The tool logs operations, providing clarity on the steps being executed.

## Installation:

To install the BibTeX Processing Tool, make sure you have the required dependencies:

```bash
pip install reffix bibtexparser 
```

## Usage:

Run the BibTeX Processing Tool with the desired arguments:

```bash
python main.py [OPTIONS]
```

### Arguments:

- `--input` : Path to the input BibTeX file. Default is "references.bib".
  
- `--output`: Path to the output BibTeX file. Default is "simplified.bib".

- `-u`, `--update`: Update the input BibTeX file with changes.

- `-d`, `--de_title`: Deduplicate entries based on title.

- `-s`, `--simplify`: Simplify the BibTeX entries (e.g., remove unnecessary fields).

- `-i`, `--new_id`: Generate new IDs for BibTeX entries.

For example, to deduplicate and simplify a BibTeX file:

```bash
python main.py --input my_references.bib --de_title --simplify
```

## Output:

- The processed BibTeX will be written to the specified output file.
  
- If deduplication based on title was performed, an additional file `id_mapping.txt` will be generated. This file maps new IDs to their corresponding old IDs.

## Examples:
### Test
```bibtex
@article{zhu2023leadfl,
  title={LeadFL: Client Self-Defense against Model Poisoning in Federated Learning},
  author={Zhu, Chaoyi and Roos, Stefanie and Chen, Lydia Y},
  year={2023}
}

@inproceedings{Zhu:ICML23:LeadFL,
  author       = {Chaoyi Zhu and
                  Stefanie Roos and
                  Lydia Y. Chen},
  title        = {LeadFL: Client Self-Defense against Model Poisoning in Federated Learning},
  booktitle    = {ICML},

  volume       = {202},
  pages        = {43158--43180},
  publisher    = {{PMLR}},
  year         = {2023},
}
```
### Processed
```bibtex
@inproceedings{Zhu:ICML23:LeadFL,
 author = {Chaoyi Zhu and
Stefanie Roos and
Lydia Y. Chen},
 booktitle = {International Conference on Machine Learning, {ICML}},
 pages = {43158--43180},
 title = {{L}ead{F}{L}: {C}lient {S}elf-Defense against {M}odel {P}oisoning in {F}ederated {L}earning},
 volume = {202},
 year = {2023}
}
```
### id_mapping
```text
zhu2023leadfl -> Zhu:ICML23:LeadFL
```