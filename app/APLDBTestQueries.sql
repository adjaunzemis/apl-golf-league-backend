-- APL DB Test Queries
SELECT *
FROM round
JOIN roundgolferlink ON round.id = roundgolferlink.round_id
JOIN golfer ON roundgolferlink.golfer_id = golfer.id;

-- round_query_data = session.exec(select(Round, MatchRoundLink, RoundGolferLink, Golfer, Course, Tee, Team)
--   .join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id)
--   .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
--   .join(Tee)
--   .join(Track)
--   .join(Course)
--   .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
--   .join(Match, onclause=Match.id == MatchRoundLink.match_id)
--   .join(Player, ((Player.golfer_id == Golfer.id) & (Player.team_id.in_((Match.home_team_id, Match.away_team_id)))))
--   .join(Team, Team.id == onclause=Player.team_id)
--   .where(Round.id.in_(round_ids)))
SELECT *
FROM round
JOIN matchroundlink ON matchroundlink.round_id = round.id
JOIN roundgolferlink ON roundgolferlink.round_id = round.id
JOIN tee ON tee.id = round.tee_id
JOIN track ON track.id = tee.track_id
JOIN course ON course.id = track.course_id
JOIN golfer ON golfer.id = roundgolferlink.golfer_id
JOIN match on match.id = matchroundlink.match_id
JOIN player ON player.golfer_id = golfer.id AND player.team_id IN (match.home_team_id, match.away_team_id)
JOIN team ON team.id = player.team_id
WHERE round.id IN (1, 2, 3);

SELECT round.id as round_id, golfer.name as golfer_name, round.date_played as date_played, course.name as course_name, golfer.id as golfer_id
FROM round
JOIN tee ON round.tee_id = tee.id
JOIN track ON tee.track_id = track.id
JOIN course ON track.course_id = course.id
JOIN golfer ON round.golfer_id = golfer.id
WHERE golfer.name == "Andris Jaunzemis"
ORDER BY round.date_played;

SELECT holeresult.id as hole_result_id, holeresult.round_id as round_id, hole.id as hole_id, hole.number as hole_number, hole.par as hole_par, hole.yardage as hole_yardage, hole.stroke_index as hole_stroke_index, holeresult.strokes as hole_result_strokes
FROM holeresult
JOIN hole ON holeresult.hole_id = hole.id
WHERE holeresult.round_id in (1,2,3);

SELECT match.id as match_id, round.id as round_id, team.name as team_name, golfer.name as golfer_name, round.date_played as date_played, flight.year as flight_year, match.week as match_week, course.name as course_name, flight.name as flight_name, division.name as division_name
FROM match
JOIN matchroundlink ON match.id = matchroundlink.match_id
JOIN round ON round.id = matchroundlink.round_id
JOIN tee ON round.tee_id = tee.id
JOIN track ON tee.track_id = track.id
JOIN course ON track.course_id = course.id
JOIN golfer ON round.golfer_id = golfer.id
JOIN player ON round.golfer_id = player.golfer_id
JOIN flight ON match.flight_id = flight.id
JOIN division ON division.flight_id = flight.id AND player.division_id = division.id
JOIN team ON player.team_id = team.id
WHERE match.id in (2);

SELECT match.id as match_id, round.id as round_id, team.name as team_name, golfer.name as golfer_name, round.date_played as date_played, course.name as course_name
FROM match
JOIN matchroundlink ON match.id = matchroundlink.match_id
JOIN round ON round.id = matchroundlink.round_id
JOIN tee ON round.tee_id = tee.id
JOIN track ON tee.track_id = track.id
JOIN course ON track.course_id = course.id
JOIN golfer ON round.golfer_id = golfer.id
JOIN player ON round.golfer_id = player.golfer_id
JOIN team ON player.team_id = team.id
WHERE match.id in (1, 2, 3);

SELECT round.tee_id, round.golfer_id, round.handicap_index, round.playing_handicap, round.date_played, round.id, matchroundlink.match_id, matchroundlink.round_id, golfer.name, golfer.affiliation, golfer.id, course.name, course.address, course.phone, course.website, course.id, tee.name, tee.gender, tee.rating, tee.slope, tee.color, tee.track_id, tee.id, team.name, team.flight_id, team.id
FROM round
JOIN matchroundlink ON matchroundlink.round_id = round.id
JOIN match ON match.id = matchroundlink.match_id
JOIN tee ON tee.id = round.tee_id
JOIN track ON track.id = tee.track_id
JOIN course ON course.id = track.course_id
JOIN golfer ON golfer.id = round.golfer_id
JOIN player ON player.golfer_id = golfer.id AND player.team_id IN (match.home_team_id, match.away_team_id)
JOIN team ON player.team_id = team.id
WHERE matchroundlink.match_id IN (2);

