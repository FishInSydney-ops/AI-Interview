<script setup lang="ts">
import BrandMark from '@yunshu/shared/BrandMark.vue'
const subjects = [
  { symbol: 'Py', name: 'Python 基础', text: '从语法到核心数据结构，构建扎实的编程基础。', color: 'blue', tag: '编程入门' },
  { symbol: '✦', name: 'VibeCoding 基础', text: '探索 AI 辅助开发，建立清晰的协作与实践思路。', color: 'purple', tag: 'AI 协作' },
  { symbol: 'DB', name: '数据库基础', text: '理解数据组织与查询，让每一次存取有据可循。', color: 'teal', tag: '数据思维' },
]
</script>
<template>
  <section class="portal-hero">
    <div class="portal-hero-copy"><span class="portal-kicker"><span></span>为每一个认真学习的你</span><h1>把知识学扎实，<br>让成长<span>看得见。</span></h1><p>循序渐进的学习路线，随学随练的知识巩固。<br>从一个知识点开始，积累解决问题的能力。</p><div class="portal-hero-actions"><RouterLink class="portal-primary" to="/routes">开始学习 <span>→</span></RouterLink><RouterLink class="portal-secondary" to="/questions">浏览题库 <span>↗</span></RouterLink></div><div class="portal-hero-notes"><span>✓ 体系化学习</span><span>✓ 练习与巩固</span><span>✓ 自主掌握节奏</span></div></div>
    <div class="portal-hero-visual" aria-hidden="true"><div class="portal-visual-circle"></div><div class="portal-path-card"><div class="portal-card-eyebrow"><BrandMark /><span>你的学习，从这里出发</span></div><strong>积累每一小步</strong><div class="portal-path-step"><i>01</i><div><b>选择学习方向</b><span>找到适合自己的起点</span></div></div><div class="portal-path-step"><i>02</i><div><b>沿着路线学习</b><span>把零散知识串成体系</span></div></div><div class="portal-path-step"><i>03</i><div><b>用练习巩固所学</b><span>把理解转化为自己的能力</span></div></div></div><span class="portal-float-label"><span>✧</span> 保持好奇，持续进步</span></div>
  </section>
  <section class="portal-directions"><div class="portal-section-title"><div><span class="portal-eyebrow">FIND YOUR PATH</span><h2>找到你的学习方向</h2></div><RouterLink to="/routes">查看学习路线 <span>→</span></RouterLink></div><div class="portal-subject-grid"><RouterLink v-for="subject in subjects" :key="subject.name" to="/routes" class="portal-subject-card"><div class="portal-subject-top"><span class="portal-subject-symbol" :class="subject.color">{{ subject.symbol }}</span><span class="portal-subject-tag">{{ subject.tag }}</span></div><h3>{{ subject.name }}</h3><p>{{ subject.text }}</p><span class="portal-subject-link">了解学习方向 <span>→</span></span></RouterLink></div></section>
  <section class="portal-bottom-banner"><div><span class="portal-eyebrow">STEP BY STEP</span><h2>不必一次学会所有，先迈出下一步。</h2><p>一段课程，一次练习，都是向前的积累。</p></div><RouterLink to="/questions">去题库看看 →</RouterLink></section>
</template>
