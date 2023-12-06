<img align="right" src="https://media.discordapp.net/attachments/1171040731104808962/1181969242506137710/Screenshot_2023-11-21_at_4.35.53.png?ex=6582fda3&is=657088a3&hm=4926db45a1d5af43d156dc8a7b29f010eba9c743e0ca599901c518570e8b8aba&=&format=webp&quality=lossless" alt="logo" width="320px"/>

# MatchScore Team 5

Welcome to `back-end match score guidance handbook`.
Here you will understand how to properly work with the program. 


**⚠ Please strictly follow the instructions we provided ⚠**

**⚠ For your best convenience you could use the swagger UI provided by FASTAPI ⚠**

<br></br>

## SEQUENCE SECTIONS IN OUR PROGRAM:

<!-- Start Server/FASTAPI -->

### 🟥 Server/FASTAPI ✅ 
>This section explains how to successfuly start the project.
>After you copy and paste the Repository link to Pycharm or VScode you should do the following steps:

>A) Download and install a MariaDB server and create MySQL WorkBench connection with port 127.0.0.1:3306.<br>
>B) Copy the SQL script from the repository data/datascript.sql and run it in MySQL WorkBench.<br>
>C) Copy the SQL script from the repository data/predefined.sql and run it in MySQL WorkBench.<br>
>D) Create in the repository folder a file with name private_password.py and create a variable with a name my_password = 'YourMariaDBServerPassword'.<br>
>E) Turn on 2-Step Verification in Gmail:<br>
    >1. Log into your gmail account and open the link: "https://myaccount.google.com/". 
    >2. Click on Security and scroll down to the menu "Signing in to Google"
    >and click on "2-Step Verification". 
    >3. On the pop mask click on "Get Started" and then write your gmail password. Then you should write 
    >your phone number and you can choose to receive the code via a text message or a phone call. 
    >4. When you receive the verification code go to step 2 mask and type it there. 
    >5. Click on next and confirm that you want to turn on the 2-Step Verification process. 
    >6. Use the URL: "https://myaccount.google.com/u/4/apppasswords" and then write your gmail password. 
    >7. From the select app down menu choose the last option: Other (Customer name).
    >8. Write "Python" in the mask and click on "Generate".
    >9. Copy the 16 digit code from the mask and return to the file private_password.py and create the following variables:
        >my_gmail_address = 'YourGmailAddress@gmail.com'
        >my_gmail_password = 'aaaa bbbb cccc dddd' (Your 16 digit code from Gmail)

>F) Check in requirements.txt the list with all used pip systems and install them if you don't have them.<br>
>G) To start the server you can run the file main.py or write the following command in the terminal: uvicorn main:app.<br>


*🔴❗WARNING DON'T SHARE YOUR MARIADB PASSWORD AND YOUR GMAIL CREDENTIALS TO ANYONE❗🔴*


<!-- Users -->

### <h2><br><br>USERS 👥</h2>
### Register 🆕
>This section allows you to successfully register yourself using your own full_name/email/password/gender.
>The email addresses are configured as unique and you are not allowed to register 2 accounts with the same email address.

### Verification ✅
>After the registration steps you will receive an email with a 6 digit verification code.
>Write in the typing fields your email address and 6 digit verification code.
>After a successful profile verification you will receive an email and you will be allowed to log in the MatchScore App.

### Login 🔠
>Uppon logging in our system you will get a unique token with expiration time from which you can access sections in our website.

*🔴❗WARNING DON'T SHARE YOUR TOKEN TO ANYONE❗🔴*

### Info ℹ️
>You are able to see your account information.

### Delete ❌
>Option to delete your own account.


<!-- Admins -->

### <h2><br><br>ADMINS 💻</h2>
### User Info ℹ️

>Admin can search for any account information without the user's password.

### Edit User 🔧

