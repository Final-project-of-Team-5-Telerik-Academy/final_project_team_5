-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema match_score_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `match_score_db` DEFAULT CHARACTER SET latin1 ;
USE `match_score_db` ;

-- -----------------------------------------------------
-- Table `match_score_db`.`blocked_players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`blocked_players` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `players_id` INT(11) NOT NULL,
  `ban_status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`teams`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`teams` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `team_name` VARCHAR(45) NOT NULL,
  `number_of_players` INT(11) NULL DEFAULT 0,
  `owners_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`players` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `full_name` VARCHAR(45) NOT NULL,
  `country` VARCHAR(45) NOT NULL,
  `sports_club` VARCHAR(45) NOT NULL,
  `is_active` INT(11) NULL DEFAULT 0,
  `is_connected` INT(11) NULL DEFAULT 0,
  `teams_id` INT(11) NULL DEFAULT NULL,
  `blocked_players_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_players_teams1_idx` (`teams_id` ASC) VISIBLE,
  INDEX `fk_players_blocked_players1_idx` (`blocked_players_id` ASC) VISIBLE,
  CONSTRAINT `fk_players_blocked_players1`
    FOREIGN KEY (`blocked_players_id`)
    REFERENCES `match_score_db`.`blocked_players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_players_teams1`
    FOREIGN KEY (`teams_id`)
    REFERENCES `match_score_db`.`teams` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `full_name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(70) NOT NULL,
  `password` VARCHAR(150) NOT NULL,
  `gender` VARCHAR(10) NOT NULL,
  `role` VARCHAR(10) NOT NULL,
  `players_id` INT(11) NULL DEFAULT NULL,
  `is_verified` INT(11) NULL DEFAULT 0,
  `verification_code` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_users_players1_idx` (`players_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_players1`
    FOREIGN KEY (`players_id`)
    REFERENCES `match_score_db`.`players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`admin_requests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`admin_requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `type_of_request` VARCHAR(45) NOT NULL,
  `players_id` INT(11) NULL DEFAULT NULL,
  `users_id` INT(11) NOT NULL,
  `status` VARCHAR(45) NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  INDEX `fk_admin_requests_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_admin_requests_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `match_score_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`director_requests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`director_requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `full_name` VARCHAR(45) NOT NULL,
  `country` VARCHAR(45) NOT NULL,
  `sports_club` VARCHAR(45) NOT NULL,
  `users_id` INT(11) NOT NULL,
  `status` VARCHAR(45) NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  INDEX `fk_director_requests_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_director_requests_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `match_score_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`matches`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`matches` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `match_format` VARCHAR(45) NOT NULL,
  `game_type` VARCHAR(45) NOT NULL,
  `sport` VARCHAR(45) NOT NULL,
  `participant_1` VARCHAR(45) NOT NULL,
  `participant_2` VARCHAR(45) NOT NULL,
  `creator` VARCHAR(45) NOT NULL,
  `date` DATE NOT NULL,
  `winner` VARCHAR(45) NULL DEFAULT NULL,
  `tournament_name` VARCHAR(100) NULL DEFAULT NULL,
  `stage` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`players_statistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`players_statistics` (
  `players_id` INT(11) NOT NULL,
  `player_name` VARCHAR(45) NULL DEFAULT NULL,
  `player_score` FLOAT NULL DEFAULT NULL,
  `opponent_name` VARCHAR(45) NULL DEFAULT NULL,
  `opponent_score` FLOAT NULL DEFAULT NULL,
  `win` INT(11) NULL DEFAULT NULL,
  `loss` INT(11) NULL DEFAULT NULL,
  `matches_id` INT(11) NOT NULL,
  `tournament_name` VARCHAR(45) NULL DEFAULT NULL,
  `tournament_trophy` INT(11) NULL DEFAULT 0,
  `stage` INT(11) NULL DEFAULT NULL,
  `date` DATE NULL DEFAULT NULL,
  INDEX `fk_players_statistics_players1_idx` (`players_id` ASC) VISIBLE,
  INDEX `fk_players_statistics_matches1_idx` (`matches_id` ASC) VISIBLE,
  CONSTRAINT `fk_players_statistics_matches1`
    FOREIGN KEY (`matches_id`)
    REFERENCES `match_score_db`.`matches` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_players_statistics_players1`
    FOREIGN KEY (`players_id`)
    REFERENCES `match_score_db`.`players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`teams_statistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`teams_statistics` (
  `teams_id` INT(11) NOT NULL,
  `team_name` VARCHAR(45) NULL DEFAULT NULL,
  `team_score` FLOAT NULL DEFAULT NULL,
  `opponent_name` VARCHAR(45) NULL DEFAULT NULL,
  `opponent_score` FLOAT NULL DEFAULT NULL,
  `win` INT(11) NULL DEFAULT NULL,
  `loss` INT(11) NULL DEFAULT NULL,
  `matches_id` INT(11) NOT NULL,
  `tournament_name` VARCHAR(45) NULL DEFAULT NULL,
  `tournament_trophy` INT(11) NULL DEFAULT 0,
  `stage` INT(11) NULL DEFAULT 0,
  `date` DATE NULL DEFAULT NULL,
  INDEX `fk_teams_statistics_teams1_idx` (`teams_id` ASC) VISIBLE,
  INDEX `fk_teams_statistics_matches1_idx` (`matches_id` ASC) VISIBLE,
  CONSTRAINT `fk_teams_statistics_matches1`
    FOREIGN KEY (`matches_id`)
    REFERENCES `match_score_db`.`matches` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_teams_statistics_teams1`
    FOREIGN KEY (`teams_id`)
    REFERENCES `match_score_db`.`teams` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`tournaments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`tournaments` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `number_participants` INT(11) NULL DEFAULT 4,
  `t_format` VARCHAR(45) NOT NULL,
  `match_format` VARCHAR(45) NULL DEFAULT NULL,
  `sport` VARCHAR(45) NOT NULL,
  `date` DATE NOT NULL,
  `prize` INT(11) NOT NULL,
  `game_type` VARCHAR(45) NOT NULL,
  `winner` VARCHAR(45) NULL DEFAULT NULL,
  `users_creator_id` INT(11) NOT NULL,
  `is_complete` TINYINT(4) NOT NULL DEFAULT 0,
  `stage` INT(11) NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `fk_tournaments_users1_idx` (`users_creator_id` ASC) VISIBLE,
  CONSTRAINT `fk_tournaments_users1`
    FOREIGN KEY (`users_creator_id`)
    REFERENCES `match_score_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`tournaments_players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`tournaments_players` (
  `players_id` INT(11) NOT NULL,
  `tournaments_id` INT(11) NOT NULL,
  `tournaments_title` VARCHAR(45) NOT NULL,
  `player_name` VARCHAR(45) NOT NULL,
  `stage` INT(11) NOT NULL DEFAULT 0,
  INDEX `fk_tournaments_players_tournaments1_idx` (`tournaments_id` ASC) VISIBLE,
  INDEX `fk_tournaments_players_players1_idx` (`players_id` ASC) VISIBLE,
  CONSTRAINT `fk_tournaments_players_players1`
    FOREIGN KEY (`players_id`)
    REFERENCES `match_score_db`.`players` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_players_tournaments1`
    FOREIGN KEY (`tournaments_id`)
    REFERENCES `match_score_db`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `match_score_db`.`tournaments_teams`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_score_db`.`tournaments_teams` (
  `teams_id` INT(11) NOT NULL,
  `teams_name` VARCHAR(45) NOT NULL,
  `tournaments_id` INT(11) NOT NULL,
  `tournaments_title` VARCHAR(45) NOT NULL,
  `stage` INT(11) NOT NULL DEFAULT 0,
  INDEX `fk_tournaments_teams_tournaments1_idx` (`tournaments_id` ASC) VISIBLE,
  INDEX `fk_tournaments_teams_teams1_idx` (`teams_id` ASC) VISIBLE,
  CONSTRAINT `fk_tournaments_teams_teams1`
    FOREIGN KEY (`teams_id`)
    REFERENCES `match_score_db`.`teams` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_teams_tournaments1`
    FOREIGN KEY (`tournaments_id`)
    REFERENCES `match_score_db`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


-- Reset AUTO_INCREMENT values for tables
ALTER TABLE match_score_db.teams AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.players AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.users AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.admin_requests AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.matches AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.tournaments AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.director_requests AUTO_INCREMENT = 1;
ALTER TABLE match_score_db.blocked_players AUTO_INCREMENT = 1;