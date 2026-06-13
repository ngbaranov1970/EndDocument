<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchDocuments, updateDocument } from "../api/documents.js";
import { fetchOrganizations } from "../api/organizations.js";

const route = useRoute();
const router = useRouter();

const documentId = Number(route.params.document_id);

const organizations = ref([]);
const loading = ref(false);
const submitError = ref("");
const formError = ref("");
const successMessage = ref("");
const submitting = ref(false);

const form = reactive({
  organization_id: "",
  user_name: "",
  start_at: "",
  end_at: "",
});

const normalizeDate = (value) => {
  if (!value) return "";
  return String(value).slice(0, 10);
};

const loadDocument = async () => {
  if (Number.isNaN(documentId) || documentId <= 0) {
    formError.value = "Некорректный идентификатор документа";
    return;
  }

  loading.value = true;
  formError.value = "";
  submitError.value = "";

  try {
    const [orgsData, documentsData] = await Promise.all([
      fetchOrganizations(),
      fetchDocuments(),
    ]);

    organizations.value = Array.isArray(orgsData) ? orgsData : [];

    const groups = Array.isArray(documentsData) ? documentsData : [];
    let foundDocument = null;
    let foundOrganization = null;

    for (const group of groups) {
      const document = (group?.documents || []).find(
        (item) => Number(item.id) === documentId,
      );
      if (document) {
        foundDocument = document;
        foundOrganization = {
          id: group.organization_id,
          name: group.organization_name,
        };
        break;
      }
    }

    if (!foundDocument) {
      formError.value = `Документ с id=${documentId} не найден`;
      return;
    }

    if (
      foundOrganization &&
      !organizations.value.some(
        (org) => Number(org.id) === Number(foundOrganization.id),
      )
    ) {
      organizations.value = [...organizations.value, foundOrganization];
    }

    form.organization_id = String(foundDocument.organization_id);
    form.user_name = foundDocument.user_name ?? "";
    form.start_at = normalizeDate(foundDocument.start_at);
    form.end_at = normalizeDate(foundDocument.end_at);
  } catch (e) {
    formError.value =
      e?.response?.data?.detail || e?.message || "Не удалось загрузить документ";
  } finally {
    loading.value = false;
  }
};

onMounted(loadDocument);

const handleSubmit = async () => {
  submitError.value = "";
  successMessage.value = "";

  if (!form.organization_id) {
    submitError.value = "Выберите организацию";
    return;
  }
  if (form.user_name.trim().length < 3) {
    submitError.value = "Ф.И.О. должно содержать не менее 3 символов";
    return;
  }
  if (!form.start_at || !form.end_at) {
    submitError.value = "Укажите даты начала и окончания работ";
    return;
  }
  if (form.start_at > form.end_at) {
    submitError.value = "Дата начала не может быть позже даты окончания";
    return;
  }

  submitting.value = true;
  try {
    await updateDocument(documentId, {
      organization_id: Number(form.organization_id),
      user_name: form.user_name.trim(),
      start_at: form.start_at,
      end_at: form.end_at,
    });

    successMessage.value = "Документ успешно обновлён!";
    setTimeout(() => router.push("/"), 1500);
  } catch (e) {
    submitError.value =
      e?.response?.data?.detail || e?.message || "Ошибка при обновлении документа";
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <main class="mx-auto max-w-lg px-4 py-6">
    <h1 class="mb-6 text-2xl font-bold">Редактировать документ</h1>

    <form
      @submit.prevent="handleSubmit"
      class="flex flex-col gap-5 rounded-xl border bg-white p-6 shadow-sm"
    >
      <p v-if="loading" class="text-sm text-gray-500">Загрузка документа...</p>
      <p
        v-else-if="formError"
        class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
      >
        {{ formError }}
      </p>

      <template v-else>
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">Организация</label>
          <select
            v-model="form.organization_id"
            required
            class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
          >
            <option value="" disabled>Выберите организацию...</option>
            <option v-for="org in organizations" :key="org.id" :value="org.id">
              {{ org.name }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">Ф.И.О. работника</label>
          <input
            v-model="form.user_name"
            type="text"
            placeholder="Иванов Иван Иванович"
            minlength="3"
            maxlength="255"
            required
            class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-gray-700">Дата начала работ</label>
            <input
              v-model="form.start_at"
              type="date"
              required
              class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>

          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-gray-700">Дата окончания работ</label>
            <input
              v-model="form.end_at"
              type="date"
              required
              class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
        </div>

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

        <div class="flex justify-end gap-3">
          <button
            type="button"
            @click="router.push('/')"
            class="rounded-lg border px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Отмена
          </button>

          <button
            type="submit"
            :disabled="submitting"
            class="rounded-lg bg-black px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
          >
            {{ submitting ? "Сохранение..." : "Сохранить" }}
          </button>
        </div>
      </template>
    </form>
  </main>
</template>

