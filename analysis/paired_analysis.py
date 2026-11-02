#!/usr/bin/env python3
"""Paired re-analysis of the EvoMemBench subset replication.

All six cells ran the SAME 50 Gorilla File System task ids, so gains are
analyzed as paired per-task differences (not independent proportions).
Reads data/full_results.json and data/per_sample/<cell>.csv from this
bundle and prints: success counts, cost shares, discordant pairs vs the
same-budget no-memory arm, and paired-bootstrap 95% CIs for the gain
shrinkage between 16K and 128K (10,000 resamples over tasks, seed fixed).
"""
import csv, json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CELLS = ['a0_16k', 'a0_128k', 'bm25_16k', 'bm25_128k', 'ace_16k', 'ace_128k']

fr = json.load(open(os.path.join(ROOT, 'data', 'full_results.json')))
tot_in = sum(fr[c]['input_tokens'] for c in CELLS)
ace_in = fr['ace_16k']['input_tokens'] + fr['ace_128k']['input_tokens']
mem = fr['ace_16k']['memory_tokens'] + fr['ace_128k']['memory_tokens']
a0o = fr['a0_16k']['output_tokens'] + fr['a0_128k']['output_tokens']
aceo = fr['ace_16k']['output_tokens'] + fr['ace_128k']['output_tokens']
print('== cost shares (from full_results.json) ==')
print(f'total input {tot_in:,} | ACE own input {ace_in:,} | ACE memory-module {mem:,}')
print(f'memory / total input = {mem / tot_in * 100:.2f}% | memory / ACE own input = {mem / ace_in * 100:.2f}%')
print(f'ACE output {aceo:,} / A0 output {a0o:,} = {aceo / a0o:.2f}x')

def load(cell):
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'per_sample', cell + '.csv'))))
    return {r['id']: int(r['success']) for r in rows}

cells = {c: load(c) for c in CELLS}
ids = sorted(cells['a0_16k'])
assert all(sorted(cells[c]) == ids for c in cells), 'task id sets differ across cells'
print(f'\n== paired analysis (same {len(ids)} task ids in all six cells) ==')
print('successes:', {c: sum(cells[c].values()) for c in CELLS})
random.seed(20261102)
for arm in ['bm25', 'ace']:
    g16 = [cells[f'{arm}_16k'][i] - cells['a0_16k'][i] for i in ids]
    g128 = [cells[f'{arm}_128k'][i] - cells['a0_128k'][i] for i in ids]
    shrink = [a - b for a, b in zip(g16, g128)]
    bs = sorted(sum(shrink[random.randrange(50)] for _ in range(50)) / 50 * 100 for _ in range(10000))
    print(f'{arm}: gain@16K {sum(g16) / 50 * 100:+.1f} (wins {sum(1 for x in g16 if x == 1)}, losses {sum(1 for x in g16 if x == -1)}), '
          f'gain@128K {sum(g128) / 50 * 100:+.1f} (wins {sum(1 for x in g128 if x == 1)}, losses {sum(1 for x in g128 if x == -1)}), '
          f'shrinkage {sum(shrink) / 50 * 100:+.1f} pts, paired-bootstrap 95% CI [{bs[250]:+.1f}, {bs[9750]:+.1f}]')
d = {a: sum(cells[f'{a}_128k'][i] - cells[f'{a}_16k'][i] for i in ids) for a in ['a0', 'bm25', 'ace']}
print(f"raw 16K->128K moves (tasks): A0 {d['a0']:+d}, BM25 {d['bm25']:+d}, ACE {d['ace']:+d}")
