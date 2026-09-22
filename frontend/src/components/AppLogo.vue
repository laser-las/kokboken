<template>
  <router-link to="/recipes" class="app-logo" aria-label="Köksboken">
    <span class="book-icon" aria-hidden="true"><svg viewBox="0 0 32 32"><path d="M16 9c-3.8-3-8-2.1-10-1v15c2.7-1.3 6.7-1.2 10 1 3.3-2.2 7.3-2.3 10-1V8c-2-1.1-6.2-2-10 1Z"/><path d="M16 9v15"/></svg></span>
    <span>Köksboken</span>
  </router-link>
</template>
<style scoped>
.app-logo{display:flex;align-items:center;gap:14px;color:#312622;font:italic 700 clamp(1.25rem,2vw,2rem) Georgia,'Times New Roman',serif;text-decoration:none;letter-spacing:-.035em}.book-icon{display:grid;place-items:center;width:58px;height:58px;border-radius:15px;background:#cd7b55}.book-icon svg{width:33px;height:33px;fill:none;stroke:white;stroke-width:2.15;stroke-linejoin:round;stroke-linecap:round}@media(max-width:640px){.app-logo{gap:8px;font-size:1.3rem}.book-icon{width:38px;height:38px;border-radius:10px}.book-icon svg{width:24px;height:24px}}
</style>
