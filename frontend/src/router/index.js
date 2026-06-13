import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    // Ленивая загрузка: компонент грузится только при первом переходе на /create
    path: "/create",
    name: "create-document",
    component: () => import("../views/CreateDocumentView.vue"),
  },
  {
    path: "/documents/:document_id/edit",
    name: "edit-document",
    component: () => import("../views/EditDocumentView.vue"),
  },
  {
    path: "/organizations/create",
    name: "create-organization",
    component: () => import("../views/CreateOrganizationView.vue"),
  },
];

const router = createRouter({
  // createWebHistory — «чистые» URL без решётки: / и /create вместо /#/ и /#/create
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;

