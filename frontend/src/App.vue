<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "./store/auth.js";

const router = useRouter();
const { state, isAuthenticated, logout, fetchUser } = useAuth();

// При первой загрузке приложения подгружаем данные пользователя, если есть токен
onMounted(() => {
  fetchUser();
});

const handleLogout = () => {
  logout();
  router.push("/login");
};
</script>

<template>
  <!-- Общая обёртка приложения: шапка + контент -->
  <div class="min-h-screen bg-gray-50">

    <!-- Навигационная панель -->
    <nav class="border-b bg-white shadow-sm">
      <div class="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <span class="text-lg font-bold tracking-tight">📄 EndDocument</span>

        <div class="flex items-center gap-3">
          <!-- Основная навигация — только для авторизованных -->
          <template v-if="isAuthenticated()">
            <!-- RouterLink не перезагружает страницу, как обычный <a> -->
            <RouterLink
              to="/"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              Список
            </RouterLink>

            <RouterLink
              to="/archive"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              Архив
            </RouterLink>

            <RouterLink
              to="/create"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              + Создать
            </RouterLink>

            <RouterLink
              to="/organizations/create"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              + Организация
            </RouterLink>

            <!-- Разделитель -->
            <span class="h-5 w-px bg-gray-200"></span>

            <!-- Ссылка на админ-панель (только для суперпользователей) -->
            <RouterLink
              v-if="state.user?.is_superuser"
              to="/admin/users"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              👥 Пользователи
            </RouterLink>

            <!-- Имя пользователя -->
            <span v-if="state.user" class="text-sm text-gray-500">
              {{ state.user.username }}
            </span>

            <!-- Выход -->
            <button
              @click="handleLogout"
              class="rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Выйти
            </button>
          </template>

          <!-- Ссылки для гостей -->
          <template v-else>
            <RouterLink
              to="/login"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              Войти
            </RouterLink>
            <RouterLink
              to="/register"
              class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
              active-class="bg-black text-white hover:bg-black"
            >
              Регистрация
            </RouterLink>
          </template>
        </div>
      </div>
    </nav>

    <!-- Сюда роутер подставляет нужный компонент -->
    <RouterView />

  </div>
</template>