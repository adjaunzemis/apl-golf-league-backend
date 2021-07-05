CREATE DATABASE apl_golf_league;
SHOW DATABASES;
USE apl_golf_league;

# Example join query using foreign keys
# SELECT courses.name, tracks.name, tee_sets.name, tee_sets.rating, tee_sets.slope FROM courses JOIN tracks ON tracks.course_id = courses.id JOIN tee_sets ON tee_sets.track_id = tracks.id;

DROP TABLE players;
CREATE TABLE players (
	id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(255),
    last_name VARCHAR(255) NOT NULL,
    affiliation ENUM("APL_EMPLOYEE", "APL_FAMILY_MEMBER", "APL_RETIREE", "NON_APL_EMPLOYEE") NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(255),
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (first_name, last_name, email)
);

DROP TABLE courses;
CREATE TABLE courses (
	id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT, # TODO: change to course_id
    name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(7) NOT NULL, # TODO: remove this?
    address VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(7),
    zip_code SMALLINT UNSIGNED, # TODO: make MEDIUMINT!
    phone VARCHAR(255),
    website VARCHAR(255),
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (name, city, state)
);

DROP TABLE tracks;
CREATE TABLE tracks (
    id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT, # TODO: change to track_id
    course_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(7) NOT NULL, # TODO: remove this?
    PRIMARY KEY (id),
    FOREIGN KEY (course_id) REFERENCES courses(id), # TODO: update with id field change
    UNIQUE (course_id, name)
);
ALTER TABLE tracks ADD FOREIGN KEY (course_id) REFERENCES courses(id);

DROP TABLE tee_sets;
CREATE TABLE tee_sets (
    id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT, # TODO: change to tee_set_id
    track_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    gender ENUM("M", "F") NOT NULL,
    rating FLOAT NOT NULL,
    slope FLOAT NOT NULL,
    color VARCHAR(6),
    PRIMARY KEY (id),
    FOREIGN KEY (track_id) REFERENCES tracks(id), # TODO: update with id field change
    UNIQUE (track_id, name, gender)
);
ALTER TABLE tee_sets ADD FOREIGN KEY (track_id) REFERENCES tracks(id);

DROP TABLE holes;
CREATE TABLE holes (
    id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT, # TODO: change to hole_id
	tee_set_id INT UNSIGNED NOT NULL,
    number TINYINT UNSIGNED NOT NULL,
    par TINYINT UNSIGNED NOT NULL,
    handicap TINYINT UNSIGNED NOT NULL,
    yardage SMALLINT UNSIGNED,
    PRIMARY KEY (id),
    FOREIGN KEY (tee_set_id) REFERENCES tee_sets(id), # TODO: update with id field change
    UNIQUE (tee_set_id, number)
);
ALTER TABLE holes ADD FOREIGN KEY (tee_set_id) REFERENCES tee_sets(id);

DROP TABLE flights;
CREATE TABLE flights (
	flight_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    year SMALLINT UNSIGNED NOT NULL,
    middle_tee_set_id INT UNSIGNED NOT NULL,
    senior_tee_set_id INT UNSIGNED NOT NULL,
	super_senior_tee_set_id INT UNSIGNED NOT NULL,
    forward_tee_set_id INT UNSIGNED NOT NULL,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (middle_tee_set_id) REFERENCES tee_sets(id), # TODO: update with id field change
    FOREIGN KEY (senior_tee_set_id) REFERENCES tee_sets(id), # TODO: update with id field change
    FOREIGN KEY (super_senior_tee_set_id) REFERENCES tee_sets(id), # TODO: update with id field change
    FOREIGN KEY (forward_tee_set_id) REFERENCES tee_sets(id), # TODO: update with id field change
    UNIQUE (name, year)
);

DROP TABLE flight_teams;
CREATE TABLE flight_teams (
	flight_team_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    flight_id INT UNSIGNED NOT NULL,
    number SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(255),
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    UNIQUE(flight_id, number)
);

DROP TABLE flight_team_golfers;
CREATE TABLE team_golfers (
	team_id INT UNSIGNED NOT NULL,
    player_id INT UNSIGNED NOT NULL,
    role ENUM("CAPTAIN", "MEMBER", "SUBSTITUTE"),
    classification ENUM("MIDDLE", "SENIOR", "SUPER_SENIOR", "FORWARD"),
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, player_id)
);

DROP TABLE matches;
CREATE TABLE matches (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    team_1_id INT UNSIGNED NOT NULL,
    team_2_id INT UNSIGNED NOT NULL,
    week TINYINT UNSIGNED NOT NULL,
    course_id INT UNSIGNED NOT NULL,
    type ENUM("REGULAR", "PLAYOFF") NOT NULL,
    team_1_score TINYINT UNSIGNED,
    team_2_score TINYINT UNSIGNED,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

DROP TABLE match_rounds;
CREATE TABLE match_rounds (
	match_id INT UNSIGNED NOT NULL,
    round_id INT UNSIGNED NOT NULL,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id, round_id)
);

DROP TABLE rounds;
CREATE TABLE rounds (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    course_id INT UNSIGNED NOT NULL,
    player_id INT UNSIGNED NOT NULL,
    date_played DATE NOT NULL,
    player_handicap_index FLOAT NOT NULL,
    player_course_handicap FLOAT NOT NULL,
    gross_score TINYINT UNSIGNED NOT NULL,
    adjusted_gross_score TINYINT UNSIGNED NOT NULL,
    net_score TINYINT UNSIGNED NOT NULL,
    score_differential FLOAT NOT NULL,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

DROP TABLE round_hole_scores;
CREATE TABLE round_hole_scores (
	round_id INT UNSIGNED NOT NULL,
    hole_number TINYINT UNSIGNED NOT NULL,
    strokes TINYINT UNSIGNED NOT NULL,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (round_id, hole_number)
);
