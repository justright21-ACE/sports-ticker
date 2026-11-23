#!/usr/bin/env python3
"""High school scores for The FanCave Wire.

Run by .github/workflows/hs-scores.yml every 10 minutes. Reads IHSA's public playoff pages
(plain HTML, updated by IHSA after games) and writes data/hs.json, which the ticker reads.

Football: the IHSA state playoffs, all eight classes (www.ihsa.org/data/fb/<n>pair.htm).
Boys basketball: the IHSA state series, all four classes (www.ihsa.org/data/bkb/<n>pair.htm),
regionals in late February through the state finals in March. The ticker picks which to show.

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

SOURCES = ([{'sport': 'fb', 'cls': '%dA' % n, 'url': 'https://www.ihsa.org/data/fb/%dpair.htm' % n} for n in range(1, 9)] +
           [{'sport': 'bkb', 'cls': '%dA' % n, 'url': 'https://www.ihsa.org/data/bkb/%dpair.htm' % n} for n in range(1, 5)])


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


DASH = r'\s*(?:[—–-]+|:)\s*'          # football: "Game 47 — ..."; basketball: "Game 1: ..."
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


DAYLINE = re.compile(r'^(?:mon|tue|wed|thu|fri|sat|sun)\w*\.?,? (\w+)\.? (\d{1,2})$', re.I)
SECTION = re.compile(r'^(State Final Tournament|.+? (?:Super-Sectional|Sectional|Regional))\b', re.I)
BK_UNPLAYED = re.compile(r'^Game (\d+)' + DASH + r'(.+?) (?:vs\.?|at) (.+?)(?:,? (\d{1,2})(?::(\d\d))? ?([ap])\.?m\.?)?\.?$', re.I)


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:40]


def parse_bkb(src, page, now):
    """IHSA basketball pages: section headers (... Regional / Sectional / Super-Sectional / State Final Tournament),
    day lines ("Mon., Feb. 23"), then "Game N: A 55, B 38" or "Game N: A vs. B, 7:00 pm"."""
    games, sec, day = [], '', None
    for ln in text_lines(page):
        if not ln.lower().startswith('game'):
            m = SECTION.match(ln)
            if m:
                sec, day = m.group(1), None
                continue
        m = DAYLINE.match(ln)
        if m:
            day = (m.group(1), m.group(2))
            continue
        if not sec:
            continue
        low = sec.lower()
        rnd = 'State Finals' if low.startswith('state') else ('Super-Sectional' if 'super' in low else ('Sectional' if low.endswith('sectional') else 'Regional'))
        site = 'Champaign (State Farm Center)' if rnd == 'State Finals' else re.sub(r' (Super-Sectional|Sectional|Regional)$', '', sec, flags=re.I)
        gid = lambda n: '%s-%s-%s-%s-%s' % (src['sport'], src.get('season', ''), src['cls'], slug(sec), n)
        base = {'sport': src['sport'], 'cls': src['cls'], 'round': rnd, 'site': site, 'final': False}
        m = PLAYED.match(ln)
        if m:
            g = dict(base, id=gid(m.group(1)), a={'name': m.group(2).strip(), 'score': int(m.group(3))},
                     b={'name': m.group(4).strip(), 'score': int(m.group(5))}, ot=m.group(6) or '', final=True)
            if day:
                g['date'] = kickoff(day[0], day[1], '12', '0', 'p', now)
            games.append(g)
            continue
        m = BK_UNPLAYED.match(ln)
        if m and not re.search(r'winner|loser', ln, re.I):     # "Winner Game 1 vs. ...": not set yet
            g = dict(base, id=gid(m.group(1)), a={'name': m.group(2).strip()}, b={'name': m.group(3).strip()})
            if day:
                g['date'] = kickoff(day[0], day[1], m.group(4) or '7', m.group(5) or '0', m.group(6) or 'p', now)
            games.append(g)
    return games


def season(page):
    m = re.search(r'Schedule\s*&(?:amp;)?\s*Scores\s*(?:&mdash;|\u2014|-)\s*(\d{4}-\d{2})', page)
    return m.group(1) if m else ''


def parse(src, page, now):
    src = dict(src, season=season(page))
    if src['sport'] == 'bkb':
        return parse_bkb(src, page, now)
    games, rnd = [], ''
    for ln in text_lines(page):
        head = next((r for r in ROUNDS if ln.lower().startswith(r.lower()) and len(ln) < len(r) + 12), None)
        if head:
            rnd = head
            continue
        m = PLAYED.match(ln)
        if m:
            games.append({'id': '%s-%s-%s-%s' % (src['sport'], src.get('season', ''), src['cls'], m.group(1)), 'sport': src['sport'], 'cls': src['cls'],
                          'round': rnd, 'a': {'name': m.group(2).strip(), 'score': int(m.group(3))},
                          'b': {'name': m.group(4).strip(), 'score': int(m.group(5))}, 'ot': m.group(6) or '', 'final': True})
            continue
        m = UNPLAYED.match(ln)
        if m:
            games.append({'id': '%s-%s-%s-%s' % (src['sport'], src.get('season', ''), src['cls'], m.group(1)), 'sport': src['sport'], 'cls': src['cls'],
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
