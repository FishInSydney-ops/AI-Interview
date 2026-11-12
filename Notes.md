| 学员端 | http://127.0.0.1:5173/ 
| 管理端 | http://127.0.0.1:5174/admin/ 
| API 文档 | http://127.0.0.1:8000/api/docs 

重启电脑后，启动后台前端：
cd "/Users/frozenfiah/Desktop/ACER/Agent_Learning/ClaudeCode 2026-10-28/云枢智学"

| 终端 | 启动命令 | 启动后访问 |
| 终端 1：学员端 | `make portal` | http://127.0.0.1:5173/
| 终端 2：管理端 | `make admin` | http://127.0.0.1:5174/admin/
| 终端 3：后端 | `make api` | http://127.0.0.1:8000/api/docs

成功启动：
Local: http://127.0.0.1:5174/admin/

创建管理员: make init-admin

管理员登陆：admin，12345678；

临时密码：显示1次，24h有效期；

