#!/usr/bin/env python3
"""High school scores for The FanCave Wire.

Run by .github/workflows/hs-scores.yml every 10 minutes. Reads IHSA's public playoff pages
(plain HTML, updated by IHSA after games) and writes data/hs.json, which the ticker reads.

Football: the IHSA state playoffs, all eight classes (www.ihsa.org/data/fb/<n>pair.htm).
Basketball: not yet (regular-season Top 25 needs a live source such as ScoreStream; the IHSA
state series pages can be added here when IHSA posts them in February).

Only the standard library, so the workflow needs no installs.
"""
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'hs.json')
UA = 'Mozilla/5.0 (FanCave Wire ticker; scores for a home TV)'
CENTRAL = timezone(timedelta(hours=-6))          # IHSA times are Central; playoffs are in standard time (Nov / Feb-Mar)
MONTHS = {m: i + 1 for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}
ROUNDS = ['Opening Round', 'First Round', 'Second Round', 'Quarterfinals', 'Semifinals', 'Championship', 'Third Place', 'Finals']

SOURCES = [{'sport': 'fb', 'cls': '%dA' % n, 'url': 'https://www.ihsa.org/data/fb/%dpair.htm' % n} for n in range(1, 9)]


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def text_lines(page):
    """HTML to lines of text: one table row / paragraph / list item per line."""
    page = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', page)
    page = re.sub(r'(?i)<\s*(br|/tr|/p|/li|/div|/h\d|/table)\b[^>]*>', '\n', page)
    page = re.sub(r'<[^>]+>', ' ', page)
    page = html.unescape(page).replace('\xa0', ' ')
    return [re.sub(r'\s+', ' ', ln).strip() for ln in page.split('\n') if ln.strip()]


DASH = r'\s*[—–-]+\s*'
PLAYED = re.compile(r'^Game (\d+)' + DASH + r'(.+?) (\d+), (.+?) (\d+)(?: \(([^)]*OT[^)]*)\))?\.?$', re.I)
UNPLAYED = re.compile(r'^Game (\d+)' + DASH + r'(.+?)(?: \((\d+-\d+)\))? (vs\.?|at) (.+?)(?: \((\d+-\d+)\))? at (.+?), '
                      r'(?:\w+\.?,? )?(\w+)\.? (\d{1,2}),? (\d{1,2})(?::(\d\d))? ?([ap])\.?m\.?', re.I)
TBD = re.compile(r'^Game (\d+)' + DASH + r'(.+)$', re.I)


def kickoff(mon, day, hh, mm, ap, now):
    m = MONTHS.get(mon[:3].lower())
    if not m:
        return None
    h = int(hh) % 12 + (12 if ap.lower() == 'p' else 0)
    y = now.year if not (now.month >= 11 and m <= 3) else now.year + 1
    return datetime(y, m, int(day), h, int(mm or 0), tzinfo=CENTRAL).isoformat()


def parse(src, page, now):
    games, rnd = [], ''
    for ln in text_lines(page):
        head = next((r for r in ROUNDS if ln.lower().startswith(r.lower()) and len(ln) < len(r) + 12), None)
        if head:
            rnd = head
            continue
        m = PLAYED.match(ln)
        if m:
            games.append({'id': '%s-%s-%s' % (src['sport'], src['cls'], m.group(1)), 'sport': src['sport'], 'cls': src['cls'],
                          'round': rnd, 'a': {'name': m.group(2).strip(), 'score': int(m.group(3))},
                          'b': {'name': m.group(4).strip(), 'score': int(m.group(5))}, 'ot': m.group(6) or '', 'final': True})
            continue
        m = UNPLAYED.match(ln)
        if m:
            games.append({'id': '%s-%s-%s' % (src['sport'], src['cls'], m.group(1)), 'sport': src['sport'], 'cls': src['cls'],
                          'round': rnd, 'a': {'name': m.group(2).strip(), 'rec': m.group(3) or ''},
                          'b': {'name': m.group(5).strip(), 'rec': m.group(6) or ''}, 'neutral': m.group(4).lower().startswith('vs'),
                          'site': m.group(7).strip(), 'date': kickoff(m.group(8), m.group(9), m.group(10), m.group(11), m.group(12), now),
                          'final': False})
    return games


def main():
    now = datetime.now(CENTRAL)
    try:
        old = {g['id']: g for g in json.load(open(OUT)).get('games', [])}
    except Exception:
        old = {}
    games, errors = [], []
    for src in SOURCES:
        try:
            got = parse(src, fetch(src['url']), now)
            print('%s %s: %d games' % (src['sport'], src['cls'], len(got)))
            games += got
        except Exception as e:                       # a page that fails keeps its last games
            errors.append('%s: %s' % (src['url'], e))
            games += [g for g in old.values() if g['sport'] == src['sport'] and g['cls'] == src['cls']]
        time.sleep(1)
    stamp = now.isoformat(timespec='seconds')
    for g in games:                                  # carry over what a final line no longer says: the kickoff, records, site
        o = old.get(g['id'])
        if o:
            for k in ('date', 'site', 'neutral'):
                if k not in g and k in o:
                    g[k] = o[k]
            for s in ('a', 'b'):
                if not g[s].get('rec'):
                    for t in ('a', 'b'):
                        if o[t]['name'] == g[s]['name'] and o[t].get('rec'):
                            g[s]['rec'] = o[t]['rec']
            g['finalAt'] = o.get('finalAt') or (stamp if g['final'] and not o.get('final') else None)
        else:
            g['finalAt'] = None                      # already final the first time it's seen: an old result
    out = {'updated': stamp, 'source': 'IHSA', 'errors': errors, 'games': games}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    new = json.dumps(out, indent=1, sort_keys=True)
    try:
        prev = json.load(open(OUT))
        prev['updated'] = stamp
        if json.dumps(prev, indent=1, sort_keys=True) == new:
            print('no change')
            return 0
    except Exception:
        pass
    open(OUT, 'w').write(new + '\n')
    print('wrote %d games, %d errors' % (len(games), len(errors)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
