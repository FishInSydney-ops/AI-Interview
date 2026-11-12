-- 云枢智学 MySQL 8.4 初始结构；禁止物理外键；仅在空库通过 Alembic 初始化。
-- 基于 SQLAlchemy metadata；UTC DATETIME(6)，数据库连接时区设为 +00:00。
-- active_guard 等为实现软删除唯一约束的派生列，不供 API 写入。

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
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_admin_log_time ON admin_operation_log (created_at, id);

CREATE TABLE admin_password_reset (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	admin_user_id BIGINT NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	expires_at DATETIME(6) NOT NULL, 
	consumed_at DATETIME(6), 
	PRIMARY KEY (id), 
	UNIQUE (admin_user_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


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
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE admin_role_permission (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	role_id BIGINT NOT NULL, 
	permission VARCHAR(64) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (role_id, permission)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE admin_session (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	admin_user_id BIGINT NOT NULL, 
	session_token_hash VARCHAR(64) NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	expires_at DATETIME(6) NOT NULL, 
	revoked_at DATETIME(6), 
	restricted INTEGER NOT NULL DEFAULT '0', 
	PRIMARY KEY (id), 
	CHECK (length(session_token_hash) > 0), 
	UNIQUE (session_token_hash)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_admin_session_owner ON admin_session (admin_user_id, revoked_at);

CREATE TABLE admin_user (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	username VARCHAR(64) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	phone VARCHAR(32) NOT NULL DEFAULT '', 
	email VARCHAR(254) NOT NULL DEFAULT '', 
	role_id BIGINT, 
	is_super INTEGER NOT NULL DEFAULT '0', 
	enabled INTEGER NOT NULL DEFAULT '1', 
	must_change_password INTEGER NOT NULL DEFAULT '0', 
	version INTEGER NOT NULL DEFAULT '1', 
	last_login_at DATETIME(6), 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	active_guard INTEGER GENERATED ALWAYS AS (CASE WHEN is_super = 1 THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (length(trim(username)) > 0), 
	CHECK (enabled IN (0,1) AND is_super IN (0,1) AND must_change_password IN (0,1)), 
	UNIQUE (username)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE UNIQUE INDEX uq_admin_single_active ON admin_user (active_guard);

CREATE TABLE content_deletion_batch (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	root_type VARCHAR(32) NOT NULL, 
	root_id BIGINT NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (root_type IN ('subject', 'stage'))
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE content_deletion_item (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	batch_id BIGINT NOT NULL, 
	entity_type VARCHAR(32) NOT NULL, 
	entity_id BIGINT NOT NULL, 
	restored_at DATETIME(6), 
	pending_guard INTEGER GENERATED ALWAYS AS (CASE WHEN restored_at IS NULL THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (entity_type IN ('subject', 'stage', 'course', 'question', 'learning_route', 'course_subject_link', 'route_course')), 
	UNIQUE (batch_id, entity_type, entity_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE UNIQUE INDEX uq_content_deletion_current ON content_deletion_item (entity_type, entity_id, pending_guard);

CREATE TABLE course (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	stage_id BIGINT NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	course_url VARCHAR(2048) NOT NULL, 
	total_episodes INTEGER NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	cover_url VARCHAR(2048), 
	duration_minutes INTEGER, 
	description TEXT, 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	active_url_hash VARCHAR(64) GENERATED ALWAYS AS (CASE WHEN deleted_at IS NULL THEN SHA2(course_url, 256) ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (length(trim(title)) > 0), 
	CHECK (total_episodes > 0), 
	CHECK (status IN ('published', 'unpublished')), 
	CHECK (duration_minutes IS NULL OR duration_minutes >= 0)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_course_stage ON course (stage_id);
CREATE UNIQUE INDEX uq_course_url_active ON course (active_url_hash);

CREATE TABLE course_subject_link (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	course_id BIGINT NOT NULL, 
	subject_id BIGINT NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	active_guard INTEGER GENERATED ALWAYS AS (CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_course_subject_subject ON course_subject_link (subject_id, course_id);
CREATE UNIQUE INDEX uq_course_subject_active ON course_subject_link (course_id, subject_id, active_guard);

CREATE TABLE learning_route (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	subject_id BIGINT NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	description TEXT, 
	is_enabled INTEGER NOT NULL DEFAULT 1, 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	PRIMARY KEY (id), 
	CHECK (length(trim(name)) > 0), 
	CHECK (is_enabled IN (0, 1))
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_route_subject ON learning_route (subject_id, is_enabled);

CREATE TABLE login_lock (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	account_domain VARCHAR(32) NOT NULL, 
	account_key VARCHAR(128) NOT NULL, 
	failed_count INTEGER NOT NULL DEFAULT 0, 
	locked_until VARCHAR(32), 
	updated_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (account_domain IN ('student', 'admin')), 
	CHECK (length(account_key) > 0), 
	CHECK (failed_count >= 0), 
	UNIQUE (account_domain, account_key)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE mistake_record (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	student_id BIGINT NOT NULL, 
	question_id BIGINT NOT NULL, 
	last_wrong_answer_id BIGINT NOT NULL, 
	error_count INTEGER NOT NULL, 
	consecutive_correct INTEGER NOT NULL DEFAULT 0, 
	last_wrong_at DATETIME(6) NOT NULL, 
	removed_at DATETIME(6), 
	PRIMARY KEY (id), 
	CHECK (error_count > 0), 
	CHECK (consecutive_correct BETWEEN 0 AND 3), 
	UNIQUE (student_id, question_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_mistake_review ON mistake_record (student_id, removed_at, consecutive_correct, last_wrong_at);

CREATE TABLE platform_settings (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(64) NOT NULL, 
	description VARCHAR(1000) NOT NULL DEFAULT '', 
	logo_file_id BIGINT, 
	avatar_file_id BIGINT, 
	version INTEGER NOT NULL DEFAULT '1', 
	updated_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE practice_answer (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	session_id BIGINT NOT NULL, 
	question_id BIGINT NOT NULL, 
	question_type_snapshot VARCHAR(32) NOT NULL, 
	prompt_snapshot TEXT NOT NULL, 
	explanation_snapshot TEXT, 
	is_correct INTEGER NOT NULL, 
	answered_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (question_type_snapshot IN ('single', 'multiple', 'judgment')), 
	CHECK (is_correct IN (0, 1)), 
	UNIQUE (session_id, question_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_answer_question ON practice_answer (question_id, answered_at);

CREATE TABLE practice_answer_option (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	practice_answer_id BIGINT NOT NULL, 
	option_order INTEGER NOT NULL, 
	content_snapshot TEXT NOT NULL, 
	is_correct_snapshot INTEGER NOT NULL, 
	is_selected INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (option_order > 0), 
	CHECK (is_correct_snapshot IN (0, 1)), 
	CHECK (is_selected IN (0, 1)), 
	UNIQUE (practice_answer_id, option_order)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE practice_session (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	student_id BIGINT NOT NULL, 
	session_type VARCHAR(32) NOT NULL, 
	stage_id BIGINT, 
	status VARCHAR(32) NOT NULL, 
	question_count INTEGER NOT NULL, 
	started_at DATETIME(6) NOT NULL, 
	completed_at DATETIME(6), 
	in_progress_guard INTEGER GENERATED ALWAYS AS (CASE WHEN status = 'in_progress' THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (session_type IN ('stage', 'mistake')), 
	CHECK (status IN ('in_progress', 'completed', 'abandoned')), 
	CHECK (question_count BETWEEN 0 AND 10), 
	CHECK ((session_type = 'stage' AND stage_id IS NOT NULL) OR (session_type = 'mistake' AND stage_id IS NULL)), 
	CHECK ((status = 'completed' AND completed_at IS NOT NULL AND question_count > 0) OR (status <> 'completed' AND completed_at IS NULL))
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_session_stage ON practice_session (student_id, stage_id, status);
CREATE INDEX ix_session_student_completed ON practice_session (student_id, status, completed_at);
CREATE UNIQUE INDEX uq_practice_session_student_in_progress ON practice_session (student_id, in_progress_guard);

CREATE TABLE practice_session_item (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	session_id BIGINT NOT NULL, 
	question_id BIGINT NOT NULL, 
	question_order INTEGER NOT NULL, 
	presented_fingerprint VARCHAR(128), 
	item_status VARCHAR(32) NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (question_order > 0), 
	CHECK (presented_fingerprint IS NULL OR length(presented_fingerprint) > 0), 
	CHECK (item_status IN ('pending', 'answered', 'removed')), 
	UNIQUE (session_id, question_id), 
	UNIQUE (session_id, question_order)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_session_item_status ON practice_session_item (session_id, item_status, question_order);

CREATE TABLE question (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	stage_id BIGINT NOT NULL, 
	question_type VARCHAR(32) NOT NULL, 
	difficulty VARCHAR(32) NOT NULL, 
	prompt TEXT NOT NULL, 
	explanation TEXT, 
	reference_source VARCHAR(2048), 
	status VARCHAR(32) NOT NULL, 
	answer_revision INTEGER NOT NULL DEFAULT 1, 
	last_published_fingerprint VARCHAR(128), 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	PRIMARY KEY (id), 
	CHECK (question_type IN ('single', 'multiple', 'judgment')), 
	CHECK (difficulty IN ('easy', 'medium', 'hard')), 
	CHECK (length(trim(prompt)) > 0), 
	CHECK (status IN ('draft', 'published', 'unpublished')), 
	CHECK (answer_revision >= 1), 
	CHECK (last_published_fingerprint IS NULL OR length(last_published_fingerprint) > 0), 
	CHECK (status <> 'published' OR last_published_fingerprint IS NOT NULL)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_question_stage_status ON question (stage_id, status, deleted_at);

CREATE TABLE question_option (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	question_id BIGINT NOT NULL, 
	option_order INTEGER NOT NULL, 
	content TEXT NOT NULL, 
	is_correct INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (option_order > 0), 
	CHECK (length(trim(content)) > 0), 
	CHECK (is_correct IN (0, 1)), 
	UNIQUE (question_id, option_order)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE rate_limit_counter (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	action VARCHAR(64) NOT NULL, 
	dimension_type VARCHAR(32) NOT NULL, 
	dimension_key VARCHAR(128) NOT NULL, 
	window_start_at DATETIME(6) NOT NULL, 
	expires_at DATETIME(6) NOT NULL, 
	request_count INTEGER NOT NULL DEFAULT 0, 
	PRIMARY KEY (id), 
	CHECK (length(action) > 0), 
	CHECK (dimension_type IN ('ip', 'account')), 
	CHECK (length(dimension_key) > 0), 
	CHECK (request_count >= 0), 
	UNIQUE (action, dimension_type, dimension_key, window_start_at)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_rate_limit_expiry ON rate_limit_counter (expires_at);

CREATE TABLE route_course (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	route_id BIGINT NOT NULL, 
	course_id BIGINT NOT NULL, 
	sort_order INTEGER NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	active_guard INTEGER GENERATED ALWAYS AS (CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (sort_order > 0)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE UNIQUE INDEX uq_route_course_active ON route_course (route_id, course_id, active_guard);
CREATE UNIQUE INDEX uq_route_order_active ON route_course (route_id, sort_order, active_guard);

CREATE TABLE stage (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	subject_id BIGINT NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	sort_order INTEGER NOT NULL DEFAULT 0, 
	is_enabled INTEGER NOT NULL DEFAULT 1, 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	active_guard INTEGER GENERATED ALWAYS AS (CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (length(trim(name)) > 0), 
	CHECK (is_enabled IN (0, 1))
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_stage_subject ON stage (subject_id, sort_order);
CREATE UNIQUE INDEX uq_stage_name_active ON stage (subject_id, name, active_guard);

CREATE TABLE stored_file (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	object_key VARCHAR(255) NOT NULL, 
	content_type VARCHAR(64) NOT NULL, 
	size_bytes BIGINT NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (object_key)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE student (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	username VARCHAR(64) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	nickname VARCHAR(128), 
	avatar_path VARCHAR(1024), 
	onboarding_completed_at DATETIME(6), 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	PRIMARY KEY (id), 
	CHECK (length(trim(username)) > 0), 
	UNIQUE (username)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE student_episode_completion (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	student_id BIGINT NOT NULL, 
	course_id BIGINT NOT NULL, 
	episode_number INTEGER NOT NULL, 
	completed_at DATETIME(6) NOT NULL, 
	revoked_at DATETIME(6), 
	PRIMARY KEY (id), 
	CHECK (episode_number > 0), 
	UNIQUE (student_id, course_id, episode_number)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_episode_course_student ON student_episode_completion (course_id, student_id);

CREATE TABLE student_password_reset (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	student_id BIGINT NOT NULL, 
	temporary_password_hash VARCHAR(255) NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	consumed_at DATETIME(6), 
	revoked_at DATETIME(6), 
	pending_guard INTEGER GENERATED ALWAYS AS (CASE WHEN consumed_at IS NULL AND revoked_at IS NULL THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (consumed_at IS NULL OR revoked_at IS NULL)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE UNIQUE INDEX uq_student_reset_pending ON student_password_reset (student_id, pending_guard);

CREATE TABLE student_session (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	student_id BIGINT NOT NULL, 
	session_token_hash VARCHAR(64) NOT NULL, 
	session_purpose VARCHAR(32) NOT NULL, 
	password_reset_id BIGINT, 
	created_at DATETIME(6) NOT NULL, 
	expires_at DATETIME(6) NOT NULL, 
	revoked_at DATETIME(6), 
	PRIMARY KEY (id), 
	CHECK (length(session_token_hash) > 0), 
	CHECK (session_purpose IN ('normal', 'password_reset')), 
	CHECK ((session_purpose = 'password_reset' AND password_reset_id IS NOT NULL) OR (session_purpose = 'normal' AND password_reset_id IS NULL)), 
	UNIQUE (session_token_hash)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE INDEX ix_student_session_owner ON student_session (student_id, revoked_at);

CREATE TABLE student_subject_preference (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	student_id BIGINT NOT NULL, 
	subject_id BIGINT NOT NULL, 
	created_at DATETIME(6) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_id, subject_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;


CREATE TABLE subject (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(128) NOT NULL, 
	icon VARCHAR(255), 
	description TEXT, 
	sort_order INTEGER NOT NULL DEFAULT 0, 
	created_at DATETIME(6) NOT NULL, 
	updated_at DATETIME(6) NOT NULL, 
	deleted_at DATETIME(6), 
	active_guard INTEGER GENERATED ALWAYS AS (CASE WHEN deleted_at IS NULL THEN 1 ELSE NULL END) STORED, 
	PRIMARY KEY (id), 
	CHECK (length(trim(name)) > 0)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_bin;

CREATE UNIQUE INDEX uq_subject_name_active ON subject (name, active_guard);

