<script setup lang="ts">
import BrandMark from './BrandMark.vue'
defineProps<{ audience: string; title: string; description: string; backHref: string }>()
</script>
<template>
  <div class="ys-auth-page">
    <header class="ys-auth-top"><a :href="backHref" class="ys-auth-brand"><BrandMark /><span>云枢智学</span><small>{{ audience }}</small></a><a :href="backHref" class="ys-auth-back">← 返回学员首页</a></header>
    <main class="ys-auth-card">
      <section class="ys-auth-story">
        <span class="ys-auth-eyebrow">LEARN. PRACTICE. GROW.</span>
        <h1>每一次积累，<br>都在靠近<span>更好的自己。</span></h1>
        <p>把知识连成体系，把练习融入日常。<br>在云枢智学，让每一步成长都有方向。</p>
        <div class="ys-auth-art" aria-hidden="true"><div class="ys-auth-orbit"></div><div class="ys-auth-orbit is-second"></div><div class="ys-auth-art-core"><BrandMark light /></div><span class="ys-auth-float one">学 · 知识体系</span><span class="ys-auth-float two">练 · 温故知新</span><span class="ys-auth-float three">进 · 日积月累</span></div>
        <div class="ys-auth-story-footer"><span class="ys-auth-dot"></span>让学习更有章法，让成长清晰可见</div>
      </section>
      <section class="ys-auth-form-pane"><div class="ys-auth-form-inner"><span class="ys-auth-form-label">{{ audience }}</span><h2>{{ title }}</h2><p class="ys-auth-description">{{ description }}</p><slot /></div></section>
    </main>
    <footer class="ys-auth-footer">云枢智学 · 专注每一步成长</footer>
  </div>
</template>
<style scoped>
.ys-auth-page { min-height: 100dvh; color: #25314d; background: radial-gradient(ellipse at 8% 35%, #ecebff, transparent 52%), radial-gradient(ellipse at 92% 88%, #e9efff, transparent 50%), #f7f8fc; font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif; padding: 0 5%; }
.ys-auth-top { height: 88px; max-width: 1240px; margin: auto; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.ys-auth-brand { display: flex; align-items: center; gap: 10px; color: #25314d; text-decoration: none; font-size: 23px; font-weight: 750; }
.ys-auth-brand small { border-left: 1px solid #dce0ed; padding-left: 14px; margin-left: 7px; font-size: 13px; font-weight: 400; color: #8b93a7; }
.ys-auth-back { font-size: 13px; color: #7d859b; text-decoration: none; }
.ys-auth-card { display: grid; grid-template-columns: 1fr 1fr; max-width: 1100px; min-height: 620px; margin: 36px auto 0; border: 1px solid #e9ebf3; border-radius: 24px; background: #fff; overflow: hidden; box-shadow: 0 22px 70px #34425e0a; padding: 0; }
.ys-auth-story { position: relative; padding: 52px 45px 32px; background: linear-gradient(145deg, #212339, #36324f); color: #fff; display: flex; flex-direction: column; overflow: hidden; }
.ys-auth-eyebrow { color: #bcb9dc; font-size: 10px; font-weight: 600; letter-spacing: 2px; }
.ys-auth-story h1 { font-size: clamp(28px, 3vw, 36px); font-weight: 600; line-height: 1.65; letter-spacing: 1px; margin: 25px 0 15px; color: white; }
.ys-auth-story h1 span { color: #c0b7ff; }
.ys-auth-story > p { color: #c1bfd2; line-height: 1.9; font-size: 13px; margin: 0; }
.ys-auth-art { position: relative; flex: 1; min-height: 230px; }
.ys-auth-orbit { position: absolute; width: 240px; height: 190px; left: 50%; top: 52%; border: 1px solid #ffffff16; border-radius: 50%; transform: translate(-50%, -50%) rotate(-28deg); }
.ys-auth-orbit.is-second { width: 150px; height: 220px; transform: translate(-50%, -50%) rotate(-28deg); }
.ys-auth-art-core { display: grid; place-items: center; position: absolute; left: 50%; top: 52%; width: 90px; height: 90px; transform: translate(-50%, -50%); border-radius: 24px; background: linear-gradient(135deg, #7770c955, #c3b1ff11); border: 1px solid #bfb5ff33; box-shadow: 0 0 60px #a9a0f520; }
.ys-auth-art-core :deep(svg) { width: 56px; height: 56px; }
.ys-auth-float { position: absolute; padding: 11px 16px; border: 1px solid #c9c4ee26; border-radius: 10px; font-size: 11px; background: #ffffff0b; color: #e3e0f6; backdrop-filter: blur(8px); letter-spacing: 1px; }
.ys-auth-float.one { left: 0; top: 20%; transform: rotate(-7deg); }.ys-auth-float.two { right: 0; top: 40%; transform: rotate(7deg); }.ys-auth-float.three { left: 13%; bottom: 6%; transform: rotate(-3deg); }
.ys-auth-story-footer { color: #aeabc4; font-size: 11px; display: flex; align-items: center; gap: 8px; margin-top: 18px; }.ys-auth-dot { width: 5px; height: 5px; background: #b2a7fa; border-radius: 50%; }
.ys-auth-form-pane { display: flex; align-items: center; justify-content: center; padding: 52px; }.ys-auth-form-inner { width: 100%; max-width: 340px; }
.ys-auth-form-label { color: #7c70be; font-size: 11px; letter-spacing: 2px; font-weight: 600; }.ys-auth-form-pane h2 { font-size: 28px; color: #222d46; margin: 13px 0 10px; font-weight: 650; }.ys-auth-description { color: #9299aa; font-size: 13px; line-height: 1.8; margin: 0 0 32px; }
.ys-auth-footer { text-align: center; font-size: 11px; color: #9ca3b5; padding: 28px 0; margin: 0; }
@media(max-width: 820px) { .ys-auth-card { grid-template-columns: 1fr; max-width: 480px; margin-top: 16px; min-height: 0; }.ys-auth-story { display: none; }.ys-auth-form-pane { padding: 44px 32px; min-height: 500px; }.ys-auth-top { height: 76px; }.ys-auth-brand small { display: none; }.ys-auth-page { padding: 0 20px; } }
@media(prefers-reduced-motion: reduce) { * { scroll-behavior: auto; } }
</style>
