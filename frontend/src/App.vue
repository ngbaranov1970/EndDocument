<script setup>
import { onMounted, ref } from "vue";
import { fetchDocuments } from "./api/documents.js";

const documents = ref([]);
const loading = ref(false);
const error = ref("");

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
  <main class="mx-auto max-w-3xl p-6">
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

    <ul v-else class="space-y-3">
      <li
        v-for="doc in documents"
        :key="doc.id ?? doc.title"
        class="rounded-xl border p-4 shadow-sm"
      >
        <h2 class="font-semibold">{{ doc.user_name ?? "Без названия" }}</h2>
        <p class="mt-1 text-sm text-gray-700">{{ doc.organization_name ?? "Нет содержимого" }}</p>

        <p v-if="doc.created_at" class="mt-2 text-xs text-gray-400">
          Создан: {{ doc.created_at }}
        </p>
      </li>
    </ul>
  </main>
</template>