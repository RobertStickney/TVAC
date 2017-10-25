DROP database IF EXISTS tvac;
create database tvac;


DROP TABLE IF EXISTS tvac.Expected_Temperature;
CREATE TABLE tvac.Expected_Temperature(
	profile_I_ID varchar(36) NOT NULL,
	time DATETIME NOT NULL,
	zone tinyint unsigned NOT NULL,
	temperature decimal(10,4) NOT NULL
);

DROP TABLE IF EXISTS tvac.Real_Temperature;
CREATE TABLE tvac.Real_Temperature(
	profile_I_ID varchar(36) NOT NULL,
	time DATETIME NOT NULL,
	thermocouple tinyint unsigned NOT NULL,
	temperature decimal(10,4) NOT NULL
);

DROP TABLE IF EXISTS tvac.Pressure;
CREATE TABLE tvac.Pressure(
	profile_I_ID varchar(36) NOT NULL,
	time DATETIME NOT NULL,
	guage tinyint unsigned NOT NULL,
	pressure float NOT NULL
);

DROP TABLE IF EXISTS tvac.Event;
CREATE TABLE tvac.Event(
	event_type varchar(256) NOT NULL,
	details varchar(256) NOT NULL,
	created timestamp NOT NULL
);

DROP TABLE IF EXISTS tvac.Debug;
CREATE TABLE tvac.Debug(
	created DATETIME NOT NULL,
	message varchar(256) NOT NULL
);

DROP TABLE IF EXISTS tvac.TC_Profile;
CREATE TABLE tvac.TC_Profile(
	profile_name varchar(36) NOT NULL,
	zone tinyint unsigned NOT NULL,
	thermocouple tinyint unsigned NOT NULL
);

DROP TABLE IF EXISTS tvac.Profile_Instance;
CREATE TABLE tvac.Profile_Instance(
	profile_name varchar(36) NOT NULL,
	profile_I_ID varchar(36) NOT NULL,
	profile_Start_Time DATETIME NOT NULL,
	thermal_Start_Time DATETIME NULL,
	first_Soak_Start_Time DATETIME NULL,
	endTime DATETIME NULL
);


DROP TABLE IF EXISTS tvac.Thermal_Zone_Profile;
CREATE TABLE tvac.Thermal_Zone_Profile(
	profile_name varchar(36) NOT NULL,
	zone tinyint unsigned NOT NULL,
	average varchar(10) NOT NULL,
	max_heat_error decimal(10,4) NOT NULL,
	min_heat_error decimal(10,4) NOT NULL,
	max_heat_per_min decimal(10,4) NOT NULL,
	created timestamp NOT NULL,
	UNIQUE KEY(profile_name,zone)
);

DROP TABLE IF EXISTS tvac.Thermal_Profile;
CREATE TABLE tvac.Thermal_Profile(
	profile_name varchar(36) NOT NULL,
	zone tinyint unsigned NOT NULL,
	set_point tinyint unsigned NOT NULL,
	temp_goal decimal(9,4) NOT NULL,
	ramp_time mediumint unsigned NOT NULL,
	soak_time mediumint unsigned NOT NULL,
	UNIQUE KEY(profile_name,zone,set_point)
);

DROP TABLE IF EXISTS tvac.System_Status;
CREATE TABLE tvac.System_Status(
	in_hold BOOLEAN not null default 0,
	in_pause BOOLEAN not null default 0,
	in_ramp BOOLEAN not null default 1,
	record_data BOOLEAN not null default 1,	
	vacuum_wanted BOOLEAN not null default 0,
	setpoint int not null default 0
);
INSERT INTO tvac.System_Status () VALUES ();
-- Change localhost to server IP
-- CREATE USER 'tvac_user'@'localhost' IDENTIFIED BY 'Go2Mars!';
-- GRANT ALL PRIVILEGES ON tvac.* TO 'tvac_user'@'localhost';
