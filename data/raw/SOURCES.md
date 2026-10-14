# Raw data sources (collected 9 October 2026)

All raw values were transcribed into CSV from public web pages. No values were invented or imputed at the raw stage.

## match_results.csv — 104 rows, one per match
| Field | Source |
|---|---|
| Group stage (matches 1–72): date, teams, score | Wikipedia, "2026 FIFA World Cup Group A" … "Group L" articles. Every group's scores were cross-checked against that group's final table (GF/GA/Pts); `src/01_build_datasets.py` re-runs this check automatically. |
| Knockout stage (matches 73–104): date, teams, score, extra time, penalties | Sortir à Paris, "FIFA World Cup 2026: all the results and the final score"; ZEE5 "Bracket Tracker 2"; national-football-teams.com (Round of 16); iCoachFootball "World Cup 2026 Winner: Spain, Full Bracket". Third-place score (England 6–4 France) also confirmed by ITV News and theScore. |

Scoring convention: `goals1`/`goals2` = the score at the end of play, **including extra time but excluding penalty shoot-outs**. A shoot-out match is recorded as a draw (goal difference 0) because shoot-out kicks are not goals.

## team_profiles.csv — 48 rows, one per team (all values known before the tournament)
| Field | Source |
|---|---|
| `fifa_rank` | FIFA/Coca-Cola Men's World Ranking as listed by MLSsoccer.com, "FIFA World Rankings: Every team at the World Cup" (table "as of June 11, 2026", i.e. the pre-tournament release). |
| `market_value_eur_m` | Transfermarkt squad values (€ millions) as compiled by Everything Edinburgh, "World Cup 2026 Squad Values: Every Team Ranked by Market Value" (18 June 2026). Same figures appear in Planet Football (15 July 2026). |
| `avg_squad_age` | RotoWire, "2026 FIFA World Cup Squad Ages" (re-used from the group's Objective 1 data, `WC2026_Task_A_Age.xlsx`). |
| `wc_prior_appearances` | Wikipedia, "National team appearances in the FIFA World Cup" (total minus the 2026 appearance; Czech Republic includes Czechoslovakia, Germany includes West Germany, DR Congo includes Zaire — FIFA's own convention). |
| `confederation`, `is_host` | FIFA 2026 qualification allocation; hosts = Canada, Mexico, United States. |

## Known data limitations
- Transfermarkt values were published a week into the tournament (18 June). Transfermarkt only updates national-team values in periodic batches, so these are treated as pre-tournament, but this is a limitation to state in the report.
- FIFA ranking is an ordinal position (1 = best), not points.
- Secondary sources (news/blog sites) were used for knockout scores because the Wikipedia knockout article could not be read in full; each knockout result was confirmed by at least two independent pages.
