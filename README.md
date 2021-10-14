# qpu-access-accum

Python module to accumulate qpu access time of D-Wave quantum annealers in Google Spreadsheet.

Valid child samplers:

- DWaveSampler
- DWaveCliqueSampler
- EmbeddingComposite
- FixedEmbeddingComposite
- LeapHybridSampler
- LeapHybridCQMSampler
- LeapHybridDQMSampler

## Preparation

You should prepare with a spreadsheet with [Google Sheet API](https://developers.google.com/sheets/api), whose format is [here](examples/spreadsheet_format.gsheet.csv).

## Installation

```
$ pip install git+https://github.com/mullzhang/qpu-access-accum.git
```

## usage

[Example of QUBO using DWaveCliqueSampler](examples/example.py)

```python
from qpu_access_accum import QPUAccessAccumComposite

accum_conifg = dict(username='NAME',
                    keyfile_path='API_KEY.json',
                    spreadsheet_key='SPREADSHEET_KEY',
                    worksheet_index=0)

sampler = QPUAccessAccumComposite(child_sampler, **accum_config)
sampleset = sampler.sample(bqm, **sampler_params)

```
