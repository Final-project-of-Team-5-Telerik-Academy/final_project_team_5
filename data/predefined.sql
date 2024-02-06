

-- Insert initial data into the teams table
-- ----------------------------------------------------------------------------------
INSERT INTO match_score_db.teams (team_name, number_of_players, owners_id)
VALUES	('Bulgarian Power', 2, 1),
		('Man City', 2, 1),
		('Jam RC Club', 2, 1),
		('Le Usine', 2, 1),
		('Benefica', 2, 1),
		('Boston Celtics', 2, 1),
		('Steaua Bucharest', 2, 1),
		('Barcelona', 2, 1),
		('KS Rakow', 2, 1),
		('Bayer Leverkusen', 5, 1);
        
        

-- Insert initial data into the players table
-- ----------------------------------------------------------------------------------
INSERT INTO match_score_db.players (full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id) 
VALUES	('Michael Scott', 'Jamaica', 'Dunder Mufflin sports club', '0', '1', null, null),
       ('Pamela Beasly', 'France', 'La Sport Club', '0', '1', null, null),
       ('Jim Halpert', 'USA', 'TheOfficeFans', '0', '1', null, null),
       ('Frank Warren', 'USA', 'NeverBackDown', '1', '1', null, null),
       ('Susan Wilkinson', 'Bulgaria', 'Bulgarian Power', '1', '1', null, null),
       ('Owen Garrett', 'UK', 'Sports Club Bruf', '0', '0', null, null),

		('Jack Thompson', 'USA', 'NeverBackDown', '1', '0', '1', null),
       ('Sophie Williams', 'Jamaica', 'La Sport Club', '1', '0', '1', null),
       ('Antoine Martin', 'France', 'TheOfficeFans', '1', '0', '2', null),
       ('Elena Petrova', 'Bulgaria', 'Bulgarian Power', '1', '0', '2', null),
       ('Oliver Smith', 'UK', 'Dunder Mufflin sports club', '1', '0', null, null),
       ('Isabella Davis', 'USA', 'Sports Club Bruf', '1', '0', null, null),
       ('Carlos Rodriguez', 'Jamaica', 'NeverBackDown', '1', '0', null, null),
       ('Camille Dupont', 'France', 'La Sport Club', '1', '0', null, null),
       ('Dimitar Ivanov', 'Bulgaria', 'TheOfficeFans', '1', '0', null, null),
       ('Grace White', 'UK', 'Bulgarian Power', '1', '0', null, null),
       ('Mason Taylor', 'USA', 'Dunder Mufflin sports club', '1', '0', null, null),
       ('Ava Robinson', 'Jamaica', 'Sports Club Bruf', '1', '0', null, null),
       ('Lucas Garcia', 'France', 'NeverBackDown', '1', '0', null, null),
       ('Stella Johnson', 'Bulgaria', 'La Sport Club', '1', '0', null, null),
       ('Liam Anderson', 'UK', 'TheOfficeFans', '1', '0', null, null),
       ('Natalie Brown', 'USA', 'Bulgarian Power', '1', '0', null, null),
       ('Diego Martinez', 'Jamaica', 'Dunder Mufflin sports club', '1', '0', null, null),
       ('Emma Wilson', 'France', 'Sports Club Bruf', '1', '0', null, null),
       ('Eva Harris', 'Bulgaria', 'NeverBackDown', '1', '0', null, null),
       ('Aiden Clark', 'UK', 'La Sport Club', '1', '0', null, null),
       ('Zoe Green', 'USA', 'TheOfficeFans', '1', '0', null, null),
       ('Julian Scott', 'Jamaica', 'Bulgarian Power', '1', '0', null, null),
       ('Sophia King', 'France', 'Dunder Mufflin sports club', '1', '0', null, null),
       ('Landon Miller', 'Bulgaria', 'Sports Club Bruf', '1', '0', null, null),
       ('Chloe Adams', 'UK', 'NeverBackDown', '1', '0', null, null);


-- Insert initial data into the users table
INSERT INTO match_score_db.users (full_name, email, password, gender, role, players_id, is_verified, verification_code) 
VALUES ('Steven Atkinson', 'steven.atkinson@gmail.com', '2fca7af39df396e0890de73cf93628cc50261c1c5bff980995ce740279a740f9', 'male', 'admin', null, '1', '123450'),
       ('Michael Scott', 'michael.scott@gmail.com', 'd24259be13407e0d132337bd8398ee9aaff43a249c38d0bf222429f311c9c939', 'male', 'director', '1', '1', '123451'),
       ('Pamela Beasly', 'pamela.beasly@gmail.com', '78d7ba5153684388785609ab6fc8beafa7d63c394481026999f6ccf420d9ab9a', 'female', 'director', '2', '1', '123452'),
       ('Jim Halpert', 'jim.halpert@gmail.com', '3cb7aff2146cd44bbdef023e465424e3c4a6ac793b7fa250c8895d93065ec53c', 'male', 'director', '3', '1', '123453'),
       ('Owen Garrett', 'owen.garrett@yahoo.com', 'c2b41017a8036252bb2308ea026284ffd455a9eab57c4b65777fbcd0ac891964', 'male', 'spectator', null, '1', '123454'),
       ('Kyan Chandler', 'chandler_kyan@gmx.de', 'c53c1c5f81b36257b951965239ef46c1c6e6fbb4d4eb01cee58b6dc9bc2ae80c', 'male', 'spectator', null, '1', '123455'),
       ('Frank Warren', 'warwarbinks@gmail.com', '74fca0325b5fdb3a34badb40a2581cfbd5344187e8d3432952a5abc0929c1246', 'male', 'player', '4', '1', '123456'),
       ('Susan Wilkinson', 'suuusan_123@abv.bg', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', 'female', 'player', null, '1', '123457');


-- Insert initial data into the admin_requests table
-- ----------------------------------------------------------------------------------
INSERT INTO match_score_db.admin_requests (type_of_request, players_id, users_id, status)
VALUES ('connection', 6, 5, 'pending');


