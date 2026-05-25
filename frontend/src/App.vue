<script setup>
import { onMounted, ref } from "vue";
import { fetchDocuments } from "./api/documents.js";

const documents = ref([]);
const loading = ref(false);
const error = ref("");

const formatDate = (value) => {
  if (!value) return "-";

  // Для строк вида YYYY-MM-DD форматируем без смещения часового пояса
  const [year, month, day] = String(value).split("-");
  if (year && month && day) {
    return `${day}.${month}.${year}`;
  }

  return String(value);
};

const loadDocuments = async () => {
  loading.value = true;
  error.value = "";

  try {
    const data = await fetchDocuments();

    // Нормализуем ответ: если бек вернул не массив, сделаем массив из одного элемента
    documents.value = Array.isArray(data) ? data : data ? [data] : [];
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
  <main class="mx-auto max-w-4xl px-2 py-6 sm:px-3">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Список документов</h1>
      <button
        @click="loadDocuments"
        class="rounded-lg bg-black px-4 py-2 text-white hover:opacity-90"
      >
        Обновить
      </button>
    </div>

    <p v-if="loading" class="text-gray-500">Загрузка...</p>

    <p v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">
      {{ error }}
    </p>

    <p v-else-if="documents.length === 0" class="text-gray-500">
      Документов пока нет
    </p>

    <div v-else class="overflow-x-auto rounded-xl border shadow-sm">
      <div class="border-b bg-gray-50 px-3 py-2 text-sm text-gray-600 sm:px-4">
        <span class="font-medium text-gray-700">
          {{ documents[0]?.organization_name ?? "Организация не указана" }}
        </span>
        <span class="ml-2 text-xs text-gray-400">
          {{ formatDate(documents[0]?.created_at) }}
        </span>
      </div>

      <table class="min-w-full table-fixed border-collapse text-sm">
        <colgroup>
          <col class="w-[52%]" />
          <col class="w-[24%]" />
          <col class="w-[24%]" />
        </colgroup>
        <thead class="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
          <tr>
            <th class="px-3 py-2 font-medium sm:px-4">Ф.И.О. работника</th>
            <th class="px-3 py-2 font-medium sm:px-4">Дата начала работ</th>
            <th class="px-3 py-2 font-medium sm:px-4">Дата окончания работ</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-100 bg-white">
          <tr v-for="doc in documents" :key="doc.id ?? `${doc.user_name}-${doc.start_at}-${doc.end_at}`">
            <td class="truncate px-3 py-3 font-medium text-gray-900 sm:px-4">
              {{ doc.user_name ?? "-" }}
            </td>
            <td class="whitespace-nowrap px-3 py-3 text-gray-700 sm:px-4">
              {{ formatDate(doc.start_at) }}
            </td>
            <td class="whitespace-nowrap px-3 py-3 text-gray-700 sm:px-4">
              {{ formatDate(doc.end_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>