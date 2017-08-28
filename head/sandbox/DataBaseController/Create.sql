DROP database IF EXISTS Cryogenics;
create database Cryogenics;
DROP TABLE IF EXISTS Cryogenics.profiles;
CREATE TABLE Cryogenics.profiles (jdoc JSON,profileUUID varchar(32), created timestamp);
DROP TABLE IF EXISTS Cryogenics.events;
CREATE TABLE Cryogenics.events (jdoc JSON, created timestamp);
DROP TABLE IF EXISTS Cryogenics.errors;
CREATE TABLE Cryogenics.errors (jdoc JSON, created timestamp);