/**
 * 云枢智学 公共JavaScript
 */

// ============================
// 工具函数
// ============================

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 类型: success, warning, error, info
 * @param {number} duration - 持续时间(毫秒)
 */
function showToast(message, type = 'info', duration = 3000) {
  const existingToast = document.querySelector('.toast');
  if (existingToast) {
    existingToast.remove();
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 9999;
    animation: slideInRight 0.3s ease;
    border-left: 4px solid ${getTypeColor(type)};
  `;
  toast.innerHTML = `
    <span style="font-size:18px;">${getToastIcon(type)}</span>
    <span style="font-size:14px;">${message}</span>
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function getToastIcon(type) {
  const icons = { success: '✓', warning: '⚠', error: '✕', info: 'ℹ' };
  return icons[type] || icons.info;
}

function getTypeColor(type) {
  const colors = { success: '#67c23a', warning: '#e6a23c', error: '#f56c6c', info: '#409eff' };
  return colors[type] || colors.info;
}

/**
 * 显示确认对话框
 */
function showConfirm(message, onConfirm, onCancel) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay active';
  overlay.innerHTML = `
    <div class="modal" style="max-width: 400px;">
      <div class="modal-header">
        <h3 class="modal-title">确认操作</h3>
        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
      </div>
      <div class="modal-body">
        <p style="font-size: 15px; color: #606266;">${message}</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">取消</button>
        <button class="btn btn-primary confirm-btn">确定</button>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);

  overlay.querySelector('.confirm-btn').addEventListener('click', () => {
    overlay.remove();
    onConfirm && onConfirm();
  });

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.remove();
      onCancel && onCancel();
    }
  });
}

/**
 * 显示表单模态框
 */
function showModal(title, bodyHtml, footerHtml) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay active';
  overlay.innerHTML = `
    <div class="modal" style="max-width: 600px;">
      <div class="modal-header">
        <h3 class="modal-title">${title}</h3>
        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
      </div>
      <div class="modal-body">${bodyHtml}</div>
      ${footerHtml ? `<div class="modal-footer">${footerHtml}</div>` : ''}
    </div>
  `;
  document.body.appendChild(overlay);
  return overlay;
}

/**
 * 加载状态
 */
function showLoading(show = true) {
  let loading = document.querySelector('.global-loading');
  if (show) {
    if (!loading) {
      loading = document.createElement('div');
      loading.className = 'global-loading';
      loading.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255,255,255,0.8);
        display: flex; align-items: center; justify-content: center;
        z-index: 10000;
      `;
      loading.innerHTML = `<div style="width:40px;height:40px;border:3px solid #f3f3f3;border-top:3px solid #409eff;border-radius:50%;animation: spin 1s linear infinite;"></div>`;
      document.body.appendChild(loading);
    }
  } else {
    loading && loading.remove();
  }
}

/**
 * 格式化日期
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (typeof date === 'string') date = new Date(date);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return format.replace('YYYY', year).replace('MM', month).replace('DD', day)
    .replace('HH', hours).replace('mm', minutes).replace('ss', seconds);
}

function getDifficultyLabel(d) {
  return { easy: '简单', medium: '中等', hard: '困难' }[d] || d;
}

function getDifficultyClass(d) {
  return { easy: 'difficulty-easy', medium: 'difficulty-medium', hard: 'difficulty-hard' }[d] || '';
}

function getTypeLabel(t) {
  return { single: '单选', multiple: '多选', judge: '判断', short: '简答' }[t] || t;
}

function debounce(fn, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

/**
 * 根据课程ID数组获取课程详情
 */
function getCoursesByIds(courseIds) {
  if (!courseIds || !MockData.courses) return [];
  return courseIds.map(function(id) {
    for (var i = 0; i < MockData.courses.length; i++) {
      if (MockData.courses[i].id === id) return MockData.courses[i];
    }
    return null;
  }).filter(Boolean);
}

/**
 * 根据学科ID获取学科详情
 */
function getSubjectById(id) {
  if (!id || !MockData.subjects) return null;
  for (var i = 0; i < MockData.subjects.length; i++) {
    if (MockData.subjects[i].id === id) return MockData.subjects[i];
  }
  return null;
}

/**
 * 根据学科ID获取对应路线
 */
function getRouteBySubjectId(subjectId) {
  if (!subjectId || !MockData.routes) return null;
  for (var i = 0; i < MockData.routes.length; i++) {
    if (MockData.routes[i].subjectId === subjectId) return MockData.routes[i];
  }
  return null;
}

/**
 * 获取所有分类的扁平列表（从各学科的 catalogs 中聚合）
 * 返回 [{ id, name, count, icon, subjectId, subjectName }, ...]
 */
function getAllCatalogs() {
  var all = [];
  var sortedSubjects = MockData.subjects.slice().sort(function(a, b) { return (a.sort || 0) - (b.sort || 0); });
  sortedSubjects.forEach(function(s) {
    var sortedCatalogs = (s.catalogs || []).slice().sort(function(a, b) { return (a.sort || 0) - (b.sort || 0); });
    sortedCatalogs.forEach(function(c) {
      all.push({
        id: c.id,
        name: c.name,
        count: c.count,
        icon: c.icon,
        sort: c.sort || 0,
        subjectId: s.id,
        subjectName: s.name
      });
    });
  });
  return all;
}

/**
 * 根据 catalogId 查找所属的分类和学科
 * 返回 { catalog: {...}, subject: {...} } 或 null
 */
function findCatalogById(catalogId) {
  if (!catalogId) return null;
  for (var i = 0; i < MockData.subjects.length; i++) {
    var s = MockData.subjects[i];
    var catalogs = s.catalogs || [];
    for (var j = 0; j < catalogs.length; j++) {
      if (catalogs[j].id === catalogId) {
        return { catalog: catalogs[j], subject: s };
      }
    }
  }
  return null;
}

/**
 * 根据学科ID获取其下的分类列表
 * 返回 [{ id, name, count, icon }, ...]
 */
function getCatalogsBySubjectId(subjectId) {
  var subject = getSubjectById(subjectId);
  if (!subject) return [];
  return (subject.catalogs || []).slice().sort(function(a, b) { return (a.sort || 0) - (b.sort || 0); });
}

/**
 * 格式化播放量（万级）
 */
function formatPlayCount(count) {
  if (!count) return '0';
  if (count >= 10000) return (count / 10000).toFixed(1) + '万';
  return count.toString();
}

/**
 * 格式化时长（分钟→小时+分钟）
 */
function formatDuration(durationStr) {
  if (!durationStr) return '';
  var parts = durationStr.split(':');
  if (parts.length === 2) return parts[0] + 'h' + parts[1] + 'min';
  if (parts.length === 3) return parts[0] + 'h' + parts[1] + 'min';
  return durationStr;
}

// ============================
// 模拟数据
// ============================

