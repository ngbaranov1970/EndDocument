<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { loginUser } from "../api/auth.js";
import { useAuth } from "../store/auth.js";

const router = useRouter();
const { setTokens, fetchUser } = useAuth();

const form = reactive({ username: "", password: "" });
const loading = ref(false);
const error = ref("");

const handleSubmit = async () => {
  error.value = "";
  if (!form.username.trim() || !form.password) {
    error.value = "Заполните все поля";
    return;
  }

  loading.value = true;
  try {
    const data = await loginUser(form.username.trim(), form.password);
    setTokens(data.access_token, data.refresh_token);
    await fetchUser();
    router.push("/");
  } catch (e) {
    const detail = e?.response?.data?.detail || "";
    if (detail.toLowerCase().includes("not activated")) {
      error.value = "Ваш аккаунт ещё не активирован. Обратитесь к администратору.";
    } else {
      error.value = detail || e?.message || "Неверный логин или пароль";
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="flex min-h-[calc(100vh-57px)] items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm rounded-xl border bg-white p-8 shadow-sm">
      <h1 class="mb-6 text-center text-2xl font-bold tracking-tight text-gray-900">
        Вход в систему
      </h1>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Логин -->
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Имя пользователя
          </label>
          <input
            v-model="form.username"
            type="text"
            autocomplete="username"
            placeholder="username"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-black focus:ring-1 focus:ring-black"
          />
        </div>

        <!-- Пароль -->
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Пароль
          </label>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-black focus:ring-1 focus:ring-black"
          />
        </div>

        <!-- Ошибка -->
        <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          {{ error }}
        </p>

        <!-- Кнопка -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-lg bg-black py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
        >
          {{ loading ? "Вход…" : "Войти" }}
        </button>
      </form>

      <p class="mt-5 text-center text-sm text-gray-500">
        Нет аккаунта?
        <RouterLink to="/register" class="font-medium text-black underline-offset-2 hover:underline">
          Зарегистрироваться
        </RouterLink>
      </p>
    </div>
  </div>
</template>
