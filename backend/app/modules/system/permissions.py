"""Stable permission catalogue; no endpoints for deferred modules are implied."""

GROUPS = [
    ("dashboard", "数据看板", [("view", "查看")]),
    (
        "subject",
        "学科管理",
        [("view", "查看"), ("create", "新增"), ("edit", "编辑"), ("delete", "删除")],
    ),
    (
        "course",
        "课程库",
        [("view", "查看"), ("create", "新增"), ("edit", "编辑"), ("delete", "删除")],
    ),
    (
        "question",
        "题库管理",
        [
            (x, y)
            for x, y in [
                ("view", "查看"),
                ("create", "新增"),
                ("edit", "编辑"),
                ("delete", "删除"),
                ("import", "导入"),
                ("export", "导出"),
                ("review", "审核"),
            ]
        ],
    ),
    (
        "kb",
        "面试题库",
        [
            ("view", "查看"),
            ("upload", "上传"),
            ("edit", "编辑"),
            ("delete", "删除"),
            ("search", "检索"),
        ],
    ),
    (
        "route",
        "学习路线",
        [("view", "查看"), ("create", "新增"), ("edit", "编辑"), ("delete", "删除")],
    ),
    ("student", "学员管理", [("view", "查看"), ("edit", "编辑"), ("delete", "删除")]),
    (
        "user",
        "用户管理",
        [
            ("view", "查看"),
            ("create", "新增"),
            ("edit", "编辑"),
            ("disable", "启用/禁用"),
            ("delete", "删除"),
            ("reset", "重置密码"),
        ],
    ),
    (
        "system",
        "系统管理",
        [
            ("roles", "角色授权（仅超级管理员）"),
            ("logs", "日志查看"),
            ("export", "日志导出"),
            ("settings", "系统设置"),
        ],
    ),
]
ALL_PERMISSIONS = {f"{key}:{action}" for key, _, items in GROUPS for action, _ in items}
REVIEWER = {p for p in ALL_PERMISSIONS if p.endswith(":view")} - {"user:view"}
REVIEWER.add("question:review")
OPERATOR = {p for p in ALL_PERMISSIONS if not p.startswith(("user:", "system:"))} - {
    "question:review"
}
DEFAULT_ROLES = [
    ("super_admin", "超级管理员", "内置唯一超级管理员", ALL_PERMISSIONS),
    ("content_reviewer", "内容审核", "查看内容与审核题目", REVIEWER),
    ("operator", "运营人员", "内容维护与学员管理，不含审核和系统管理", OPERATOR),
]


def catalogue():
    return [
        {
            "key": key,
            "name": name,
            "items": [{"key": f"{key}:{action}", "label": label} for action, label in items],
        }
        for key, name, items in GROUPS
    ]
