-- 云枢智学首发 SQLite 建表草案：仅供评审和空库验证，未经审核不得用于生产。
-- 全部关联为逻辑关联，无物理外键；时间均为 UTC ISO 8601 文本，由应用写入。
-- 业务主键统一 INTEGER PRIMARY KEY AUTOINCREMENT；本脚本不含种子数据。

CREATE TABLE student (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE CHECK(length(trim(username)) > 0),
  password_hash TEXT NOT NULL,
  nickname TEXT,
  avatar_path TEXT,
  -- 完成或跳过首次偏好引导时写入时间；尚未处理时为空。
  onboarding_completed_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);

-- 候选设计：单独保存临时密码哈希，不能覆盖原密码；使用一次后消费，不设时间期限。
-- 消费后的受限改密会话与并发规则尚待设计，不能仅凭本表完成身份验证。
CREATE TABLE student_password_reset (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  temporary_password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  consumed_at TEXT,
  revoked_at TEXT,
  CHECK(consumed_at IS NULL OR revoked_at IS NULL)
);
CREATE UNIQUE INDEX uq_student_reset_pending ON student_password_reset(student_id)
  WHERE consumed_at IS NULL AND revoked_at IS NULL;

-- 学员服务端会话候选设计：凭据只保存哈希，通过独立 HttpOnly Cookie 传输；普通会话 7 天、受限改密会话 15 分钟，具体安全属性及事务待评审。
CREATE TABLE student_session (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  session_token_hash TEXT NOT NULL UNIQUE CHECK(length(session_token_hash) > 0),
  session_purpose TEXT NOT NULL CHECK(session_purpose IN ('normal', 'password_reset')),
  password_reset_id INTEGER,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT,
  CHECK((session_purpose = 'password_reset' AND password_reset_id IS NOT NULL)
     OR (session_purpose = 'normal' AND password_reset_id IS NULL))
);
CREATE INDEX ix_student_session_owner ON student_session(student_id, revoked_at);

CREATE TABLE admin_user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE CHECK(length(trim(username)) > 0),
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);

-- 单例索引约束有效管理员不超过一名；是否允许停用或恢复待确认。
CREATE UNIQUE INDEX uq_admin_single_active ON admin_user ((1)) WHERE deleted_at IS NULL;

-- 后台独立服务端会话，固定有效期由应用校验；凭据仅存哈希。
CREATE TABLE admin_session (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  admin_user_id INTEGER NOT NULL,
  session_token_hash TEXT NOT NULL UNIQUE CHECK(length(session_token_hash) > 0),
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT
);
CREATE INDEX ix_admin_session_owner ON admin_session(admin_user_id, revoked_at);


CREATE TABLE login_lock (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_domain TEXT NOT NULL CHECK(account_domain IN ('student', 'admin')),
  account_key TEXT NOT NULL CHECK(length(account_key) > 0),
  failed_count INTEGER NOT NULL DEFAULT 0 CHECK(failed_count >= 0),
  locked_until TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE(account_domain, account_key)
);

-- dimension_key 的规范化/脱敏和过期清理策略待确认；不可存明文密码或验证码。
CREATE TABLE rate_limit_counter (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL CHECK(length(action) > 0),
  dimension_type TEXT NOT NULL CHECK(dimension_type IN ('ip', 'account')),
  dimension_key TEXT NOT NULL CHECK(length(dimension_key) > 0),
  window_start_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 0 CHECK(request_count >= 0),
  UNIQUE(action, dimension_type, dimension_key, window_start_at)
);
CREATE INDEX ix_rate_limit_expiry ON rate_limit_counter(expires_at);

