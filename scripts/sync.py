#!/usr/bin/env python3
"""Refresh nflverse releases and optional bookmaker prices; retain last good datasets."""
import csv, io, json, os, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
HEAD={'User-Agent':'FIELD-EDGE-private-site/1.0','Accept':'application/vnd.github+json'}
def request(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=90) as r: return r.read()
def json_get(url):return json.loads(request(url))
def asset(tag,pattern):
    release=json_get(f'https://api.github.com/repos/nflverse/nflverse-data/releases/tags/{tag}')
    matches=[x for x in release['assets'] if re.fullmatch(pattern,x['name'],re.I)]
    if not matches: raise RuntimeError(f'{tag}: matching release asset missing; examples: {[x["name"] for x in release["assets"][:20]]}')
    return matches[0]['browser_download_url']
def csv_rows(url):return list(csv.DictReader(io.StringIO(request(url).decode('utf-8-sig'))))
def write(name,payload):
    p=DATA/name;tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8');tmp.replace(p)
def games():
    rows=csv_rows(asset('schedules',r'games\.csv'))
    wanted=('season','week','game_type','home_team','away_team','home_score','away_score','gameday','game_id','spread_line','total_line')
    rows=[{k:r.get(k,'') for k in wanted} for r in rows if int(r.get('season') or 0)>=2018]
    if len(rows)<500:raise RuntimeError('Unusually small schedule data set')
    write('games.json',{'updated_at':datetime.now(timezone.utc).isoformat(),'source':'nflverse schedules release','rows':rows})
    print('games',len(rows))
def player_stats():
    # Current and last season provide forecasts; no future games may be used for a given forecast.
    season=datetime.now(timezone.utc).year
    columns=('player_display_name','player_name','player_id','season','week','recent_team','team','receptions','receiving_yards','rushing_yards','passing_yards','rushing_tds','receiving_tds')
    allrows=[]
    for y in (season-2,season-1,season):
        # nflverse releases typically publish season-partitioned weekly summaries.
        url=asset('stats_player',rf'stats_player_week_{y}\.csv')
        rows=csv_rows(url)
        if not rows:continue
        if not {'season','week'}.issubset(rows[0]):raise RuntimeError(f'Unexpected {y} player stat columns')
        allrows.extend({k:r.get(k,'') for k in columns} for r in rows)
    if len(allrows)<100:raise RuntimeError('No useful player rows')
    write('players.json',{'updated_at':datetime.now(timezone.utc).isoformat(),'source':'nflverse weekly player summary releases','rows':allrows})
    print('players',len(allrows))
def odds():
    key=os.getenv('ODDS_API_KEY','').strip()
    if not key:
        print('odds: optional ODDS_API_KEY not configured; no odds published')
        return
    import urllib.parse
    root='https://api.the-odds-api.com/v4/sports/americanfootball_nfl'
    q=urllib.parse.urlencode({'apiKey':key,'regions':'us','bookmakers':'draftkings,fanatics','markets':'spreads,totals,h2h','oddsFormat':'american'})
    data=json_get(root+'/odds/?'+q)
    if not isinstance(data,list):raise RuntimeError('Unexpected odds format')
    # Player props on a subset of next games to conserve API quota. Bookmaker availability varies by subscription.
    markets='player_anytime_td,player_receptions,player_reception_yds,player_rush_yds,player_pass_yds'
    enriched=[]
    for g in sorted(data,key=lambda x:x.get('commence_time',''))[:8]:
        url=root+'/events/'+urllib.parse.quote(g['id'])+'/odds?'+urllib.parse.urlencode({'apiKey':key,'regions':'us','bookmakers':'draftkings,fanatics','markets':markets,'oddsFormat':'american'})
        try:
            p=json_get(url);enriched.append({'event_id':g['id'],'bookmakers':p.get('bookmakers',[])})
        except Exception as e:print('props unavailable for',g.get('id'),str(e)[:120])
    write('odds.json',{'updated_at':datetime.now(timezone.utc).isoformat(),'source':'The Odds API','events':data,'props':enriched})
    print('odds',len(data),'events;',len(enriched),'prop requests')
if __name__=='__main__':
    failed=[]
    for f in (games,player_stats):
        try:f()
        except Exception as e:failed.append(f'{f.__name__}: {e}');print('ERROR',failed[-1],file=sys.stderr)
    if failed:sys.exit(1)