>Admin can edit any user (with user's id) by will or by a request(promotion or connection). 
>Options for editing:
    >Promote user's role from spectator to player.
    >Promote user's role from player to director.
    >Demote user's role from director to player.
    >Demote user's role from player to spectator.
    >Connect an user's with a player's account.

### Delete User ❌
>Admin can delete any user's account.

### Blocked Players 🚫
>Admin can temporary or permanently block any user's account.

### Find All Blocked Players 👥
>Admin can temporary or permanently block any user's account.

### Remove Players Block 🆗
>Admin can temporary or permanently block any user's account.


<!-- Players -->

### <h2><br><br>PLAYERS 🏃‍♂️</h2>
### Create Player 🙆‍♂️
>Only admins and directors are allowed to create new players. 
>For creating a new player you must type a player's full_name/country/sports_club.

### Edit Player 💇‍♂️
>Admins can edit any player.
>Directors can edit players only if they are still not connected to a specific user. 
>User can edit only his connected player.

### Find All Players 👀
>See all players. You are allowed to view them even if you are not logged in the app.

### Find Player By ID 🔎
>Search for a specific player. You are allowed to view the player even if you are not logged in the app.

### Delete Player By ID ❌
>Only admins are allowed to delete player's accounts.


<!-- Admin Requests -->

### <h2><br><br>ADMIN REQUESTS 📥</h2>
### Create Admin Request 🔨
>Users with a spectator or a player role can create and send admin requests.
>Types of admin requests:
    >Request for connection with a player's account and user's role to be changed from spectator to player.
    >Request for promotion from player to director.

### Find All Admin Requests 👀
>Admins can view admin requests from all users. Users can see a list of only their sent requests.

### Find Admin Request By ID 🔎
>Admins can view any existing admin request and users can view only their sent requests.

### Delete Player By ID ❌
>Admins can delete any existing admin request and users can delete only their requests.


<!-- Director Requests -->

### <h2><br><br>DIRECTOR REQUESTS 📥</h2>
### Create Director Request 🔨
>Users with a spectator role can create and send requests to directors so a player with their full_name/country/sports_club can be created.

### Find All Director Requests 👀
>Directos and admins can view director requests from all users. Users can see a list of only their sent requests.

### Find Director Request By ID 🔎
>Directors and admins can view any existing director request and users can view only their sent requests.

### Delete Director Request ❌
>Directors and admins can delete any existing director request and users can delete only their requests.


<!-- Teams -->

### <h2><br><br>TEAMS 👫👬👭</h2>
### Create Team 🔨
>Directors and admins can create a team which to be used for participating in matches and tournaments.
>To create a team the following information should be filled: team_name/number_of_players

### Find All Teams 👀
>Directos and admins can view all created teams.

### Delete Team ❌👫👬👭
>Admins can delete all teams. Directors can delete only their created teams.

### Find Team By ID 🔎👫👬👭
>Directors and admins can view any team.

### Add Player To Team 🚶‍♂️▶👫👬👭
>Admins can add a player to any team. Directors can add a player only in their created teams.

### Remove Player From Team 👫👬👭▶🚶‍♂️
>Admins can remove a player from any team. Directors can remove a player only from their created teams.


<!-- Matches -->

### <h2><br><br>MATCHES ⚽🏀🏐🎾</h2>
### View All Matches 👀
>Accessible to everyone, providing the opportunity to view matches. Matches can be filtered by completed, upcoming, and all, and sorted in ascending or descending order.

### Enter Match Winner 🥇
>Accessible to the match creator and admin. Requires entry of the match ID and points for the first and second participants.

### View Matches By Tournament 👀
>Accessible to everyone. Upon entering the tournament name, it displays all matches associated with it.

### Delete Matches By Tournament ❌
>Accessible to the tournament creator and admin. Deletes matches from a specified tournament.

### View Match By Id 🔎
>Accessible to everyone. Retrieves information about a match based on the provided ID.

### Delete Match ❌
>Accessible to the match creator and admin. Deletes a match based on its ID.

### Create Match ⚽
>Accessible to admin and director. Involves entering participants 1 and 2. If they are players and do not exist in the database, new profiles are created. The new profile needs further editing. Options: one on one/team game, time limit/score limit, type of sport.

### Matches Simulations 🔀
>Accessible to admin and director. Checks for unplayed matches and randomly assigns points to players, determining the winner.


<!-- Tournaments -->

### <h2><br><br>TOURNAMENTS 🤺⛹️‍♂️🏋️‍♂️🚴‍♂️</h2>
### View All Tournaments 👀
>Accessible to everyone. Displays tournaments with options to filter by upcoming/completed/all tournaments, and sort in ascending or descending order.

### View Tournament By Title 🔎
>Accessible to everyone. Shows information about a tournament based on its name.

### Delete Tournament By Title ❌
>Accessible to admin and tournament creator. Deletes a tournament by name and all matches associated with it.

### View Tournament Participants 🔎
>Accessible to everyone. Displays all participants in the tournament.

### Create Tournament 🤺
>Accessible to admin and director. Involves entering participants 1 and 2. If they are players and do not exist in the database, new profiles are created. The new profile needs further editing. Options: one on one/team game, time limit/score limit, number of participants, type of sport.

### Add Participant To Tournament 🚶‍♂️▶🤺
>Accessible to admin and creator. Participants are added one by one. After each addition, it returns information on whether the participant has been added and how many participants are needed to complete the tournament. If an inputted player does not exist, a profile is created, which needs to be filled in later.

### Arrange Tournament Matches 🤼🤼🤼
>Accessible to admin and creator. Creates matches by randomly combining participants. Match days can be limited.

### Set League Tournament Winner 🏆
>Accessible to admin and creator. Calculates points for participants and awards the trophy. In points-based tournaments, the participant with the most points wins. In time-based tournaments, the participant with the shortest time wins.


<!-- Statistics -->

### <h2><br><br>STATISTICS 🤺⛹️‍♂️🏋️‍♂️🚴‍♂️</h2>


### Statistics Single Player Or Team Statistics 📈
>Accessible to everyone. Displays information about a participant – player or team. Includes name, total wins, total losses, tournaments played, tournament trophies, most frequent opponent, games against the most frequent opponent, best opponent, games against the best opponent, worst opponent, games against the worst opponent. List of all matches, sorted in ascending and descending order.

### All Players Or Teams Statistics 📉
>Accessible to everyone. Shows a ranking of teams and players with filtering options for number of wins, losses, tournament participations, and tournament wins. Sorted in ascending and descending order.

### View Tournament Results 📊
>Accessible to everyone. Displays the results of a tournament by name.


<!-- MySQL Diagram -->

### <h1><br>MYSQL DIAGRAM 🧾</h1>

<img align="left" src="https://cdn.discordapp.com/attachments/1171040731104808962/1181911482552827945/Shema_match_score_db.jpg?ex=6582c7d8&is=657052d8&hm=d2ad72bc712cc79194f711874cdfb0b9f9d68a29787ed975904416e131d0ced5&" alt="diagram" width="1020px"/>

# <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>ADDITIONAL INFORMATION:


## TOKEN ADDITIONAL INFORMATION 
>Authentication tokens are the most valuable thing in the app. That's why we warn you to be extremely cautious❗<br>
>Don't share your token/password with anyone❗❗❗<br>


## EMAIL ADDITIONAL INFORMATION:
>Emails will arrive at customers inboxes with a caution message that the email sender might be a hacker and to not open any shared links. That is because the security options of the company's gmail address are turned off. You camn ignore this message when testing the app❗<br>


### [Click to return to the top](#sequence-sections-in-our-program)
------------------------------------------------------------------------------
```
# THIS STRUCTURED INFORMATION WAS BROUGHT TO YOU BY DIMITAR/PETAR/YASEN