CREATE TABLE subject (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL CHECK(length(trim(name)) > 0),
  icon TEXT,
  description TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE UNIQUE INDEX uq_subject_name_active ON subject(name) WHERE deleted_at IS NULL;

CREATE TABLE stage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject_id INTEGER NOT NULL,
  name TEXT NOT NULL CHECK(length(trim(name)) > 0),
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_enabled INTEGER NOT NULL DEFAULT 1 CHECK(is_enabled IN (0, 1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE UNIQUE INDEX uq_stage_name_active ON stage(subject_id, name) WHERE deleted_at IS NULL;
CREATE INDEX ix_stage_subject ON stage(subject_id, sort_order);

-- 候选设计：记录实际由一次删除操作标记的内容，以区分先前已删除的记录。
CREATE TABLE content_deletion_batch (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  root_type TEXT NOT NULL CHECK(root_type IN ('subject', 'stage')),
  root_id INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE content_deletion_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id INTEGER NOT NULL,
  entity_type TEXT NOT NULL CHECK(entity_type IN ('subject', 'stage', 'course', 'question', 'learning_route', 'course_subject_link', 'route_course')),
  entity_id INTEGER NOT NULL,
  restored_at TEXT,
  UNIQUE(batch_id, entity_type, entity_id)
);
CREATE UNIQUE INDEX uq_content_deletion_current ON content_deletion_item(entity_type, entity_id) WHERE restored_at IS NULL;

CREATE TABLE course (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stage_id INTEGER NOT NULL,
  title TEXT NOT NULL CHECK(length(trim(title)) > 0),
  course_url TEXT NOT NULL,
  total_episodes INTEGER NOT NULL CHECK(total_episodes > 0),
  -- 课程是否对学员上架；与逻辑删除相互独立。
  status TEXT NOT NULL CHECK(status IN ('published', 'unpublished')),
  cover_url TEXT,
  duration_minutes INTEGER CHECK(duration_minutes IS NULL OR duration_minutes >= 0),
  description TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE INDEX ix_course_stage ON course(stage_id);
-- 仅按保存的完整链接严格相等去重；不移除参数、不提取 BV 号。
CREATE UNIQUE INDEX uq_course_url_active ON course(course_url) WHERE deleted_at IS NULL;

-- 仅存跨学科关联；课程归属学科由 course.stage_id → stage.subject_id 确定。
CREATE TABLE course_subject_link (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER NOT NULL,
  subject_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE UNIQUE INDEX uq_course_subject_active ON course_subject_link(course_id, subject_id) WHERE deleted_at IS NULL;
CREATE INDEX ix_course_subject_subject ON course_subject_link(subject_id, course_id);

CREATE TABLE learning_route (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject_id INTEGER NOT NULL,
  name TEXT NOT NULL CHECK(length(trim(name)) > 0),
  description TEXT,
  is_enabled INTEGER NOT NULL DEFAULT 1 CHECK(is_enabled IN (0, 1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE INDEX ix_route_subject ON learning_route(subject_id, is_enabled);

CREATE TABLE route_course (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  route_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  sort_order INTEGER NOT NULL CHECK(sort_order > 0),
  created_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE UNIQUE INDEX uq_route_course_active ON route_course(route_id, course_id) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX uq_route_order_active ON route_course(route_id, sort_order) WHERE deleted_at IS NULL;

-- 保留超出课程当前总集数的完成记录；未完成无须有行。
CREATE TABLE student_episode_completion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  episode_number INTEGER NOT NULL CHECK(episode_number > 0),
  completed_at TEXT NOT NULL,
  revoked_at TEXT,
  UNIQUE(student_id, course_id, episode_number)
);
CREATE INDEX ix_episode_course_student ON student_episode_completion(course_id, student_id);

CREATE TABLE question (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stage_id INTEGER NOT NULL,
  question_type TEXT NOT NULL CHECK(question_type IN ('single', 'multiple', 'judgment')),
  difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard')),
  prompt TEXT NOT NULL CHECK(length(trim(prompt)) > 0),
  explanation TEXT,
  reference_source TEXT,
  status TEXT NOT NULL CHECK(status IN ('draft', 'published', 'unpublished')),
  -- 作答版本与掌握重置指纹分离；影响判分的变更由服务端事务递增。
  answer_revision INTEGER NOT NULL DEFAULT 1 CHECK(answer_revision >= 1),
  -- 上次成功上架时的题干、选项与标准答案重置指纹，不包含题型；从未上架时可为空。旧页面判分需独立版本校验。
  last_published_fingerprint TEXT CHECK(last_published_fingerprint IS NULL OR length(last_published_fingerprint) > 0),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT,
  CHECK(status <> 'published' OR last_published_fingerprint IS NOT NULL)
);
CREATE INDEX ix_question_stage_status ON question(stage_id, status, deleted_at);

CREATE TABLE question_option (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id INTEGER NOT NULL,
  option_order INTEGER NOT NULL CHECK(option_order > 0),
  content TEXT NOT NULL CHECK(length(trim(content)) > 0),
  is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
  UNIQUE(question_id, option_order)
);

CREATE TABLE practice_session (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  session_type TEXT NOT NULL CHECK(session_type IN ('stage', 'mistake')),
  stage_id INTEGER,
  status TEXT NOT NULL CHECK(status IN ('in_progress', 'completed', 'abandoned')),
  -- 候选设计：当前有效题数可因下架降至零，零题轮次须以未完成状态结束。
  question_count INTEGER NOT NULL CHECK(question_count BETWEEN 0 AND 10),
  started_at TEXT NOT NULL,
  completed_at TEXT,
  CHECK((session_type = 'stage' AND stage_id IS NOT NULL) OR (session_type = 'mistake' AND stage_id IS NULL)),
  CHECK((status = 'completed' AND completed_at IS NOT NULL AND question_count > 0) OR (status <> 'completed' AND completed_at IS NULL))
);
-- 学员最多一轮进行中练习；已完成和已放弃轮次不受此索引限制。
CREATE UNIQUE INDEX uq_practice_session_student_in_progress ON practice_session(student_id) WHERE status = 'in_progress';
CREATE INDEX ix_session_student_completed ON practice_session(student_id, status, completed_at);
CREATE INDEX ix_session_stage ON practice_session(student_id, stage_id, status);

-- 候选设计：服务端保存抽题清单及发给学员的题目版本；支持恢复未完成轮次；并发及版本校验仍需细化。
CREATE TABLE practice_session_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  question_id INTEGER NOT NULL,
  question_order INTEGER NOT NULL CHECK(question_order > 0),
  presented_fingerprint TEXT CHECK(presented_fingerprint IS NULL OR length(presented_fingerprint) > 0),
  item_status TEXT NOT NULL CHECK(item_status IN ('pending', 'answered', 'removed')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(session_id, question_id),
  UNIQUE(session_id, question_order)
);
CREATE INDEX ix_session_item_status ON practice_session_item(session_id, item_status, question_order);

-- 一次作答的不可变题目快照及判定；未完成轮次已判定作答仍计入正确率和错题。
-- 同轮同题重复提交返回首次结果且不重复计数；服务端须处理并发和权限。
CREATE TABLE practice_answer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  question_id INTEGER NOT NULL,
  question_type_snapshot TEXT NOT NULL CHECK(question_type_snapshot IN ('single', 'multiple', 'judgment')),
  prompt_snapshot TEXT NOT NULL,
  explanation_snapshot TEXT,
  is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
  answered_at TEXT NOT NULL,
  UNIQUE(session_id, question_id)
);
CREATE INDEX ix_answer_question ON practice_answer(question_id, answered_at);

CREATE TABLE practice_answer_option (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  practice_answer_id INTEGER NOT NULL,
  option_order INTEGER NOT NULL CHECK(option_order > 0),
  content_snapshot TEXT NOT NULL,
  is_correct_snapshot INTEGER NOT NULL CHECK(is_correct_snapshot IN (0, 1)),
  is_selected INTEGER NOT NULL CHECK(is_selected IN (0, 1)),
  UNIQUE(practice_answer_id, option_order)
);

CREATE TABLE mistake_record (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  question_id INTEGER NOT NULL,
  last_wrong_answer_id INTEGER NOT NULL,
  error_count INTEGER NOT NULL CHECK(error_count > 0),
  consecutive_correct INTEGER NOT NULL DEFAULT 0 CHECK(consecutive_correct BETWEEN 0 AND 3),
  last_wrong_at TEXT NOT NULL,
  removed_at TEXT,
  UNIQUE(student_id, question_id)
);
CREATE INDEX ix_mistake_review ON mistake_record(student_id, removed_at, consecutive_correct, last_wrong_at);

CREATE TABLE student_subject_preference (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  subject_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(student_id, subject_id)
);
