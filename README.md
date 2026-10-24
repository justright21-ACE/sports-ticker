# Sports Ticker

Full-screen live sports scoreboard for an old Samsung web-enabled monitor.

Live page: https://justright21-ace.github.io/sports-ticker/

Data (both free, no API key):
- SportsBlaze: NFL, NBA, MLB, WNBA
- ESPN scoreboard feed: NCAA football, UFC main card fights (also NCAA men's basketball and NHL)

Each card also shows the opening spread and over/under (DraftKings, via ESPN) when available.

Options go on the end of the address:
- Favorites are set per league in the CONFIG block (Bears, Eagles, USC, Wisconsin, Spurs, Bulls, White Sox)
- `?fav=DAL,TEX` override favorites for every league
- `?leagues=nfl,ncaaf,nba` choose leagues (nfl, ncaaf, nba, mlb, wnba, ncaab, nhl)
- `?cfb=fbs` every FBS college football game instead of just ranked-team games
- `?rotate=20` seconds per screen
- `?theme=bears`, `?theme=usc` or `?theme=classic` force a color scheme (default `auto`: Bears Sunday-Friday, USC on Saturday)
- `?stats=0` / `?news=0` turn off key stats or headlines in the bottom bar
- `?demo=1` fake games to test the layout
