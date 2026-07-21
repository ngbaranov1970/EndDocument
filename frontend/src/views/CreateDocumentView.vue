<script setup>
import { onMounted, ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { createDocument } from "../api/documents.js";
import { fetchOrganizations } from "../api/organizations.js";

const router = useRouter();

// Список организаций для <select>
const organizations = ref([]);
const orgsLoading = ref(false);
const orgsError = ref("");

// Организация выбирается один раз на весь пакет и не сбрасывается после сохранения
const selectedOrgId = ref("");

// Черновик строки — мини-форма добавления документа в локальный список
const draftRow = reactive({
  user_name: "",
  start_at: "",
  end_at: "",
});
const addRowError = ref("");

// Накопленный локально список документов, ещё не отправленных на сервер
const pendingRows = ref([]); // [{ id, user_name, start_at, end_at, error }]
let nextRowId = 1;

// Состояния пакетной отправки
const submitting = ref(false);
const submitError = ref("");
const successMessage = ref("");

/** Загружаем организации при монтировании компонента */
const loadOrganizations = async () => {
  orgsLoading.value = true;
  orgsError.value = "";
  try {
    organizations.value = await fetchOrganizations();
  } catch (e) {
    orgsError.value =
      e?.response?.data?.detail || e?.message || "Не удалось загрузить организации";
  } finally {
    orgsLoading.value = false;
  }
};

onMounted(loadOrganizations);

/**
 * Общая валидация одной строки документа.
 * Используется и при добавлении в список, и повторно перед пакетной отправкой
 * (строки редактируются прямо в списке, поэтому могли снова стать невалидными).
 */
const validateRow = ({ user_name, start_at, end_at }) => {
  if (user_name.trim().length < 3) return "Ф.И.О. должно содержать не менее 3 символов";
  if (!start_at || !end_at) return "Укажите даты начала и окончания работ";
  if (start_at > end_at) return "Дата начала не может быть позже даты окончания";
  return "";
};

/** Добавляет черновик в локальный список документов на сохранение */
const handleAddRow = () => {
  addRowError.value = "";

  if (!selectedOrgId.value) {
    addRowError.value = "Сначала выберите организацию";
    return;
  }

  const error = validateRow(draftRow);
  if (error) {
    addRowError.value = error;
    return;
  }

  pendingRows.value.push({
    id: nextRowId++,
    user_name: draftRow.user_name.trim(),
    start_at: draftRow.start_at,
    end_at: draftRow.end_at,
    error: "",
  });

  draftRow.user_name = "";
  draftRow.start_at = "";
  draftRow.end_at = "";
  successMessage.value = "";
};

/** Убирает строку из локального списка */
const handleRemoveRow = (id) => {
  pendingRows.value = pendingRows.value.filter((row) => row.id !== id);
};

/** Полностью очищает несохранённый список (например, чтобы сменить организацию) */
const handleClearPending = () => {
  if (pendingRows.value.length === 0) return;
  if (!confirm("Удалить весь несохранённый список?")) return;
  pendingRows.value = [];
};

/**
 * Пакетная отправка накопленных документов.
 * Бэкенд не поддерживает bulk-создание, поэтому шлём по одному запросу на строку.
 */
const handleBatchSubmit = async () => {
  submitError.value = "";
  successMessage.value = "";

  if (!selectedOrgId.value) {
    submitError.value = "Выберите организацию";
    return;
  }
  if (pendingRows.value.length === 0) {
    submitError.value = "Список пуст — добавьте хотя бы один документ";
    return;
  }

  // Строки редактируются прямо в списке — перепроверяем перед отправкой
  const hasInvalid = pendingRows.value
    .map((row) => {
      row.error = validateRow(row);
      return row.error;
    })
    .some(Boolean);

  if (hasInvalid) {
    submitError.value = "Исправьте отмеченные строки перед сохранением";
    return;
  }

  submitting.value = true;

  const organizationId = Number(selectedOrgId.value);
  const stillPending = [];
  let succeededCount = 0;

  for (const row of pendingRows.value) {
    try {
      await createDocument({
        organization_id: organizationId,
        user_name: row.user_name,
        start_at: row.start_at,
        end_at: row.end_at,
      });
      succeededCount++;
    } catch (e) {
      row.error = e?.response?.data?.detail || e?.message || "Не удалось сохранить";
      stillPending.push(row);
    }
  }

  pendingRows.value = stillPending;

  if (stillPending.length === 0) {
    successMessage.value = `Сохранено документов: ${succeededCount}`;
  } else {
    submitError.value = `Сохранено ${succeededCount} из ${succeededCount + stillPending.length}. Исправьте отмеченные строки и повторите.`;
  }

  submitting.value = false;
};

/** Переход к списку документов; предупреждает, если есть несохранённые строки */
const handleGoToList = () => {
  if (
    pendingRows.value.length > 0 &&
    !confirm("Есть несохранённые документы в списке. Перейти к списку без сохранения?")
  ) {
    return;
  }
  router.push("/");
};
</script>

<template>
  <main class="mx-auto max-w-3xl px-4 py-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Создать документы</h1>
      <button
        type="button"
        @click="handleGoToList"
        class="rounded-lg border px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
      >
        К списку документов
      </button>
    </div>

    <div class="flex flex-col gap-5">

      <!-- Организация: выбирается один раз на весь пакет -->
      <div class="flex flex-col gap-1 rounded-xl border bg-white p-6 shadow-sm">
        <label class="text-sm font-medium text-gray-700">Организация</label>

        <p v-if="orgsLoading" class="text-sm text-gray-400">Загрузка...</p>
        <p v-else-if="orgsError" class="text-sm text-red-600">{{ orgsError }}</p>
        <p v-else-if="organizations.length === 0" class="text-sm text-amber-700">
          Нет активных организаций.
          <RouterLink to="/organizations/create" class="underline hover:no-underline">
            Добавить организацию
          </RouterLink>
        </p>

        <select
          v-else
          v-model="selectedOrgId"
          :disabled="pendingRows.length > 0"
          class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-400"
        >
          <option value="" disabled>Выберите организацию...</option>
          <option
            v-for="org in organizations"
            :key="org.id"
            :value="org.id"
          >
            {{ org.name }}
          </option>
        </select>

        <p v-if="pendingRows.length > 0" class="text-xs text-gray-400">
          Чтобы сменить организацию, сначала сохраните или очистите список ниже.
        </p>

        <RouterLink
          v-if="!orgsLoading && !orgsError"
          to="/organizations/create"
          class="w-fit text-xs text-gray-500 underline hover:text-gray-700 hover:no-underline"
        >
          + Добавить организацию
        </RouterLink>
      </div>

      <!-- Добавление строки в локальный список -->
      <form
        @submit.prevent="handleAddRow"
        novalidate
        class="flex flex-col gap-4 rounded-xl border bg-white p-6 shadow-sm"
      >
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">Ф.И.О. работника</label>
          <input
            v-model="draftRow.user_name"
            type="text"
            placeholder="Иванов Иван Иванович"
            minlength="3"
            maxlength="255"
            class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-gray-700">Дата начала работ</label>
            <input
              v-model="draftRow.start_at"
              type="date"
              class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>

          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-gray-700">Дата окончания работ</label>
            <input
              v-model="draftRow.end_at"
              type="date"
              class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
        </div>

        <p v-if="addRowError" class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {{ addRowError }}
        </p>

        <button
          type="submit"
          :disabled="!selectedOrgId"
          class="self-end rounded-lg border px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Добавить в список
        </button>
      </form>

      <!-- Список несохранённых документов -->
      <div v-if="pendingRows.length > 0" class="overflow-x-auto rounded-xl border shadow-sm">
        <div class="flex items-center justify-between border-b bg-gray-50 px-4 py-2 text-sm">
          <span class="font-semibold text-gray-800">К сохранению ({{ pendingRows.length }})</span>
          <button
            type="button"
            @click="handleClearPending"
            class="text-xs text-gray-500 underline hover:text-gray-700 hover:no-underline"
          >
            Очистить список
          </button>
        </div>

        <table class="min-w-full table-fixed border-collapse text-sm">
          <colgroup>
            <col class="w-[40%]" />
            <col class="w-[20%]" />
            <col class="w-[20%]" />
            <col class="w-[20%]" />
          </colgroup>

          <thead class="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th class="px-4 py-2 font-medium">Ф.И.О. работника</th>
              <th class="px-4 py-2 font-medium">Дата начала работ</th>
              <th class="px-4 py-2 font-medium">Дата окончания работ</th>
              <th class="px-4 py-2 font-medium">Действия</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100 bg-white">
            <tr
              v-for="row in pendingRows"
              :key="row.id"
              :class="row.error ? 'bg-red-50' : ''"
            >
              <td class="px-4 py-3 align-top">
                <input
                  v-model="row.user_name"
                  type="text"
                  class="w-full rounded-lg border px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-black"
                />
                <p v-if="row.error" class="mt-1 text-xs text-red-700">{{ row.error }}</p>
              </td>
              <td class="px-4 py-3 align-top">
                <input
                  v-model="row.start_at"
                  type="date"
                  class="w-full rounded-lg border px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-black"
                />
              </td>
              <td class="px-4 py-3 align-top">
                <input
                  v-model="row.end_at"
                  type="date"
                  class="w-full rounded-lg border px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-black"
                />
              </td>
              <td class="px-4 py-3 align-top">
                <button
                  type="button"
                  @click="handleRemoveRow(row.id)"
                  class="inline-flex rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Сообщения об ошибке / успехе пакетной отправки -->
      <p
        v-if="submitError"
        class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
      >
        {{ submitError }}
      </p>

      <p
        v-if="successMessage"
        class="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700"
      >
        {{ successMessage }}
      </p>

      <!-- Пакетное сохранение -->
      <div class="flex justify-end">
        <button
          type="button"
          @click="handleBatchSubmit"
          :disabled="submitting || pendingRows.length === 0"
          class="rounded-lg bg-black px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
        >
          {{ submitting ? "Сохранение..." : `Сохранить (${pendingRows.length})` }}
        </button>
      </div>

    </div>
  </main>
</template>
