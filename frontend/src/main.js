import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router/index.js";

// .use(router) — подключаем vue-router как плагин,
// чтобы <RouterView> и <RouterLink> работали во всех компонентах
createApp(App).use(router).mount("#app");
