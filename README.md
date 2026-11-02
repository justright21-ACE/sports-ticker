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
- When no primetime game (SNF/MNF/TNF, World Series) is on the board that day, your other teams (Bears, Eagles, Spurs, Bulls, Blackhawks, White Sox) get their own tab and big screen too, with basketball and hockey versions (leaders, team stats, periods, GOAL! banners). `?favscreen=0` turns it off
- Injury reports: each team's side panel on the big screens lists who's out / doubtful / questionable (day-to-day in NBA/NHL) before the game and who's out during it (trimmed to fit the screen), and the bottom bar has an INJURIES segment for your teams' games today. Injured reserve is left off. `?injuries=0` turns it off
- Any NFL game, and any college game with a Top 25 team, within one score (8 pts) in the 4th quarter or overtime gets its own CLOSE screen, 30 seconds a time (`?close=0` turns it off)
- Big-screen animations (primetime, game day, CLOSE, World Series): team-color wipe as the screen arrives, the ball glides on the field, red-zone pulse, scoring banners (TOUCHDOWN / FIELD GOAL / SAFETY, lead changes, ties) with a flipping score, a two-minute-warning pulse, a FINAL stamp, and 20+ yard plays (a runner sprinting across, or a ball flying into a pair of hands). A 20+ yard play or a turnover (INTERCEPTION! / FUMBLE! / TURNOVER ON DOWNS, with a loose-ball and possession-swap animation) in a live big-screen game, or any score in a CLOSE game, jumps the rotation straight to that game (a score that breaks a game open keeps its CLOSE screen 3 more minutes). `?motion=0` turns animations off, `?jump=0` turns off the jump
- A league drops off the top bar once its season is over (champion decided or ESPN says off-season), after the title game result has been up 12 hours; it comes back on its own next season (`?ended=1` keeps every tab)
- `?fav=DAL,TEX` override favorites for every league
- `?leagues=nfl,ncaaf,nba` choose leagues (nfl, ncaaf, nba, mlb, wnba, ncaab, nhl)
- NHL tab with the Blackhawks as the favorite
- College football Top 25 screen switches to the College Football Playoff rankings once they are released (AP moves to the second column); ranks next to team names follow it
- Standings screens after each league, every day but only before that league's first game starts or after its last game is final (never mid-games): NFL, NBA and NHL by division (a screen per conference); college football for the SEC, Big Ten, Big 12, ACC, Pac-12, Mountain West and American (college basketball keeps just its Top 25 screen). `?standings=0` turns them off
- March Madness: the NCAAB tab shows the bracket in place of the Top 25 screen. Through the Sweet 16, one screen per region (16 teams down to the region winner) with a line through every eliminated team; once it is down to the last 8, one screen with the Elite Eight, Final Four, championship and champion. `?bracket=0` turns it off
- `?cfb=fbs` every FBS college football game instead of just ranked-team games
- `?rotate=20` seconds per screen
- `?theme=bears`, `usc`, `sox`, `bulls` or `classic` force a color scheme. Default `auto`: USC colors on Saturdays when USC plays; Bears every other day during the NFL season; after the Super Bowl, White Sox or Bulls colors, whichever team plays next (Bears again once the NFL is back)
- `?stats=0` / `?news=0` turn off key stats or headlines in the bottom bar
- Fits any screen: sideways screens from 5:4 to 21:9 fill the screen; anything else (phone or tablet held upright, super-wide monitors) runs in a correctly shaped frame centered on the screen. Phones with rounded corners or a notch keep clear of them automatically. `?inset=3` adds a 3% safety margin on every side for TVs that crop their edges
- `?demo=1` fake games to test the layout