const MockData = {
  userInfo: {
    id: 'u001',
    username: '黑马学员',
    avatar: '',
    phone: '138****8888',
    email: 'student@itheima.com',
    role: 'admin',
    joinDate: '2026-06-01',
    studyDays: 54,
    dailyGoal: 20
  },

  // 注意：catalogs 已移入 subjects 各项的 catalogs 字段中（一对多关系）
  // 通过 getAllCatalogs() 获取扁平分类列表，findCatalogById(id) 查找分类

  questions: [
    { id: 1, subject: '在Java中，ArrayList和LinkedList的区别是什么？', type: 'single', difficulty: 'medium', catalogId: 'c001', catalogName: 'AI应用基础', tags: ['集合框架', '数据结构'], options: [{ id: 'a', content: 'ArrayList基于数组，LinkedList基于链表', correct: true }, { id: 'b', content: 'ArrayList和LinkedList完全相同', correct: false }, { id: 'c', content: 'LinkedList查询更快', correct: false }, { id: 'd', content: 'ArrayList插入更快', correct: false }], analysis: 'ArrayList底层是数组，查询快，增删慢；LinkedList底层是双向链表，增删快，查询慢。', status: 'published' },
    { id: 2, subject: '以下哪些是JavaScript的基本数据类型？', type: 'multiple', difficulty: 'easy', catalogId: 'c003', catalogName: 'AI视觉基础', tags: ['JavaScript', '基础'], options: [{ id: 'a', content: 'String', correct: true }, { id: 'b', content: 'Number', correct: true }, { id: 'c', content: 'Array', correct: false }, { id: 'd', content: 'Boolean', correct: true }], analysis: 'JS基本数据类型：String、Number、Boolean、null、undefined、Symbol、BigInt。Array是引用类型。', status: 'published' },
    { id: 3, subject: 'MySQL中，以下哪个命令用于创建数据库？', type: 'single', difficulty: 'easy', catalogId: 'c004', catalogName: '数据库', tags: ['MySQL', 'SQL'], options: [{ id: 'a', content: 'CREATE DATABASE', correct: true }, { id: 'b', content: 'NEW DATABASE', correct: false }, { id: 'c', content: 'ADD DATABASE', correct: false }, { id: 'd', content: 'INSERT DATABASE', correct: false }], analysis: 'MySQL中使用CREATE DATABASE语句来创建数据库。', status: 'published' },
    { id: 4, subject: 'Redis的持久化方式有哪些？', type: 'multiple', difficulty: 'medium', catalogId: 'c007', catalogName: 'Redis缓存', tags: ['Redis', '持久化'], options: [{ id: 'a', content: 'RDB快照', correct: true }, { id: 'b', content: 'AOF日志', correct: true }, { id: 'c', content: 'WAL预写日志', correct: false }, { id: 'd', content: 'Binlog', correct: false }], analysis: 'Redis有RDB和AOF两种持久化方式。RDB是快照方式，AOF是日志追加方式。', status: 'published' },
    { id: 5, subject: 'Spring中IoC和DI的区别与联系是什么？', type: 'short', difficulty: 'medium', catalogId: 'c006', catalogName: 'Spring生态', tags: ['Spring', 'IoC'], options: [], analysis: 'IoC（控制反转）是一种设计思想，DI（依赖注入）是IoC的具体实现方式。Spring通过DI实现IoC。', status: 'pending' },
    { id: 6, subject: 'Redis是单线程模型，所以不需要考虑线程安全问题。', type: 'judge', difficulty: 'easy', catalogId: 'c007', catalogName: 'Redis缓存', tags: ['Redis', '线程'], options: [{ id: 'a', content: '正确', correct: false }, { id: 'b', content: '错误', correct: true }], analysis: 'Redis核心命令执行是单线程，但从6.0引入了多线程IO。', status: 'published' },
    { id: 7, subject: '什么是CAP理论？在分布式系统中如何权衡？', type: 'short', difficulty: 'hard', catalogId: 'c008', catalogName: '微服务', tags: ['分布式', 'CAP'], options: [], analysis: 'CAP理论指一致性(C)、可用性(A)、分区容错性(P)三者最多满足两个。分布式系统通常优先保证P，然后在C和A之间权衡。', status: 'published' },
    { id: 8, subject: 'MySQL中什么情况下索引会失效？', type: 'multiple', difficulty: 'medium', catalogId: 'c004', catalogName: '数据库', tags: ['MySQL', '索引'], options: [{ id: 'a', content: '使用LIKE左模糊匹配', correct: true }, { id: 'b', content: '对索引列使用函数', correct: true }, { id: 'c', content: '使用OR连接非索引列', correct: true }, { id: 'd', content: '使用WHERE id = 1', correct: false }], analysis: '索引失效常见情况：左模糊、使用函数、OR条件、类型隐式转换等。', status: 'published' },
    { id: 9, subject: 'HashMap的底层数据结构是什么？', type: 'single', difficulty: 'medium', catalogId: 'c001', catalogName: 'AI应用基础', tags: ['集合框架', 'HashMap'], options: [{ id: 'a', content: '数组+链表+红黑树', correct: true }, { id: 'b', content: '只有数组', correct: false }, { id: 'c', content: '双向链表', correct: false }, { id: 'd', content: '跳表', correct: false }], analysis: 'HashMap底层是数组+链表+红黑树。当链表长度>=8且数组长度>=64时，链表转为红黑树。', status: 'published' },
    { id: 10, subject: 'TCP三次握手的过程是什么？', type: 'short', difficulty: 'medium', catalogId: 'c010', catalogName: 'AI视觉基础', tags: ['网络', 'TCP'], options: [], analysis: '三次握手：SYN→SYN+ACK→ACK。确保双方收发能力正常。', status: 'pending' },
    { id: 11, subject: 'Python中列表和元组的区别？', type: 'single', difficulty: 'easy', catalogId: 'c009', catalogName: 'Python基础', tags: ['Python', '基础'], options: [{ id: 'a', content: '列表可变，元组不可变', correct: true }, { id: 'b', content: '列表不可变，元组可变', correct: false }, { id: 'c', content: '两者没有区别', correct: false }, { id: 'd', content: '列表用()定义', correct: false }], analysis: '列表(list)用[]定义，可变；元组(tuple)用()定义，不可变。', status: 'published' },
    { id: 12, subject: '什么是事务的ACID特性？', type: 'multiple', difficulty: 'medium', catalogId: 'c004', catalogName: '数据库', tags: ['事务', 'ACID'], options: [{ id: 'a', content: '原子性(Atomicity)', correct: true }, { id: 'b', content: '一致性(Consistency)', correct: true }, { id: 'c', content: '隔离性(Isolation)', correct: true }, { id: 'd', content: '持久性(Durability)', correct: true }], analysis: 'ACID指原子性、一致性、隔离性、持久性，是事务的四大特性。', status: 'published' }
  ],

  // 错题本数据
  wrongQuestions: [
    { id: 'w001', questionId: 'q002', subject: '以下哪些是JavaScript的基本数据类型？', catalogName: 'AI视觉基础', wrongCount: 2, lastWrongTime: '2026-07-22', yourAnswer: '选漏了Symbol', correctAnswer: 'String, Number, Boolean, null, undefined, Symbol, BigInt', status: 'pending' },
    { id: 'w002', questionId: 'q004', subject: 'Redis的持久化方式有哪些？', catalogName: 'Redis缓存', wrongCount: 1, lastWrongTime: '2026-07-21', yourAnswer: '只知道RDB', correctAnswer: 'RDB快照和AOF日志', status: 'pending' },
    { id: 'w003', questionId: 'q008', subject: 'MySQL中什么情况下索引会失效？', catalogName: '数据库', wrongCount: 3, lastWrongTime: '2026-07-20', yourAnswer: '左模糊匹配', correctAnswer: '左模糊、使用函数、OR条件、类型隐式转换', status: 'pending' },
    { id: 'w004', questionId: 'q006', subject: 'Redis是单线程模型，所以不需要考虑线程安全问题。', catalogName: 'Redis缓存', wrongCount: 1, lastWrongTime: '2026-07-18', yourAnswer: '正确', correctAnswer: '错误，Redis 6.0引入了多线程IO', status: 'mastered' },
    { id: 'w005', questionId: 'q007', subject: '什么是CAP理论？在分布式系统中如何权衡？', catalogName: '微服务', wrongCount: 1, lastWrongTime: '2026-07-15', yourAnswer: '理解不全面', correctAnswer: 'C一致性、A可用性、P分区容错性，最多满足两个', status: 'mastered' },
    { id: 'w006', questionId: 'q001', subject: '在Java中，ArrayList和LinkedList的区别是什么？', catalogName: 'AI应用基础', wrongCount: 2, lastWrongTime: '2026-07-23', yourAnswer: 'B. ArrayList和LinkedList在性能上完全相同', correctAnswer: 'A. ArrayList基于数组，LinkedList基于链表', status: 'pending' }
  ],

  wrongStats: { total: 47, pending: 12, mastered: 35, masteryRate: 89 },

  // ===== 学科定义（含子分类 catalogs） =====
  subjects: [
    { id: 'subj001', name: 'AI应用与智能体开发', icon: '🤖', description: 'AI应用开发、RAG检索增强、Agent智能体、MCP协议、后端工程', color: '#667eea', sort: 1, routeCount: 1, courseCount: 18,
      catalogs: [
        { id: 'c001', name: 'AI应用基础', count: 256, icon: '🤖', sort: 1 },
        { id: 'c006', name: 'Spring生态', count: 145, icon: '🍃', sort: 2 },
        { id: 'c004', name: '数据库', count: 178, icon: '🗄️', sort: 3 },
        { id: 'c007', name: 'Redis缓存', count: 98, icon: '📦', sort: 4 },
        { id: 'c008', name: '微服务', count: 87, icon: '🔧', sort: 5 }
      ]
    },
    { id: 'subj006', name: 'AI大模型开发', icon: '🧠', description: '大模型微调与部署、机器学习、深度学习、NLP/CV', color: '#ff758c', sort: 2, routeCount: 1, courseCount: 12,
      catalogs: [
        { id: 'c009', name: 'Python基础', count: 189, icon: '🐍', sort: 1 }
      ]
    },
    { id: 'subj010', name: 'AI具身智能机器人开发', icon: '🦾', description: '具身智能、机器人控制、传感器融合、仿真环境', color: '#fa709a', sort: 3, routeCount: 1, courseCount: 0, catalogs: [] },
    { id: 'subj009', name: 'AI嵌入式_机器人开发', icon: '🔩', description: '嵌入式Linux、ROS机器人、边缘AI部署、ARM架构', color: '#43e97b', sort: 4, routeCount: 1, courseCount: 4, catalogs: [] },
    { id: 'subj007', name: 'AI测试', icon: '🧪', description: 'AI驱动测试、自动化测试、性能与安全测试、智能断言', color: '#20c997', sort: 5, routeCount: 1, courseCount: 4, catalogs: [] },
    { id: 'subj008', name: 'AI运维', icon: '🔧', description: '云原生、容器化、CI/CD、AIops智能运维、监控告警', color: '#4facfe', sort: 6, routeCount: 1, courseCount: 5, catalogs: [] },
    { id: 'subj011', name: 'AI视觉设计', icon: '🎨', description: 'AI辅助UI设计、AIGC视觉创作、前端工程化', color: '#a18cd1', sort: 7, routeCount: 1, courseCount: 0,
      catalogs: [
        { id: 'c010', name: 'AI视觉基础', count: 312, icon: '🎨', sort: 1 }
      ]
    },
    { id: 'subj012', name: 'AI视频与短剧创作', icon: '🎬', description: 'AI视频生成、短剧制作、AIGC内容创作、数字人', color: '#f093fb', sort: 8, routeCount: 1, courseCount: 0, catalogs: [] }
  ],

  // ===== B站课程库（独立实体，BV号为唯一标识） =====
  courses: [
    { id: 'crs001', bvid: 'BV17F411T7Ao', title: 'Java零基础视频教程_上部', duration: '4511:45', durationMin: 4512, playCount: 46588162, pic: 'http://i0.hdslb.com/bfs/archive/e324834c33ca9e9ce64bab15e743c16a19765435.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs002', bvid: 'BV1yW4y1Y7Ms', title: 'Java零基础视频教程_下部', duration: '2306:08', durationMin: 2306, playCount: 27032356, pic: 'http://i1.hdslb.com/bfs/archive/3ea248b484f595fcf33c7a96b7b9ad753c7b745d.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs003', bvid: 'BV1Cv411372m', title: 'Java入门基础视频教程', duration: '4752:44', durationMin: 4753, playCount: 9961094, pic: 'http://i2.hdslb.com/bfs/archive/2ddbac3475dd3c18fb3983c9809ffd60a67ee308.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs004', bvid: 'BV1TJxCzSEEZ', title: '2026版AI+Java零基础全套视频课程', duration: '2267:13', durationMin: 2267, playCount: 6198129, pic: 'http://i1.hdslb.com/bfs/archive/b8dc39786920f22f1ff0d297737d5added5a7096.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs005', bvid: 'BV1Kr4y1i7ru', title: 'MySQL数据库入门到精通', duration: '1800:52', durationMin: 1801, playCount: 13045697, pic: 'http://i1.hdslb.com/bfs/archive/7e15bb1dc75f9933f9cbe4feac9a0bfbd570e5c0.jpg', subjectIds: ['subj001', 'subj006'], source: 'bilibili' },
    { id: 'crs006', bvid: 'BV1yGydYEE3H', title: 'AI+JavaWeb开发入门项目实战', duration: '4558:10', durationMin: 4558, playCount: 11479834, pic: 'http://i2.hdslb.com/bfs/archive/77c6db508db03f7273263a8767a1a0e160f0a165.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs007', bvid: 'BV1m84y1w7Tb', title: 'JavaWeb开发教程(Spring+MyBatis+SpringMVC+SpringBoot)', duration: '2571:07', durationMin: 2571, playCount: 8929984, pic: 'http://i2.hdslb.com/bfs/archive/bc28656ba0e7f62925b8bedcfca006c1b7ad7100.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs008', bvid: 'BV1Qf4y1T7Hx', title: 'JavaWeb基础教程企业实战完整版', duration: '2049:00', durationMin: 2049, playCount: 6058523, pic: 'http://i2.hdslb.com/bfs/archive/c6e4ea1ec234f702ae96a3de64ba394dd4f9f0cf.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs009', bvid: 'BV1Fi4y1S7ix', title: 'SSM框架教程(Spring+SpringMVC+MyBatisPlus)', duration: '1255:11', durationMin: 1255, playCount: 5212031, pic: 'http://i1.hdslb.com/bfs/archive/ab4f1df1bb4e85163321fb76333ad9dcaaa947eb.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs010', bvid: 'BV1WZ4y1P7Bp', title: 'SSM框架教程(Spring+SpringMVC+MyBatis)', duration: '1399:22', durationMin: 1399, playCount: 2386482, pic: 'http://i2.hdslb.com/bfs/archive/64487f39b4e1bb270ec71fa76efc578008f685fa.png', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs011', bvid: 'BV15b4y1a7yG', title: 'SpringBoot2全套视频教程', duration: '2068:42', durationMin: 2069, playCount: 2907212, pic: 'http://i0.hdslb.com/bfs/archive/95916a50852f5243ba6f4c06428feb26b60a6ce9.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs012', bvid: 'BV14z4y1N7pg', title: 'SpringBoot3+Vue3全套视频教程', duration: '1452:00', durationMin: 1452, playCount: 2642429, pic: 'http://i1.hdslb.com/bfs/archive/bcbb95b2d1b7e4ec14834bc09358342fa4a2bb61.jpg', subjectIds: ['subj001', 'subj011'], source: 'bilibili' },
    { id: 'crs013', bvid: 'BV1LQ4y127n4', title: 'SpringCloud微服务技术栈课程', duration: '2680:19', durationMin: 2680, playCount: 4532283, pic: 'http://i2.hdslb.com/bfs/archive/b1a5e3092c0295e7c9c88099b9def2f5e2327bda.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs014', bvid: 'BV1S142197x7', title: 'SpringCloud微服务开发与实战', duration: '2451:51', durationMin: 2452, playCount: 2664762, pic: 'http://i0.hdslb.com/bfs/archive/f86cb7ca4f3161a08ee6fa38ef1ebdad34820e58.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs015', bvid: 'BV1TP411v7v6', title: '苍穹外卖(SpringBoot+SSM企业级项目)', duration: '2270:35', durationMin: 2271, playCount: 6652392, pic: 'http://i0.hdslb.com/bfs/archive/4a6c7c24e3a3403d4403867f0ce41e5c48342dd3.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs016', bvid: 'BV13a411q753', title: '瑞吉外卖(SpringBoot+MyBatisPlus)', duration: '1938:48', durationMin: 1939, playCount: 4114854, pic: 'http://i0.hdslb.com/bfs/archive/66e8947b3c48d6710c93d572ebc91f27bf4db9fc.png', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs017', bvid: 'BV1gb42177hm', title: 'Java+AI智能辅助编程全套视频教程', duration: '3556:42', durationMin: 3557, playCount: 3508715, pic: 'http://i0.hdslb.com/bfs/archive/b6480114f42a1fef29f74405df65003733af762e.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    // 前端
    { id: 'crs018', bvid: 'BV1kM4y127Li', title: '前端Web开发HTML5+CSS3+移动web视频教程', duration: '2687:00', durationMin: 2687, playCount: 4300461, pic: 'http://i0.hdslb.com/bfs/archive/84705cdc024a6c7ba5fdc86977e2e27e49a5685a.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs019', bvid: 'BV1Kg411T7t9', title: '前端开发入门教程(html5+css3+项目)', duration: '1639:49', durationMin: 1640, playCount: 4277687, pic: 'http://i2.hdslb.com/bfs/archive/bc53f6bab261c8d3e0742286e0f7314c5206ede2.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs020', bvid: 'BV1Y84y1L7Nn', title: '前端JavaScript入门到精通全套视频教程', duration: '3610:24', durationMin: 3610, playCount: 7643764, pic: 'http://i2.hdslb.com/bfs/archive/7cbcf700e3950f40dab97b5e57c8581733fdad22.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs021', bvid: 'BV1ux411d75J', title: 'JavaScript全套教程(Web前端必学)', duration: '995:46', durationMin: 996, playCount: 3093539, pic: 'http://i0.hdslb.com/bfs/archive/2c6b47d111f503cbf27a04b92e29bae3017ba070.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs022', bvid: 'BV1HV4y1a7n4', title: 'Vue2+Vue3基础入门到实战项目全套教程', duration: '3091:32', durationMin: 3092, playCount: 3508291, pic: 'http://i2.hdslb.com/bfs/archive/c0247f29a115368ed1d236126a8b0cae0dd1396e.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs023', bvid: 'BV1zq4y1p7ga', title: 'Vue全套视频教程(vue2到vue3全覆盖)', duration: '3597:47', durationMin: 3598, playCount: 3028501, pic: 'http://i1.hdslb.com/bfs/archive/2e20f95da4cbc6d4ec84ce24e01499973c7ebbd4.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs024', bvid: 'BV1a34y167AZ', title: 'Node.js全套入门教程(含es6+express+webpack)', duration: '1354:40', durationMin: 1355, playCount: 2956521, pic: 'http://i2.hdslb.com/bfs/archive/a35e28d321c55c783526b2382431409935ddfb9f.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs025', bvid: 'BV1834y1676P', title: '微信小程序开发教程(含uni-app多端部署)', duration: '1776:44', durationMin: 1777, playCount: 6430425, pic: 'http://i1.hdslb.com/bfs/archive/47e6fca8a041a09fb6782d845e7588e56e4f922c.png', subjectIds: ['subj011'], source: 'bilibili' },
    { id: 'crs026', bvid: 'BV1nE41117BQ', title: '微信小程序开发前端教程', duration: '1131:10', durationMin: 1131, playCount: 3232616, pic: 'http://i0.hdslb.com/bfs/archive/5bfe3753cf7113e9121f4adc37e8ca996b763443.jpg', subjectIds: ['subj011'], source: 'bilibili' },
    // Python
    { id: 'crs027', bvid: 'BV1qW4y1a7fU', title: 'Python零基础全套教程(8天从入门到精通)', duration: '1900:20', durationMin: 1900, playCount: 24880310, pic: 'http://i1.hdslb.com/bfs/archive/0c95a6ac5ae81dbc7425bb0c01604dbe3a99568d.jpg', subjectIds: ['subj006'], source: 'bilibili' },
    { id: 'crs028', bvid: 'BV1ex411x7Em', title: 'Python教程_600集从入门到精通', duration: '3303:06', durationMin: 3303, playCount: 20799266, pic: 'http://i1.hdslb.com/bfs/archive/b1a018567ac680559b0fdb54ff8767f42bf0fba4.png', subjectIds: ['subj006'], source: 'bilibili' },
    { id: 'crs029', bvid: 'BV1sHU9BmEne', title: 'Python+AI零基础入门到大神全套视频课程', duration: '3098:30', durationMin: 3099, playCount: 8416669, pic: 'http://i0.hdslb.com/bfs/archive/f4a70133df54a0a41a9c3b482904ac26f2e3a56e.jpg', subjectIds: ['subj006', 'subj001'], source: 'bilibili' },
    // C/C++
    { id: 'crs030', bvid: 'BV1et411b73Z', title: 'C++教程从0到1入门编程', duration: '3149:32', durationMin: 3150, playCount: 46588162, pic: 'http://i0.hdslb.com/bfs/archive/e324834c33ca9e9ce64bab15e743c16a19765435.jpg', subjectIds: ['subj009'], source: 'bilibili' },
    { id: 'crs031', bvid: 'BV1Xa4y1k7LU', title: 'C语言零基础入门到精通全套视频教程', duration: '1587:32', durationMin: 1588, playCount: 5901067, pic: 'http://i2.hdslb.com/bfs/archive/3499ed831caec14e273ac16ef96bc969b62c5da9.jpg', subjectIds: ['subj009'], source: 'bilibili' },
    // AI
    { id: 'crs032', bvid: 'BV1yjz5BLEoY', title: '大模型RAG与Agent智能体项目实战教程', duration: '931:31', durationMin: 932, playCount: 3057154, pic: 'http://i0.hdslb.com/bfs/archive/ec034de58ed78ca875c6561c7b2a93c212ffbf8a.jpg', subjectIds: ['subj001', 'subj006'], source: 'bilibili' },
    // 测试
    { id: 'crs033', bvid: 'BV1TP4y1J7BD', title: '软件测试视频教程(基础入门到项目实战)', duration: '986:19', durationMin: 986, playCount: 2390458, pic: 'http://i2.hdslb.com/bfs/archive/732dc99f20a523818a0d8e9f88e4e674a874370d.png', subjectIds: ['subj007'], source: 'bilibili' },
    // Linux/运维
    { id: 'crs034', bvid: 'BV1n84y1i7td', title: 'Linux零基础快速入门到精通', duration: '801:43', durationMin: 802, playCount: 7586640, pic: 'http://i2.hdslb.com/bfs/archive/8524e06682ebbe47ec08e922d9743a10f9632378.jpg', subjectIds: ['subj008'], source: 'bilibili' },
    // Java面试
    { id: 'crs035', bvid: 'BV1yT411H7YK', title: '新版Java面试专题视频教程', duration: '1421:42', durationMin: 1422, playCount: 3801671, pic: 'http://i2.hdslb.com/bfs/archive/d56d07291cc9231e9822328d552249733d87d5cb.jpg', subjectIds: ['subj001'], source: 'bilibili' },
    { id: 'crs036', bvid: 'BV16J411h7Rd', title: '深入学习Java并发编程(JUC)', duration: '1958:51', durationMin: 1959, playCount: 2770792, pic: 'http://i0.hdslb.com/bfs/archive/cc9c854fba9e3eb1139ee772d18fbdb9d056eac5.png', subjectIds: ['subj001'], source: 'bilibili' },
  ],

  // ===== 学习路线（只关联课程；courseIds 即学习顺序，引用 course.id，不嵌入课程数据） =====
  routes: [
    {
      id: 'r001', name: 'AI应用与智能体全栈开发', subjectId: 'subj001',
      description: '从零基础到AI应用全栈工程师，涵盖AI应用开发、Spring全家桶、微服务架构、RAG检索增强',
      suitableFor: '🎓 适合大专及以上学历，逻辑思维较强，希望从事AI应用开发、智能体开发的学员。0基础可学，建议学习周期6-8个月。',
      courseIds: ['crs001','crs002','crs003','crs004','crs005','crs006','crs007','crs008','crs009','crs010','crs011','crs012','crs013','crs014','crs015','crs016','crs017']
    },
    {
      id: 'r002', name: 'AI视觉设计工程师', subjectId: 'subj011',
      description: '从入门到精通AI视觉设计，涵盖UI设计、AIGC视觉创作、前端工程化',
      suitableFor: '🎓 适合对UI交互敏感、喜欢视觉创作的学员。0基础可学，建议学习周期5-7个月。',
      courseIds: ['crs018','crs019','crs020','crs021','crs022','crs023','crs024','crs025','crs026']
    },
    {
      id: 'r003', name: 'AI大模型开发工程师', subjectId: 'subj006',
      description: '从Python基础到大模型开发，涵盖机器学习、深度学习、大模型微调与部署',
      suitableFor: '🎓 适合大专及以上学历，入门友好，适合转行学员。0基础可学，建议学习周期5-6个月。',
      courseIds: ['crs027','crs028','crs029']
    },
    {
      id: 'r004', name: 'AI嵌入式_机器人开发工程师', subjectId: 'subj009',
      description: '从C语言基础到嵌入式Linux、ROS机器人开发，涵盖数据结构、ARM架构、边缘AI部署',
      suitableFor: '🎓 适合本科及以上学历，对底层原理和硬件感兴趣，希望从事嵌入式、机器人开发的学员。建议学习周期7-9个月。',
      courseIds: ['crs030','crs031']
    },
    {
      id: 'r005', name: 'AI应用与智能体开发', subjectId: 'subj001',
      description: '基于大模型API构建AI应用，Prompt工程、RAG检索增强、Agent智能体、MCP协议',
      suitableFor: '🎓 适合大专及以上学历，有至少一门编程语言基础，对AI应用开发充满热情的学员。建议学习周期3-5个月。',
      courseIds: ['crs027','crs028','crs032','crs017']
    },
    {
      id: 'r006', name: 'AI大模型算法工程师', subjectId: 'subj006',
      description: '从机器学习基础到大模型训练与微调，涵盖NLP/CV、模型压缩、部署优化',
      suitableFor: '🎓 适合本科及以上学历（计算机/数学/统计相关专业优先），数学基础较好，希望从事AI算法岗的学员。建议学习周期8-12个月。',
      courseIds: ['crs032']
    },
    {
      id: 'r007', name: 'AI测试开发工程师', subjectId: 'subj007',
      description: '融合AI的软件测试全流程，自动化测试、AI驱动测试、性能测试',
      suitableFor: '🎓 适合大专及以上学历，细心耐心，逻辑缜密，希望从传统测试升级到AI测试的学员。建议学习周期4-6个月。',
      courseIds: ['crs033']
    },
    {
      id: 'r008', name: 'AI运维开发工程师', subjectId: 'subj008',
      description: '云原生时代的AI运维体系，Docker/K8s、监控告警、CICD、AIops',
      suitableFor: '🎓 适合大专及以上学历，熟悉Linux命令行，对系统架构和稳定性有追求的学员。建议学习周期5-7个月。',
      courseIds: ['crs034']
    },
    {
      id: 'r009', name: 'AI具身智能机器人开发', subjectId: 'subj010',
      description: 'AI与硬件的深度融合，具身智能、机器人控制、传感器融合、仿真环境',
      suitableFor: '🎓 适合本科及以上学历（电子/自动化/计算机相关专业），有C/C++基础，对硬件和机器人感兴趣的学员。建议学习周期8-10个月。',
      courseIds: ['crs031','crs034']
    }
  ],

  interviews: [
    { id: 'i001', direction: 'AI应用与智能体开发', difficulty: 'medium', questionCount: 10, score: 85, startTime: '2026-07-23 14:30:00', duration: 35, status: 'completed' },
    { id: 'i002', direction: 'AI视觉设计', difficulty: 'easy', questionCount: 8, score: 92, startTime: '2026-07-21 10:15:00', duration: 25, status: 'completed' },
    { id: 'i003', direction: 'AI应用与智能体开发', difficulty: 'hard', questionCount: 12, score: 72, startTime: '2026-07-18 16:00:00', duration: 40, status: 'completed' },
    { id: 'i004', direction: 'AI大模型开发', difficulty: 'medium', questionCount: 10, score: 88, startTime: '2026-07-15 09:30:00', duration: 30, status: 'completed' },
    { id: 'i005', direction: 'AI应用与智能体开发', difficulty: 'medium', questionCount: 5, score: 0, startTime: '2026-07-24 11:00:00', duration: 12, status: 'in_progress' }
  ],

  // 面试题库不再有独立的「知识库 / 知识库文档」实体：
  // 面试题按「方向」（= 学科，见上方 subjects）归属，来源只记文档名文本，不保留原始文档。
  // 方向下拉直接取 subjects 的 name，避免两处维护。

  // 面试题库：对应 kb_question 表。direction 即面试方向（= 学科），是唯一归属维度；
  // docTitle + seq 只作为来源文案留痕，系统不保留原文档、也不支持按文档重新解析。
  // topic 为空字符串表示「未分类」；difficulty：1 简单 / 2 中等 / 3 困难
  kbQuestions: [
    { id: 'q001', direction: 'AI大模型开发', docTitle: '大模型基础与Transformer.md', seq: 1, content: 'Transformer 的自注意力机制是怎么算出注意力权重的？为什么要除以根号 dk？', referenceAnswer: '用 Q 与 K 做点积得到相似度分数，除以根号 dk 做缩放，再经 Softmax 归一化成权重，最后对 V 加权求和。缩放是为了避免维度升高后点积数值过大、Softmax 梯度趋近于 0。', topic: '大模型基础', difficulty: 2, tags: ['Transformer', '自注意力'], sourceMdLine: 42, createdAt: '2026-06-26 10:12', updatedAt: '2026-06-26 10:12' },
    { id: 'q002', direction: 'AI大模型开发', docTitle: '大模型基础与Transformer.md', seq: 2, content: '位置编码解决的是什么问题？没有它会发生什么？', referenceAnswer: '自注意力本身是位置无关的，打乱词序结果不变。位置编码把顺序信息注入输入表示，缺少它模型无法区分「我给你」和「你给我」。', topic: '大模型基础', difficulty: 1, tags: ['位置编码'], sourceMdLine: 78, createdAt: '2026-06-26 10:15', updatedAt: '2026-06-26 10:15' },
    { id: 'q003', direction: 'AI大模型开发', docTitle: '大模型基础与Transformer.md', seq: 3, content: '多头的意义在哪里？把注意力头的数量减到 1 会损失什么？', referenceAnswer: '单个注意力头只能学到一种对齐关系，多头让模型在不同子空间并行关注语法、指代、语义等不同维度，最后拼接再做线性变换融合。减到 1 头表征能力明显下降。', topic: '大模型基础', difficulty: 3, tags: ['Transformer', '多头注意力'], sourceMdLine: 121, createdAt: '2026-06-26 10:20', updatedAt: '2026-06-26 10:20' },
    { id: 'q004', direction: 'AI大模型开发', docTitle: '提示词工程与RAG实战.md', seq: 1, content: '零样本、少样本、思维链提示分别适合什么场景？', referenceAnswer: '零样本适合模型已掌握的任务；少样本适合需要固定输出格式或领域口径的任务；思维链适合需要多步推理的数学、逻辑题，让模型把中间步骤写出来。', topic: 'Prompt工程', difficulty: 1, tags: ['提示词', '少样本'], sourceMdLine: 15, createdAt: '2026-06-28 09:30', updatedAt: '2026-06-28 09:30' },
    { id: 'q005', direction: 'AI大模型开发', docTitle: '提示词工程与RAG实战.md', seq: 2, content: '温度参数（temperature）和 top_p 有什么区别？做结构化抽取时该怎么设置？', referenceAnswer: 'temperature 调整整个概率分布的平滑程度，top_p 只保留累积概率最高的一部分候选词（核采样），二者通常只调一个。结构化抽取要稳定输出，建议 temperature 设 0 到 0.2。', topic: 'Prompt工程', difficulty: 2, tags: ['采样参数'], sourceMdLine: 52, createdAt: '2026-06-28 09:34', updatedAt: '2026-07-05 14:02' },
    { id: 'q006', direction: 'AI大模型开发', docTitle: '提示词工程与RAG实战.md', seq: 3, content: 'RAG 的完整链路包含哪几个阶段？每个阶段最常见的坑是什么？', referenceAnswer: '离线建库（解析、分片、向量化、入库）和在线检索（改写查询、召回、重排、拼装上下文、生成）。常见坑：分片切断了语义、只做向量召回漏掉关键词匹配、召回内容超长导致中间信息被忽略。', topic: 'RAG检索增强', difficulty: 2, tags: ['RAG', '检索链路'], sourceMdLine: 96, createdAt: '2026-06-28 09:40', updatedAt: '2026-06-28 09:40' },
    { id: 'q007', direction: 'AI大模型开发', docTitle: '提示词工程与RAG实战.md', seq: 4, content: '混合检索为什么比单纯向量检索效果好？倒数排名融合（RRF）怎么算？', referenceAnswer: '向量检索擅长语义相近，BM25 擅长专有名词、编号等精确匹配，两者互补。RRF 不比较分数绝对值，只按每路结果的排名取 1/(k+rank) 相加，k 一般取 60，可以把量纲不同的两路分数安全融合。', topic: 'RAG检索增强', difficulty: 3, tags: ['混合检索', 'RRF'], sourceMdLine: 138, createdAt: '2026-06-28 09:45', updatedAt: '2026-06-28 09:45' },
    { id: 'q008', direction: 'AI大模型开发', docTitle: '向量数据库选型.md', seq: 1, content: '文档分片（chunk）大小怎么定？重叠部分有什么用？', referenceAnswer: '没有万能值，中文技术文档常用 300 到 800 字，配合 10% 到 20% 重叠。重叠是为了避免一句话被切断，保证跨边界的语义在至少一个分片里是完整的。', topic: 'RAG检索增强', difficulty: 2, tags: ['分片策略'], sourceMdLine: 23, createdAt: '2026-07-02 11:00', updatedAt: '2026-07-02 11:00' },
    { id: 'q009', direction: 'AI大模型开发', docTitle: '向量数据库选型.md', seq: 2, content: '什么是重排（Rerank）？它在链路里补上了什么？', referenceAnswer: '召回阶段追求快，用双塔向量算相似度，精度有限；重排用交叉编码器把「查询 + 候选文档」一起送进模型打分，精度高但慢，所以只对前几十条候选做。它补上的是排序精度。', topic: 'RAG检索增强', difficulty: 1, tags: ['重排'], sourceMdLine: 67, createdAt: '2026-07-02 11:05', updatedAt: '2026-07-02 11:05' },
    { id: 'q010', direction: 'AI大模型开发', docTitle: '向量数据库选型.md', seq: 3, content: 'HNSW、IVF、PQ 三种索引各有什么取舍？', referenceAnswer: 'HNSW 用多层图换查询速度，召回高、内存占用大；IVF 先聚类再在若干簇内搜，省内存、需要调 nprobe；PQ 把向量分段量化压缩，最省内存但精度损失最大，常与 IVF 组合使用。', topic: '向量数据库', difficulty: 2, tags: ['HNSW', '索引'], sourceMdLine: 104, createdAt: '2026-07-02 11:10', updatedAt: '2026-07-02 11:10' },
    { id: 'q011', direction: 'AI大模型开发', docTitle: '向量数据库选型.md', seq: 4, content: '余弦相似度、内积、欧氏距离三者怎么选？归一化之后有区别吗？', referenceAnswer: '文本向量一般先做 L2 归一化，此时余弦相似度与内积等价，排序结果一致；欧氏距离在归一化后也与前两者单调对应。选哪个主要看数据库和索引的实现支持。', topic: '向量数据库', difficulty: 3, tags: ['相似度度量'], sourceMdLine: 149, createdAt: '2026-07-02 11:15', updatedAt: '2026-07-02 11:15' },
    { id: 'q012', direction: 'AI应用与智能体开发', docTitle: 'LangChain与Agent开发.md', seq: 1, content: 'LangChain 里的 Chain 和 Agent 有什么本质区别？', referenceAnswer: 'Chain 的调用路径在编码时就固定了，是确定性的流水线；Agent 把「下一步调什么工具」交给模型决策，路径是运行时产生的，更灵活但更难控。', topic: 'LangChain与Agent', difficulty: 1, tags: ['LangChain'], sourceMdLine: 18, createdAt: '2026-06-24 15:20', updatedAt: '2026-06-24 15:20' },
    { id: 'q013', direction: 'AI应用与智能体开发', docTitle: 'LangChain与Agent开发.md', seq: 2, content: 'Function Calling 和 ReAct 提示的区别是什么？工程上更推荐哪个？', referenceAnswer: 'ReAct 靠提示词让模型输出「思考 + 动作」文本，再由代码解析，格式易漂移；Function Calling 由模型原生输出结构化的工具调用参数，解析可靠。工程上优先用原生 Function Calling。', topic: 'LangChain与Agent', difficulty: 2, tags: ['Function Calling', 'ReAct'], sourceMdLine: 63, createdAt: '2026-06-24 15:26', updatedAt: '2026-06-24 15:26' },
    { id: 'q014', direction: 'AI应用与智能体开发', docTitle: 'LangChain与Agent开发.md', seq: 3, content: 'Agent 调用工具时陷入死循环，你会从哪些地方排查？', referenceAnswer: '限制最大迭代轮次；检查工具返回是否把错误吞掉导致模型看不到失败；在提示词里给出终止条件；对重复的相同调用做去重拦截；观察是不是工具描述太模糊让模型反复试探。', topic: 'LangChain与Agent', difficulty: 3, tags: ['Agent', '稳定性'], sourceMdLine: 112, createdAt: '2026-06-24 15:31', updatedAt: '2026-07-08 10:40' },
    { id: 'q015', direction: 'AI大模型开发', docTitle: '大模型基础与Transformer.md', seq: 4, content: 'LoRA 微调为什么能省显存？rank 一般怎么取？', referenceAnswer: 'LoRA 冻结原始权重，只在旁路插入低秩矩阵 A、B 参与训练，可训练参数量大幅下降，优化器状态和梯度显存随之降低。rank 常用 8 到 64，任务越复杂、与预训练分布差得越远，就取越大。', topic: '模型微调', difficulty: 3, tags: ['LoRA', 'PEFT'], sourceMdLine: 176, createdAt: '2026-06-26 10:35', updatedAt: '2026-06-26 10:35' },
    { id: 'q016', direction: 'AI大模型开发', docTitle: '提示词工程与RAG实战.md', seq: 5, content: '多模态检索里，图文向量怎么对齐到同一个空间？', referenceAnswer: '用对比学习在成对的图像和文本上训练双塔编码器，让匹配的图文对在共享空间里距离更近、不匹配的更远（如 CLIP）。检索时图搜文、文搜图都落到同一套相似度计算上。', topic: '多模态', difficulty: 2, tags: ['CLIP', '跨模态'], sourceMdLine: 186, createdAt: '2026-06-28 09:52', updatedAt: '2026-06-28 09:52' },
    { id: 'q017', direction: 'AI应用与智能体开发', docTitle: 'LangChain与Agent开发.md', seq: 4, content: 'LangGraph 里节点和边的运行模型是什么？和普通 Chain 有什么不同？', referenceAnswer: '把流程建模成状态图：节点是函数，接收并返回状态，边决定下一步走哪；条件边让分支由状态决定，还支持循环与中断。普通 Chain 是线性有向无环，做不了循环与人工介入。', topic: 'LangGraph', difficulty: 3, tags: ['LangGraph', '状态图'], sourceMdLine: 168, createdAt: '2026-06-24 15:40', updatedAt: '2026-06-24 15:40' },
    { id: 'q018', direction: 'AI应用与智能体开发', docTitle: 'LangChain与Agent开发.md', seq: 5, content: 'Checkpointer 在 LangGraph 里解决什么问题？', referenceAnswer: '它把每一步的状态持久化，于是图可以在中断后按 thread_id 恢复继续跑，也为人工审批这类「暂停—外部输入—继续」的场景提供支撑，同时可用同一份 checkpoint 做回放调试。', topic: 'LangGraph', difficulty: 2, tags: ['LangGraph', '状态持久化'], sourceMdLine: 219, createdAt: '2026-06-24 15:45', updatedAt: '2026-06-24 15:45' },
    { id: 'q019', direction: 'AI大模型开发', docTitle: '向量数据库选型.md', seq: 5, content: '这段文档讲了向量库的部署方式，但标题没有落在词表里，具体属于哪一类？', referenceAnswer: '', topic: '', difficulty: 1, tags: ['部署'], sourceMdLine: 201, createdAt: '2026-07-02 11:22', updatedAt: '2026-07-02 11:22' },
    { id: 'q020', direction: 'AI应用与智能体开发', docTitle: 'LangChain与Agent开发.md', seq: 6, content: '解析出来的这道题是文档里的一个表格片段，没给出主题，该怎么处理？', referenceAnswer: '', topic: '', difficulty: 2, tags: [], sourceMdLine: 264, createdAt: '2026-06-24 15:50', updatedAt: '2026-06-24 15:50' }
  ],

  // 面试题库主题词表（对应配置项 kb.question.topics）；inVocabulary 为 false 表示题目主题不在词表内
  kbTopics: [
    { topic: '大模型基础', questionCount: 3, inVocabulary: true },
    { topic: 'Prompt工程', questionCount: 2, inVocabulary: true },
    { topic: 'RAG检索增强', questionCount: 4, inVocabulary: true },
    { topic: '向量数据库', questionCount: 2, inVocabulary: true },
    { topic: 'LangChain与Agent', questionCount: 3, inVocabulary: true },
    { topic: '模型微调', questionCount: 1, inVocabulary: true },
    { topic: '多模态', questionCount: 1, inVocabulary: true },
    { topic: '模型评估', questionCount: 0, inVocabulary: true },
    { topic: 'AIGC工程化', questionCount: 0, inVocabulary: true },
    { topic: 'LangGraph', questionCount: 2, inVocabulary: false }
  ],

  dashboardStats: {
    totalUsers: 12580, todayNewUsers: 156,
    totalQuestions: 1567, todayNewQuestions: 23,
    totalInterviews: 3420, todayInterviews: 89
  },

  // 管理后台 - 系统用户（管理员、编辑、运营等内部人员）
  adminUsers: [
    { id: 1, username: '管理员', phone: '138****8888', email: 'admin@itheima.com', role: '超级管理员', department: '技术部', status: 'active', lastLogin: '2026-07-24 08:00', createTime: '2025-01-01' },
    { id: 2, username: '李编辑', phone: '139****6666', email: 'editor@itheima.com', role: '内容编辑', department: '教研部', status: 'active', lastLogin: '2026-07-23 17:30', createTime: '2025-03-15' },
    { id: 3, username: '王运营', phone: '137****5555', email: 'ops@itheima.com', role: '运营人员', department: '运营部', status: 'active', lastLogin: '2026-07-22 09:00', createTime: '2025-06-01' },
    { id: 4, username: '赵主管', phone: '136****4444', email: 'lead@itheima.com', role: '管理员', department: '教研部', status: 'disabled', lastLogin: '2026-06-15 14:00', createTime: '2025-02-10' },
    { id: 5, username: '陈助理', phone: '135****3333', email: 'assistant@itheima.com', role: '运营人员', department: '运营部', status: 'active', lastLogin: '2026-07-24 09:15', createTime: '2025-08-20' },
  ],

  // 前台学员列表（互联网注册用户）
  students: [
    { id: 1, nickname: '张三', phone: '138****0001', email: 'zhangsan@test.com', status: 'active', registerTime: '2026-06-01', lastLogin: '2026-07-24 10:30', studyDays: 54, courseCount: 3, practiceCount: 356, accuracy: 78, interviewCount: 12 },
    { id: 2, nickname: '李四', phone: '138****0002', email: 'lisi@test.com', status: 'active', registerTime: '2026-06-03', lastLogin: '2026-07-23 15:20', studyDays: 41, courseCount: 2, practiceCount: 210, accuracy: 72, interviewCount: 8 },
    { id: 3, nickname: '王五', phone: '138****0003', email: 'wangwu@test.com', status: 'disabled', registerTime: '2026-06-05', lastLogin: '2026-07-10 09:00', studyDays: 18, courseCount: 1, practiceCount: 88, accuracy: 65, interviewCount: 3 },
    { id: 4, nickname: '赵六', phone: '138****0005', email: 'zhaoliu@test.com', status: 'active', registerTime: '2026-06-10', lastLogin: '2026-07-22 14:15', studyDays: 35, courseCount: 4, practiceCount: 520, accuracy: 82, interviewCount: 15 },
    { id: 5, nickname: '周七', phone: '138****0006', email: 'zhouqi@test.com', status: 'active', registerTime: '2026-06-15', lastLogin: '2026-07-24 11:00', studyDays: 30, courseCount: 2, practiceCount: 180, accuracy: 75, interviewCount: 6 },
    { id: 6, nickname: '吴八', phone: '138****0007', email: 'wuba@test.com', status: 'active', registerTime: '2026-06-20', lastLogin: '2026-07-21 16:45', studyDays: 22, courseCount: 1, practiceCount: 95, accuracy: 68, interviewCount: 2 },
    { id: 7, nickname: '郑九', phone: '138****0008', email: 'zhengjiu@test.com', status: 'active', registerTime: '2026-07-01', lastLogin: '2026-07-24 08:30', studyDays: 15, courseCount: 3, practiceCount: 310, accuracy: 85, interviewCount: 10 },
    { id: 8, nickname: '孙十', phone: '138****0009', email: 'sunshi@test.com', status: 'active', registerTime: '2026-07-05', lastLogin: '2026-07-23 20:00', studyDays: 12, courseCount: 1, practiceCount: 65, accuracy: 70, interviewCount: 1 },
    { id: 9, nickname: '冯小', phone: '138****0010', email: 'fengxiao@test.com', status: 'disabled', registerTime: '2026-07-10', lastLogin: '2026-07-18 11:20', studyDays: 5, courseCount: 0, practiceCount: 20, accuracy: 55, interviewCount: 0 },
    { id: 10, nickname: '陈明', phone: '138****0011', email: 'chenming@test.com', status: 'active', registerTime: '2026-07-15', lastLogin: '2026-07-24 14:00', studyDays: 8, courseCount: 2, practiceCount: 150, accuracy: 80, interviewCount: 5 },
  ],

  // 管理后台 - 角色列表（固定三个内置角色）
  adminRoles: [
    { id: 'r001', name: '超级管理员', code: 'super_admin', userCount: 1, description: '拥有全部权限，含系统管理', permissions: ['all'] },
    { id: 'r002', name: '内容审核', code: 'content_reviewer', userCount: 1, description: '只把关不生产：可查看全部内容并审核题目，无增删改权限', permissions: ['question:view', 'question:review', 'kb:view', 'route:view'] },
    { id: 'r003', name: '运营人员', code: 'operator', userCount: 2, description: '除系统管理外的全部操作，含内容维护与学员管理，不具备审核权限', permissions: ['question:view', 'question:create', 'question:edit', 'question:delete', 'question:import', 'question:export', 'kb:view', 'kb:upload', 'kb:edit', 'kb:delete', 'kb:search', 'route:view', 'route:create', 'route:edit', 'route:delete', 'student:view', 'student:edit', 'student:delete'] }
  ],

  // 管理后台 - 操作日志
  adminLogs: [
    { id: 'l001', user: '管理员', action: '登录系统', target: '-', ip: '192.168.1.1', time: '2026-07-24 08:00:00' },
    { id: 'l002', user: '管理员', action: '新增题目', target: 'HashMap的底层数据结构', ip: '192.168.1.1', time: '2026-07-24 08:30:00' },
    { id: 'l003', user: '管理员', action: '修改角色', target: '学员角色权限', ip: '192.168.1.1', time: '2026-07-24 09:15:00' },
    { id: 'l004', user: '管理员', action: '禁用用户', target: '王五', ip: '192.168.1.1', time: '2026-07-23 10:00:00' },
    { id: 'l005', user: '管理员', action: '上传文档', target: '大模型部署与推理优化.md', ip: '192.168.1.1', time: '2026-07-23 14:20:00' }
  ],

  // 学习进度统计
  studyStats: {
    totalPracticed: 356,
    totalCorrect: 278,
    accuracy: 78,
    studyDays: 54,
    currentStreak: 7,
    maxStreak: 15,
    dailyStats: [
      { date: '07-18', count: 15 },
      { date: '07-19', count: 22 },
      { date: '07-20', count: 8 },
      { date: '07-21', count: 30 },
      { date: '07-22', count: 18 },
      { date: '07-23', count: 25 },
      { date: '07-24', count: 12 }
    ]
  }
};

// 动画样式
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from { opacity: 0; transform: translateX(100px); }
    to { opacity: 1; transform: translateX(0); }
  }
  @keyframes slideOutRight {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(100px); }
  }
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);
