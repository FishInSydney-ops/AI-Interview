
CREATE TABLE admin_role (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(64) NOT NULL, 
	code VARCHAR(64) NOT NULL, 
	description VARCHAR(500) NOT NULL DEFAULT '', 
	built_in INTEGER NOT NULL DEFAULT '0', 
	version INTEGER NOT NULL DEFAULT '1', 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	UNIQUE (code)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin

;

CREATE TABLE admin_role_permission (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	role_id BIGINT NOT NULL, 
	permission VARCHAR(64) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (role_id, permission)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin

;

CREATE TABLE admin_password_reset (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	admin_user_id BIGINT NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	expires_at DATETIME(6) NOT NULL, 
	consumed_at DATETIME(6), 
	PRIMARY KEY (id), 
	UNIQUE (admin_user_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin

;

CREATE TABLE admin_operation_log (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	actor_id BIGINT, 
	actor_name VARCHAR(64) NOT NULL, 
	action VARCHAR(64) NOT NULL, 
	target VARCHAR(255) NOT NULL, 
	ip VARCHAR(128) NOT NULL, 
	outcome VARCHAR(32) NOT NULL, 
	request_id VARCHAR(64) NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin

;

CREATE TABLE stored_file (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	object_key VARCHAR(255) NOT NULL, 
	content_type VARCHAR(64) NOT NULL, 
	size_bytes BIGINT NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (object_key)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin

;

CREATE TABLE platform_settings (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(64) NOT NULL, 
	description VARCHAR(1000) NOT NULL DEFAULT '', 
	logo_file_id BIGINT, 
	avatar_file_id BIGINT, 
	version INTEGER NOT NULL DEFAULT '1', 
	updated_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin

;