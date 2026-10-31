# The FanCave Wire

Full-screen live sports scoreboard for an old Samsung web-enabled monitor.

Live page: https://justright21-ace.github.io/sports-ticker/

Data (both free, no API key):
- ESPN scoreboard feed (main source for every league)
- SportsBlaze: backup for NFL, NBA, MLB, WNBA if ESPN can't be reached
- ESPN scoreboard feed: NCAA football, UFC + PFL main card fights for the COMBAT tab (also NCAA men's basketball and NHL)
- TheSportsDB (free key): major boxing cards on the COMBAT tab (scheduled time and result; no live round-by-round)

Each card also shows the opening spread and over/under (DraftKings, via ESPN) when available.

Options go on the end of the address:
- Favorites are set per league in the CONFIG block (Bears, Eagles, USC, Wisconsin, Spurs, Bulls, White Sox, Blackhawks)
- Every USC or Wisconsin football game gets the primetime-style game-day screen and its own tab, kept 30 minutes after the final (`?gameday=0` turns it off, `?gamedayafter=45` changes the minutes)
- A Top 25 college game within one score (8 pts) in the 4th quarter or overtime gets its own CLOSE screen, 30 seconds a time (`?close=0` turns it off)
- A league drops off the top bar once its season is over (champion decided or ESPN says off-season), after the title game result has been up 12 hours; it comes back on its own next season (`?ended=1` keeps every tab)
- `?fav=DAL,TEX` override favorites for every league
- `?leagues=nfl,ncaaf,nba` choose leagues (nfl, ncaaf, nba, mlb, wnba, ncaab, nhl)
- NHL tab with the Blackhawks as the favorite
- `?cfb=fbs` every FBS college football game instead of just ranked-team games
- `?rotate=20` seconds per screen
- `?theme=bears`, `?theme=usc` or `?theme=classic` force a color scheme (default `auto`: Bears Sunday-Friday, USC on Saturday)
- `?stats=0` / `?news=0` turn off key stats or headlines in the bottom bar
- `?demo=1` fake games to test the layout
