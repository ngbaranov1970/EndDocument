import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { useAuth } from "../store/auth.js";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("../views/RegisterView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/create",
    name: "create-document",
    component: () => import("../views/CreateDocumentView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/documents/:document_id/edit",
    name: "edit-document",
    component: () => import("../views/EditDocumentView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/organizations/create",
    name: "create-organization",
    component: () => import("../views/CreateOrganizationView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/archive",
    name: "archive",
    component: () => import("../views/ArchiveView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/users",
    name: "admin-users",
    component: () => import("../views/AdminUsersView.vue"),
    meta: { requiresAuth: true, requiresSuperuser: true },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Навигационный guard
router.beforeEach((to) => {
  const { isAuthenticated, state } = useAuth();
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: "login" };
  }
  if (to.meta.guestOnly && isAuthenticated()) {
    return { name: "home" };
  }
  if (to.meta.requiresSuperuser && !state.user?.is_superuser) {
    return { name: "home" };
  }
});

export default router;

