<script setup>
import { onMounted, ref } from "vue";
import { fetchDocuments } from "../api/documents.js";

// Состояния
const groups = ref([]); // список групп: { organization_id, organization_name, documents[] }
const loading = ref(false);
const error = ref("");

/**
 * Форматирует дату из "YYYY-MM-DD" в "DD.MM.YYYY".
 * Разбираем строку вручную, чтобы избежать сдвига часового пояса.
 */
const formatDate = (value) => {
  if (!value) return "-";
  const [year, month, day] = String(value).split("-");
  if (year && month && day) return `${day}.${month}.${year}`;
  return String(value);
};

/**
 * Загружает документы с бэкенда.
 * Бэк возвращает list[DocumentsByOrganization]:
 * [{ organization_id, organization_name, documents: [{ id, user_name, start_at, end_at, ... }] }]
 */
const loadDocuments = async () => {
  loading.value = true;
  error.value = "";

  try {
    const data = await fetchDocuments();
    // fetchDocuments возвращает массив групп
    groups.value = Array.isArray(data) ? data : data ? [data] : [];
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      e?.message ||
      "Не удалось загрузить документы";
  } finally {
    loading.value = false;
  }
};

onMounted(loadDocuments);
</script>

<template>
  <main class="mx-auto max-w-4xl px-2 py-6 sm:px-4">

    <!-- Заголовок + кнопка обновления -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Список документов</h1>
      <button
        @click="loadDocuments"
        :disabled="loading"
        class="rounded-lg bg-black px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
      >
        {{ loading ? "Загрузка..." : "Обновить" }}
      </button>
    </div>

    <!-- Состояния: загрузка / ошибка / пусто -->
    <p v-if="loading" class="text-gray-500">Загрузка...</p>

    <p
      v-else-if="error"
      class="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700"
    >
      {{ error }}
    </p>

    <p v-else-if="groups.length === 0" class="text-gray-500">
      Документов пока нет
    </p>

    <!--
      Основной контент: перебираем группы.
      Каждая группа — одна организация с таблицей своих документов.
    -->
    <div v-else class="flex flex-col gap-6">
      <div
        v-for="group in groups"
        :key="group.organization_id"
        class="overflow-x-auto rounded-xl border shadow-sm"
      >
        <!-- Шапка группы: название организации -->
        <div class="border-b bg-gray-50 px-4 py-2 text-sm">
          <span class="font-semibold text-gray-800">{{ group.organization_name }}</span>
          <span class="ml-2 text-xs text-gray-400">
            ID {{ group.organization_id }}
          </span>
        </div>

        <!-- Таблица документов этой организации -->
        <table class="min-w-full table-fixed border-collapse text-sm">
          <colgroup>
            <col class="w-[52%]" />
            <col class="w-[24%]" />
            <col class="w-[24%]" />
          </colgroup>

          <thead class="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th class="px-4 py-2 font-medium">Ф.И.О. работника</th>
              <th class="px-4 py-2 font-medium">Дата начала работ</th>
              <th class="px-4 py-2 font-medium">Дата окончания работ</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100 bg-white">
            <tr
              v-for="doc in group.documents"
              :key="doc.id"
              class="hover:bg-gray-50"
            >
              <td class="truncate px-4 py-3 font-medium text-gray-900">
                {{ doc.user_name ?? "-" }}
              </td>
              <td class="whitespace-nowrap px-4 py-3 text-gray-700">
                {{ formatDate(doc.start_at) }}
              </td>
              <td class="whitespace-nowrap px-4 py-3 text-gray-700">
                {{ formatDate(doc.end_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </main>
</template>