SELECT player.id as player_id, golfer.id as golfer_id, player.role as player_role, division.name as division_name, flight.name as flight_name, team.name as team_name
FROM player
JOIN golfer ON player.golfer_id = golfer.id
JOIN team ON player.team_id = team.id
JOIN division ON player.division_id = division.id
JOIN flight ON division.flight_id = flight.id
WHERE golfer.id in (1,2,3,4);

SELECT *
FROM player
JOIN team on player.team_id = team.id
JOIN golfer on player.golfer_id = golfer.id
JOIN division on player.division_id = division.id
JOIN flight on division.flight_id = flight.id;

SELECT match.id as match_id, flight.name as flight_name, home_team.name as home_team_name, away_team.name as away_team
FROM match
JOIN flight on match.flight_id = flight.id
JOIN team AS home_team on match.home_team_id = home_team.id
JOIN team AS away_team on match.away_team_id = away_team.id;

SELECT * FROM flight;

SELECT * FROM round
JOIN roundgolferlink ON roundgolferlink.round_id = round.id
JOIN golfer ON golfer.id = roundgolferlink.golfer_id
WHERE golfer.name = 'Charlie Overly';

SELECT * FROM teamgolferlink
JOIN golfer ON golfer.id = teamgolferlink.golfer_id
JOIN flightteamlink on flightteamlink.team_id = teamgolferlink.team_id
JOIN flight ON flight.id = flightteamlink.flight_id
WHERE golfer.name = 'Charlie Overly' AND flight.year = 2021;

SELECT tee.* FROM tee
JOIN division ON division.primary_tee_id = tee.id
JOIN tournamentdivisionlink ON tournamentdivisionlink.division_id = division.id
JOIN tournamentteamlink ON tournamentteamlink.tournament_id = tournamentdivisionlink.tournament_id
JOIN teamgolferlink ON teamgolferlink.team_id = tournamentteamlink.team_id
JOIN golfer ON golfer.id = teamgolferlink.golfer_id
WHERE tournamentdivisionlink.tournament_id = 1 AND golfer.id = 115 AND teamgolferlink.division_id = division.id;

SELECT * FROM round
JOIN roundgolferlink ON roundgolferlink.round_id = round.id
JOIN golfer ON golfer.id = roundgolferlink.golfer_id
JOIN teamgolferlink ON teamgolferlink.golfer_id = golfer.id
JOIN tournamentteamlink ON tournamentteamlink.team_id = teamgolferlink.team_id
JOIN tournament ON tournament.id = tournamentteamlink.tournament_id
WHERE tournament.id = 5 AND round.date_played = tournament.date;

SELECT * FROM round WHERE round.type = "Tournament" ORDER BY date_played;

SELECT * FROM tournament;
PRAGMA table_info(tournament);

SELECT * FROM tournamentteamlink
JOIN teamgolferlink ON teamgolferlink.team_id = tournamentteamlink.team_id
JOIN golfer ON golfer.id = teamgolferlink.golfer_id
JOIN roundgolferlink ON roundgolferlink.golfer_id = golfer.id
WHERE tournamentteamlink.tournament_id = 1;

SELECT team.* FROM team
JOIN tournamentteamlink ON tournamentteamlink.team_id = team.id
WHERE tournamentteamlink.tournament_id = 1;

SELECT * FROM round
JOIN roundgolferlink ON roundgolferlink.round_id = round.id
JOIN golfer ON golfer.id = roundgolferlink.golfer_id
JOIN teamgolferlink ON teamgolferlink.golfer_id = golfer.id
WHERE round.id IN (1669, 1670);

SELECT * FROM round
JOIN roundgolferlink ON roundgolferlink.round_id = round.id
JOIN golfer ON golfer.id = roundgolferlink.golfer_id
JOIN tee ON tee.id = round.tee_id
JOIN track ON track.id = tee.track_id
JOIN course ON course.id = track.course_id
WHERE round.id IN (1669, 1670);
