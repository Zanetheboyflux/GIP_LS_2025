create database fightinggame_database; 

create table Pygame (
GameID int not null auto_increment, 
Winner varchar(255) not null, 
Loser varchar(255) not null, 
Player1_character varchar(255), 
Player2_character varchar(255), 
primary key (GameID)); 

alter table Pygame 
modify column Winner int ; 
alter table Pygame 
modify column Loser int ; 

alter table Pygame 
modify column Player1_character text; 
alter table Pygame 
modify column Player2_character text; 
alter table Pygame 
add timestamp datetime default current_timestamp ; 

create table users (
accountID int not null auto_increment, 
account_name varchar(255) not null, 
account_password varchar(255) not null,
primary key (accountID)
); 
alter table users 
add GameID int ; 
alter table users 
add foreign key (accountID) references pygame(GameID); 
