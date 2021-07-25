CREATE DATABASE apl_golf_league;
SHOW DATABASES;
USE apl_golf_league;

# Example join query using foreign keys
# SELECT courses.name, tracks.name, tee_sets.name, tee_sets.rating, tee_sets.slope FROM courses JOIN tracks ON tracks.course_id = courses.course_id JOIN tee_sets ON tee_sets.track_id = tracks.track_id;

# Example filtered join query using foreign keys and where-clause
# SELECT players.last_name, players.first_name, player_contacts.type, player_contacts.contact FROM players JOIN player_contacts ON player_contacts.player_id = players.player_id WHERE players.player_id = 3;

DROP TABLE players;
CREATE TABLE players (
	player_id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    affiliation ENUM("APL_EMPLOYEE", "APL_RETIREE", "APL_FAMILY_MEMBER", "NON_APL_EMPLOYEE", "UNKNOWN") NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id)
);

DROP TABLE player_contacts;
CREATE TABLE player_contacts (
	contact_id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
	player_id INT UNSIGNED NOT NULL,
    type ENUM("PHONE", "EMAIL") NOT NULL,
    contact VARCHAR(255) NOT NULL,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    UNIQUE (player_id, type)
);

DROP TABLE courses;
CREATE TABLE courses (
	course_id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(7),
    zip_code MEDIUMINT UNSIGNED,
    phone VARCHAR(255),
    website VARCHAR(255),
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (course_id),
    UNIQUE (name, city, state)
);

DROP TABLE tracks;
CREATE TABLE tracks (
    track_id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    course_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (track_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    UNIQUE (course_id, name)
);

DROP TABLE tee_sets;
CREATE TABLE tee_sets (
    tee_set_id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    track_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    gender ENUM("M", "F") NOT NULL,
    rating FLOAT NOT NULL,
    slope FLOAT NOT NULL,
    color VARCHAR(6),
    PRIMARY KEY (tee_set_id),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id),
    UNIQUE (track_id, name, gender)
);

DROP TABLE holes;
CREATE TABLE holes (
    hole_id INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
	tee_set_id INT UNSIGNED NOT NULL,
    number TINYINT UNSIGNED NOT NULL,
    par TINYINT UNSIGNED NOT NULL,
    handicap TINYINT UNSIGNED NOT NULL,
    yardage SMALLINT UNSIGNED,
    PRIMARY KEY (hole_id),
    FOREIGN KEY (tee_set_id) REFERENCES tee_sets(tee_set_id),
    UNIQUE (tee_set_id, number)
);

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
    FOREIGN KEY (middle_tee_set_id) REFERENCES tee_sets(tee_set_id),
    FOREIGN KEY (senior_tee_set_id) REFERENCES tee_sets(tee_set_id),
    FOREIGN KEY (super_senior_tee_set_id) REFERENCES tee_sets(tee_set_id),
    FOREIGN KEY (forward_tee_set_id) REFERENCES tee_sets(tee_set_id),
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
	match_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    team_1_id INT UNSIGNED NOT NULL,
    team_2_id INT UNSIGNED NOT NULL,
    week TINYINT UNSIGNED NOT NULL,
    course_id INT UNSIGNED NOT NULL,
    type ENUM("REGULAR", "PLAYOFF") NOT NULL,
    team_1_score TINYINT UNSIGNED,
    team_2_score TINYINT UNSIGNED,
    date_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id)
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
