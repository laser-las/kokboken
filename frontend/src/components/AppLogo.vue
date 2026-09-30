<script setup lang="ts"></script>

<template>
  <router-link to="/recipes" class="app-logo logo" aria-label="Köksboken, till startsidan">
    <span class="mark" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="M12 6.5C10.5 5.3 8.3 4.8 5 5v12c3.3-.2 5.5.3 7 1.5 1.5-1.2 3.7-1.7 7-1.5V5c-3.3-.2-5.5.3-7 1.5z" /><path d="M12 6.5v12" /></svg>
    </span>Köksboken
  </router-link>
</template>

<style scoped>
.app-logo { display: inline-flex; align-items: center; gap: .65rem; flex-shrink: 0; color: #9d5138; font-size: 1.3rem; font-style: italic; font-weight: 700; text-decoration: none; }
.mark { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 11px; background: linear-gradient(135deg, #d47a55, #b8532f); box-shadow: 0 4px 10px rgba(196, 98, 63, .3); transition: transform .2s; }
.app-logo:hover .mark { transform: rotate(-6deg) scale(1.05); }
svg { width: 20px; height: 20px; fill: none; stroke: #fff; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
</style>
