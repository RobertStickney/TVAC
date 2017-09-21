DROP database IF EXISTS tvac;
create database tvac;


DROP TABLE IF EXISTS tvac.Expected_Temperture;
CREATE TABLE tvac.Expected_Temperture(
	profile_I_ID varchar(36) NOT NULL,
	time DATETIME NOT NULL,
	zone tinyint unsigned NOT NULL,
	temperture decimal(10,4) NOT NULL
);

DROP TABLE IF EXISTS tvac.Real_Temperture;
CREATE TABLE tvac.Real_Temperture(
	profile_I_ID varchar(36) NOT NULL,
	time DATETIME NOT NULL,
	thermocouple tinyint unsigned NOT NULL,
	temperture decimal(10,4) NOT NULL
);

DROP TABLE IF EXISTS tvac.Event;
CREATE TABLE tvac.Event(
	event_type varchar(256) NOT NULL,
	details varchar(256) NOT NULL,
	created timestamp NOT NULL
);

DROP TABLE IF EXISTS tvac.Debug;
CREATE TABLE tvac.Debug(
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
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
	startTime DATETIME DEFAULT CURRENT_TIMESTAMP,
	endTime DATETIME 
);

DROP TABLE IF EXISTS tvac.Thermal_Zone_Profile;
CREATE TABLE tvac.Thermal_Zone_Profile(
	profile_name varchar(36) NOT NULL,
	zone tinyint unsigned NOT NULL,
	average varchar(10) NOT NULL,
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
	soak_time mediumint unsigned NOT NULL
);
-- Change localhost to server IP
-- CREATE USER 'tvac_user'@'localhost' IDENTIFIED BY 'Go2Mars!';
-- GRANT ALL PRIVILEGES ON tvac.* TO 'tvac_user'@'localhost';
