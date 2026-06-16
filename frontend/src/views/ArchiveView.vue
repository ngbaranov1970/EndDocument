<script setup>
import { onMounted, ref } from "vue";
import { fetchArchivedDocuments, restoreDocument } from "../api/documents.js";

const groups = ref([]);
const loading = ref(false);
const error = ref("");
const restoringId = ref(null);

const formatDate = (value) => {
  if (!value) return "-";
  const source = String(value);

  if (source.includes("-")) {
    const [year, month, day] = source.slice(0, 10).split("-");
    if (year && month && day) return `${day}.${month}.${year}`;
  }

  return source;
};

const loadArchivedDocuments = async () => {
  loading.value = true;
  error.value = "";

  try {
    const data = await fetchArchivedDocuments();
    groups.value = Array.isArray(data) ? data : data ? [data] : [];
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      e?.message ||
      "Не удалось загрузить архивные документы";
  } finally {
    loading.value = false;
  }
};

const handleRestore = async (docId) => {
  if (!confirm("Вернуть документ из архива?")) return;

  restoringId.value = docId;
  try {
    await restoreDocument(docId);
    await loadArchivedDocuments();
  } catch (e) {
    alert(e?.response?.data?.detail || "Не удалось вернуть документ из архива");
  } finally {
    restoringId.value = null;
  }
};

onMounted(loadArchivedDocuments);
</script>

<template>
  <main class="mx-auto max-w-4xl px-2 py-6 sm:px-4">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold">Архив документов</h1>
      <button
        @click="loadArchivedDocuments"
        :disabled="loading"
        class="rounded-lg bg-black px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
      >
        {{ loading ? "Загрузка..." : "Обновить" }}
      </button>
    </div>

    <p v-if="loading" class="text-gray-500">Загрузка...</p>

    <p
      v-else-if="error"
      class="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700"
    >
      {{ error }}
    </p>

    <p v-else-if="groups.length === 0" class="text-gray-500">
      Архив пуст
    </p>

    <div v-else class="flex flex-col gap-6">
      <div
        v-for="group in groups"
        :key="group.organization_id"
        class="overflow-x-auto rounded-xl border shadow-sm"
      >
        <div class="border-b bg-gray-50 px-4 py-2 text-sm">
          <span class="font-semibold text-gray-800">{{ group.organization_name }}</span>
          <span class="ml-2 text-xs text-gray-400">ID {{ group.organization_id }}</span>
        </div>

        <table class="min-w-full table-fixed border-collapse text-sm">
          <colgroup>
            <col class="w-[44%]" />
            <col class="w-[18%]" />
            <col class="w-[18%]" />
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
            <tr v-for="doc in group.documents" :key="doc.id" class="hover:bg-gray-50">
              <td class="truncate px-4 py-3 font-medium text-gray-900">
                {{ doc.user_name ?? "-" }}
              </td>
              <td class="whitespace-nowrap px-4 py-3 text-gray-700">
                {{ formatDate(doc.start_at) }}
              </td>
              <td class="whitespace-nowrap px-4 py-3 text-gray-700">
                {{ formatDate(doc.end_at) }}
              </td>
              <td class="px-4 py-3">
                <button
                  @click="handleRestore(doc.id)"
                  :disabled="restoringId === doc.id"
                  class="inline-flex rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100 disabled:opacity-50"
                >
                  {{ restoringId === doc.id ? "..." : "Восстановить" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</template>

