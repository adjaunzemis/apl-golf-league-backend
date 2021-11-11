-- APL DB Test Queries
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
JOIN team ON player.team_id = team.id;

SELECT golfer.id as golfer_id, golfer.name as golfer_name, golfer.affiliation as golfer_affiliation
FROM golfer;

SELECT player.id as player_id, golfer.id as golfer_id, player.role as player_role, division.name as division_name, flight.name as flight_name, team.name as team_name
FROM player
JOIN golfer ON player.golfer_id = golfer.id
JOIN team ON player.team_id = team.id
JOIN division ON player.division_id = division.id
JOIN flight ON division.flight_id = flight.id
WHERE golfer.id in (1,2,3,4);
