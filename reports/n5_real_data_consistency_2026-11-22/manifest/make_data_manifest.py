"""P-N5 (gap 2) data manifest: sources, hashes and structure of the two real tables. No model is run.

Reads the downloaded archives and the single extracted members under artifacts/data_real/ (git-ignored) and writes
data_manifest.json next to this file. Data files are never committed.
usage: <venv python> -I make_data_manifest.py
"""
import csv, hashlib, json, zipfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DR = REPO / 'artifacts' / 'data_real'


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def table(path, delim, drop=()):
    rows = list(csv.reader(open(path, encoding='utf-8', newline=''), delimiter=delim))
    hdr, body = rows[0], rows[1:]
    keep = [j for j, h in enumerate(hdr) if h not in drop]
    X = np.array([[float(r[j]) for j in keep] for r in body])
    full_dup = len(body) - len({tuple(r) for r in body})
    kept_dup = len(body) - len({tuple(r[j] for j in keep) for r in body})
    return dict(header_all=hdr, variables_used=[hdr[j] for j in keep], dropped=list(drop), n_rows=len(body),
                n_cols_used=len(keep), all_finite=bool(np.isfinite(X).all()),
                min=[float(v) for v in X.min(0)], max=[float(v) for v in X.max(0)],
                n_unique=[int(len(np.unique(X[:, j]))) for j in range(X.shape[1])],
                n_zero=[int((X[:, j] == 0).sum()) for j in range(X.shape[1])],
                duplicate_rows_all_columns=int(full_dup), duplicate_rows_used_columns=int(kept_dup))


sachs_zip = DR / 'sachs_zenodo_7681811' / 'raw' / 'sachs.zip'
sachs_csv = DR / 'sachs_zenodo_7681811' / 'extracted' / 'cd3cd28.csv'
wine_zip = DR / 'uci_wine_quality_186' / 'raw' / 'wine_quality.zip'
wine_csv = DR / 'uci_wine_quality_186' / 'extracted' / 'winequality-white.csv'
out = dict(
    note='Sources and hashes of the P-N5 real tables; data under artifacts/data_real/ (git-ignored), never committed.',
    sachs=dict(
        source=dict(repository='Zenodo', record='https://zenodo.org/records/7681811', doi='10.5281/zenodo.7681811',
                    concept_doi='10.5281/zenodo.7679091', title='Sachs: Protein and Phospholipids Expressions',
                    creator='Mathematical Research Data Initiative (MaRDI)', published='2023-02-26', license='CC BY 4.0',
                    derived_from='Sachs et al., Science 2005, doi 10.1126/science.1105809',
                    download_url='https://zenodo.org/api/records/7681811/files/sachs.zip/content'),
        archive=dict(file='sachs.zip', bytes=sachs_zip.stat().st_size, md5=md5(sachs_zip), sha256=sha256(sachs_zip),
                     md5_published_by_zenodo='d50ccd7f88bb3705bcf6eda3978bcc41',
                     members=[i.filename for i in zipfile.ZipFile(sachs_zip).infolist()]),
        member_used=dict(name='Data Files/cd3cd28.csv', bytes=sachs_csv.stat().st_size, sha256=sha256(sachs_csv),
                         **table(sachs_csv, ',')),
        not_used='the 13 other condition files, GroundTruth.csv and the description files (not extracted)'),
    wine_white=dict(
        source=dict(repository='UCI Machine Learning Repository', dataset_id=186, page='https://archive.ics.uci.edu/dataset/186/wine+quality',
                    doi='10.24432/C56S3T', title='Wine Quality', license='CC BY 4.0 (dataset page)',
                    creators=['Paulo Cortez', 'A. Cerdeira', 'F. Almeida', 'T. Matos', 'J. Reis'],
                    intro_paper='Cortez et al., Modeling wine preferences by data mining from physicochemical properties, Decision Support Systems, 2009',
                    download_url='https://archive.ics.uci.edu/static/public/186/wine+quality.zip'),
        archive=dict(file='wine_quality.zip', bytes=wine_zip.stat().st_size, md5=md5(wine_zip), sha256=sha256(wine_zip),
                     checksum_published_by_source=None, members=[i.filename for i in zipfile.ZipFile(wine_zip).infolist()]),
        member_used=dict(name='winequality-white.csv', bytes=wine_csv.stat().st_size, sha256=sha256(wine_csv),
                         **table(wine_csv, ';', drop=('quality',))),
        not_used='winequality-red.csv and winequality.names (not extracted)'))
out['sachs']['archive']['md5_matches_zenodo'] = out['sachs']['archive']['md5'] == out['sachs']['archive']['md5_published_by_zenodo']
(HERE / 'data_manifest.json').write_text(json.dumps(out, indent=1))
for k in ('sachs', 'wine_white'):
    m = out[k]['member_used']
    print(k, m['name'], m['n_rows'], 'x', m['n_cols_used'], 'sha256', m['sha256'][:16], 'dups(all/used)',
          m['duplicate_rows_all_columns'], m['duplicate_rows_used_columns'])
print('sachs md5 matches Zenodo:', out['sachs']['archive']['md5_matches_zenodo'])
