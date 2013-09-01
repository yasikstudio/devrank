CREATE TABLE `devrank`.`users` (
  `id` INT NOT NULL ,
  `login` VARCHAR(45) NULL ,
  `name` VARCHAR(45) NULL ,
  `etag` VARCHAR(45) NULL ,
  `gravatar_id` VARCHAR(45) NULL ,
  `avatar_url` VARCHAR(200) NULL ,
  `blog` VARCHAR(100) NULL ,
  `location` VARCHAR(100) NULL ,
  `email` VARCHAR(45) NULL ,
  `bio` VARCHAR(45) NULL ,
  `company` VARCHAR(45) NULL ,
  `hireable` BIT NULL ,
  `crawled_at` DATETIME NULL ,
  PRIMARY KEY (`id`) );

CREATE TABLE `devrank`.`followings` (
  `follower_id` INT NOT NULL ,
  `following_id` INT NOT NULL ,
  PRIMARY KEY (`follower_id`, `following_id`) );

CREATE TABLE `devrank`.`friendship` (
  `owner_id` INT NOT NULL ,
  `friend_id` INT NOT NULL ,
  PRIMARY KEY (`owner_id`, `friend_id`) );

CREATE TABLE `devrank`.`repos` (
  `id` INT NOT NULL,
  `owner_id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `description` TEXT NULL,
  `fork` BIT NOT NULL,
  `language` VARCHAR(45) NOT NULL,
  `etag` VARCHAR(45) NULL,
  `crawled_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `devrank`.`watchers` (
  `watcher_id` INT NOT NULL,
  `repo_id` INT NOT NULL,
  PRIMARY KEY (`watcher_id`, `repo_id`));

CREATE TABLE `devrank`.`stargazers` (
  `stargazer_id` INT NOT NULL,
  `repo_id` INT NOT NULL,
  PRIMARY KEY (`stargazer_id`, `repo_id`));

CREATE TABLE `devrank`.`contributors` (
  `repo_id` INT NOT NULL,
  `contributor_id` INT NOT NULL,
  `contributions` INT,
  PRIMARY KEY (`repo_id`,`contributor_id`));

CREATE TABLE `devrank`.`orgs` (
  `org_id` INT NOT NULL,
  `member_id` INT NOT NULL,
  PRIMARY KEY (`org_id`, `member_id`));
