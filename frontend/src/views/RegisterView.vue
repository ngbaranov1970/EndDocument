<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { registerUser } from "../api/auth.js";

const router = useRouter();

const form = reactive({ username: "", email: "", password: "", confirm: "" });
const loading = ref(false);
const error = ref("");
const registered = ref(false); // флаг успешной регистрации

const handleSubmit = async () => {
  error.value = "";

  if (!form.username.trim() || !form.email.trim() || !form.password) {
    error.value = "Заполните все поля";
    return;
  }
  if (form.username.trim().length < 3) {
    error.value = "Имя пользователя должно содержать не менее 3 символов";
    return;
  }
  if (form.password.length < 6) {
    error.value = "Пароль должен содержать не менее 6 символов";
    return;
  }
  if (form.password !== form.confirm) {
    error.value = "Пароли не совпадают";
    return;
  }

  loading.value = true;
  try {
    await registerUser(form.username.trim(), form.password, form.email.trim());
    registered.value = true;
  } catch (e) {
    error.value =
      e?.response?.data?.detail || e?.message || "Ошибка при регистрации";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="flex min-h-[calc(100vh-57px)] items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm rounded-xl border bg-white p-8 shadow-sm">

      <!-- Успешная регистрация — ожидание активации -->
      <div v-if="registered" class="text-center">
        <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-2xl">
          ✓
        </div>
        <h2 class="mb-2 text-lg font-bold text-gray-900">Заявка отправлена</h2>
        <p class="mb-6 text-sm text-gray-500">
          Ваш аккаунт создан и ожидает активации администратором.
          Когда он вас активирует — вы сможете войти.
        </p>
        <RouterLink
          to="/login"
          class="inline-block rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          Перейти ко входу
        </RouterLink>
      </div>

      <!-- Форма регистрации -->
      <template v-else>
        <h1 class="mb-6 text-center text-2xl font-bold tracking-tight text-gray-900">
          Регистрация
        </h1>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Имя пользователя -->
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

          <!-- Email -->
          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">
              Электронная почта
            </label>
            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="user@example.com"
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
              autocomplete="new-password"
              placeholder="••••••"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-black focus:ring-1 focus:ring-black"
            />
          </div>

          <!-- Подтверждение пароля -->
          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">
              Подтверждение пароля
            </label>
            <input
              v-model="form.confirm"
              type="password"
              autocomplete="new-password"
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
            {{ loading ? "Регистрация…" : "Зарегистрироваться" }}
          </button>
        </form>

        <p class="mt-5 text-center text-sm text-gray-500">
          Уже есть аккаунт?
          <RouterLink to="/login" class="font-medium text-black underline-offset-2 hover:underline">
            Войти
          </RouterLink>
        </p>
      </template>
    </div>
  </div>
</template>
