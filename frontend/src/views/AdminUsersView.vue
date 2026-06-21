<script setup>
import { onMounted, ref } from "vue";
import { fetchAllUsers, activateUser, deactivateUser } from "../api/users.js";
import { useAuth } from "../store/auth.js";

const { state } = useAuth();
const users = ref([]);
const loading = ref(false);
const error = ref("");
const actionLoading = ref(null); // id пользователя, над которым выполняется действие

const loadUsers = async () => {
  loading.value = true;
  error.value = "";
  try {
    users.value = await fetchAllUsers();
  } catch (e) {
    error.value =
      e?.response?.data?.detail || e?.message || "Не удалось загрузить пользователей";
  } finally {
    loading.value = false;
  }
};

const handleActivate = async (user) => {
  actionLoading.value = user.id;
  try {
    const updated = await activateUser(user.id);
    const idx = users.value.findIndex((u) => u.id === user.id);
    if (idx !== -1) users.value[idx] = updated;
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || "Ошибка активации";
  } finally {
    actionLoading.value = null;
  }
};

const handleDeactivate = async (user) => {
  actionLoading.value = user.id;
  try {
    const updated = await deactivateUser(user.id);
    const idx = users.value.findIndex((u) => u.id === user.id);
    if (idx !== -1) users.value[idx] = updated;
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || "Ошибка деактивации";
  } finally {
    actionLoading.value = null;
  }
};

const formatDate = (value) => {
  if (!value) return "—";
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

onMounted(loadUsers);
</script>

<template>
  <main class="mx-auto max-w-4xl px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold tracking-tight text-gray-900">
        Управление пользователями
      </h1>
      <button
        @click="loadUsers"
        class="rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
      >
        Обновить
      </button>
    </div>

    <!-- Загрузка -->
    <p v-if="loading" class="text-sm text-gray-500">Загрузка…</p>

    <!-- Ошибка -->
    <p v-if="error" class="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
      {{ error }}
    </p>

    <!-- Таблица пользователей -->
    <div v-if="!loading && users.length" class="overflow-hidden rounded-xl border bg-white shadow-sm">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
          <tr>
            <th class="px-4 py-3">Пользователь</th>
            <th class="px-4 py-3">Email</th>
            <th class="px-4 py-3">Статус</th>
            <th class="px-4 py-3">Роль</th>
            <th class="px-4 py-3">Дата регистрации</th>
            <th class="px-4 py-3">Действия</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr
            v-for="user in users"
            :key="user.id"
            class="hover:bg-gray-50"
          >
            <td class="px-4 py-3 font-medium text-gray-900">{{ user.username }}</td>
            <td class="px-4 py-3 text-gray-600">{{ user.email || "—" }}</td>
            <td class="px-4 py-3">
              <span
                :class="[
                  'inline-flex rounded-full px-2 py-0.5 text-xs font-medium',
                  user.is_active
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700',
                ]"
              >
                {{ user.is_active ? "Активен" : "Ожидает" }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span
                v-if="user.is_superuser"
                class="inline-flex rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700"
              >
                Администратор
              </span>
              <span v-else class="text-gray-400">Пользователь</span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ formatDate(user.created_at) }}</td>
            <td class="px-4 py-3">
              <!-- Нельзя менять статус своего аккаунта -->
              <span v-if="user.id === state.user?.id" class="text-xs text-gray-400">
                (это вы)
              </span>
              <template v-else>
                <button
                  v-if="!user.is_active"
                  :disabled="actionLoading === user.id"
                  @click="handleActivate(user)"
                  class="rounded-lg bg-green-600 px-3 py-1 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
                >
                  {{ actionLoading === user.id ? "…" : "Активировать" }}
                </button>
                <button
                  v-else
                  :disabled="actionLoading === user.id"
                  @click="handleDeactivate(user)"
                  class="rounded-lg border px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                >
                  {{ actionLoading === user.id ? "…" : "Деактивировать" }}
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="!loading && !users.length && !error" class="text-sm text-gray-500">
      Нет пользователей.
    </p>
  </main>
</template>
