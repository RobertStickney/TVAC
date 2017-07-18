DROP database IF EXISTS Cryogenics;
create database Cryogenics;
DROP TABLE IF EXISTS Cryogenics.profiles;
CREATE TABLE Cryogenics.profiles (jdoc JSON);
DROP TABLE IF EXISTS Cryogenics.events;
CREATE TABLE Cryogenics.events (jdoc JSON);