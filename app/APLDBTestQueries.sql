-- APL DB Test Queries
SELECT round.id as round_id, golfer.name as golfer, round.date_played as date, course.name as course
FROM round
JOIN tee ON round.tee_id = tee.id
JOIN track ON tee.track_id = track.id
JOIN course ON track.course_id = course.id
JOIN golfer ON round.golfer_id = golfer.id;

SELECT match.id as match_id, round.id as round_id, team.name as team, golfer.name as golfer, round.date_played as date, flight.year as year, match.week as week, course.name as course, flight.name as flight, division.name as division
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
