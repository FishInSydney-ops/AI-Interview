export interface NavigationItem {
  path: string
  title: string
  icon: string
}

export const navigationGroups: { title: string; items: NavigationItem[] }[] = [
  { title: '概览', items: [{ path: '/', title: '数据看板', icon: 'dashboard' }] },
  {
    title: '内容管理',
    items: [
      { path: '/subjects', title: '学科管理', icon: 'subjects' },
      { path: '/courses', title: 'B站课程库', icon: 'video' },
      { path: '/questions', title: '题库管理', icon: 'books' },
      { path: '/question-bank', title: '面试题库管理', icon: 'archive' },
      { path: '/routes', title: '学习路线', icon: 'route' },
    ],
  },
  { title: '学员管理', items: [{ path: '/students', title: '学员管理', icon: 'student' }] },
  {
    title: '系统管理',
    items: [
      { path: '/users', title: '用户管理', icon: 'users' },
      { path: '/roles', title: '角色管理', icon: 'shield' },
      { path: '/logs', title: '操作日志', icon: 'document' },
      { path: '/settings', title: '系统设置', icon: 'settings' },
    ],
  },
]
