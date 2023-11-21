CREATE TABLE `users` (
	`user_id` int NOT NULL AUTO_INCREMENT,
	`username` varchar(20) NOT NULL,
	`password` varchar(64) NOT NULL,
	`created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
	`profile_picture` varchar(64),
	PRIMARY KEY (`user_id`)
);

CREATE TABLE `friends` (
	`friends_id` int NOT NULL AUTO_INCREMENT,
	`requester_user_id` int NOT NULL,
	`target_user_id` int NOT NULL,
	PRIMARY KEY (`friends_id`)
);

CREATE TABLE `tokens` (
	`token_id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    	`token` varchar(64) NOT NULL,
	PRIMARY KEY (`token_id`)
);

CREATE TABLE `posts` (
	`post_id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`name` varchar(50) NOT NULL,
	`type` SMALLINT NOT NULL DEFAULT 0,
	`volume` FLOAT NOT NULL,
	`review` text,
	`created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
	`picture` varchar(64),
	PRIMARY KEY (`post_id`)
);

ALTER TABLE `friends` ADD CONSTRAINT `friends_fk0` FOREIGN KEY (`requester_user_id`) REFERENCES `users`(`user_id`);

ALTER TABLE `friends` ADD CONSTRAINT `friends_fk1` FOREIGN KEY (`target_user_id`) REFERENCES `users`(`user_id`);

ALTER TABLE `tokens` ADD CONSTRAINT `tokens_fk0` FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`);

ALTER TABLE `posts` ADD CONSTRAINT `posts_fk0` FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`);


