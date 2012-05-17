SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `marks_billing` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `marks_billing` ;

-- -----------------------------------------------------
-- Table `marks_billing`.`staging`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `marks_billing`.`staging` (
  `path` VARCHAR(500) NOT NULL ,
  `month` VARCHAR(3) NOT NULL ,
  `day` INT NOT NULL ,
  `hour` INT NOT NULL ,
  `minute` INT NOT NULL ,
  `second` INT NOT NULL ,
  `year` INT NOT NULL ,
  `status` VARCHAR(45) NOT NULL )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `marks_billing`.`experiment`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `marks_billing`.`experiment` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `path` VARCHAR(500) NOT NULL ,
  PRIMARY KEY (`path`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `marks_billing`.`event`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `marks_billing`.`event` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `path` VARCHAR(500) NOT NULL ,
  `time` DATETIME NULL ,
  `isstart` TINYINT(1)  NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_event_experiment` (`path` ASC) ,
  CONSTRAINT `fk_event_experiment`
    FOREIGN KEY (`path` )
    REFERENCES `marks_billing`.`experiment` (`path` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
