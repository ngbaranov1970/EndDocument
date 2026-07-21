<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import {
  createOrganization,
  deleteOrganization,
  fetchOrganizations,
  updateOrganization,
} from "../api/organizations.js";

const router = useRouter();

const form = reactive({
  name: "",
});

const submitting = ref(false);
const submitError = ref("");
const successMessage = ref("");

const handleSubmit = async () => {
  submitError.value = "";
  successMessage.value = "";

  const name = form.name.trim();
  if (name.length < 3) {
    submitError.value = "Название организации должно содержать минимум 3 символа";
    return;
  }

  submitting.value = true;
  try {
    const organization = await createOrganization({ name });
    successMessage.value = `Организация \"${organization.name}\" сохранена`;
    form.name = "";
    await loadOrganizations();
  } catch (e) {
    submitError.value =
      e?.response?.data?.detail || e?.message || "Не удалось сохранить организацию";
  } finally {
    submitting.value = false;
  }
};

// Список существующих организаций и состояние их переименования/удаления
const organizations = ref([]);
const loading = ref(false);
const listError = ref("");

const editingId = ref(null); // id организации, которую сейчас переименовываем
const editingName = ref("");
const savingId = ref(null); // id организации, для которой идёт запрос сохранения/удаления

const loadOrganizations = async () => {
  loading.value = true;
  listError.value = "";
  try {
    organizations.value = await fetchOrganizations();
  } catch (e) {
    listError.value =
      e?.response?.data?.detail || e?.message || "Не удалось загрузить организации";
  } finally {
    loading.value = false;
  }
};

const startEdit = (organization) => {
  editingId.value = organization.id;
  editingName.value = organization.name;
};

const cancelEdit = () => {
  editingId.value = null;
  editingName.value = "";
};

const saveEdit = async (organization) => {
  const name = editingName.value.trim();
  if (name.length < 3) {
    listError.value = "Название организации должно содержать минимум 3 символа";
    return;
  }

  savingId.value = organization.id;
  listError.value = "";
  try {
    const updated = await updateOrganization(organization.id, { name });
    const idx = organizations.value.findIndex((o) => o.id === organization.id);
    if (idx !== -1) organizations.value[idx] = updated;
    cancelEdit();
  } catch (e) {
    listError.value =
      e?.response?.data?.detail || e?.message || "Не удалось переименовать организацию";
  } finally {
    savingId.value = null;
  }
};

const handleDelete = async (organization) => {
  if (!confirm(`Удалить организацию \"${organization.name}\"?`)) return;

  savingId.value = organization.id;
  listError.value = "";
  try {
    await deleteOrganization(organization.id);
    organizations.value = organizations.value.filter((o) => o.id !== organization.id);
  } catch (e) {
    listError.value =
      e?.response?.data?.detail || e?.message || "Не удалось удалить организацию";
  } finally {
    savingId.value = null;
  }
};

onMounted(loadOrganizations);
</script>

<template>
  <main class="mx-auto max-w-lg px-4 py-6">
    <h1 class="mb-6 text-2xl font-bold">Организации</h1>

    <form
      @submit.prevent="handleSubmit"
      class="mb-8 flex flex-col gap-5 rounded-xl border bg-white p-6 shadow-sm"
    >
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Название организации</label>
        <input
          v-model="form.name"
          type="text"
          minlength="3"
          maxlength="255"
          placeholder="ООО Ромашка"
          required
          class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
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
          @click="router.push('/create')"
          class="rounded-lg border px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
        >
          К документу
        </button>

        <button
          type="submit"
          :disabled="submitting"
          class="rounded-lg bg-black px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
        >
          {{ submitting ? "Сохранение..." : "Сохранить" }}
        </button>
      </div>
    </form>

    <!-- Список существующих организаций: переименование и удаление -->
    <div class="rounded-xl border bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">Список организаций</h2>
        <button
          @click="loadOrganizations"
          :disabled="loading"
          class="rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50"
        >
          {{ loading ? "Загрузка..." : "Обновить" }}
        </button>
      </div>

      <p
        v-if="listError"
        class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
      >
        {{ listError }}
      </p>

      <p v-if="loading" class="text-sm text-gray-500">Загрузка...</p>

      <p v-else-if="!organizations.length" class="text-sm text-gray-500">
        Организаций пока нет
      </p>

      <ul v-else class="divide-y">
        <li
          v-for="organization in organizations"
          :key="organization.id"
          class="flex items-center gap-3 py-3"
        >
          <template v-if="editingId === organization.id">
            <input
              v-model="editingName"
              type="text"
              minlength="3"
              maxlength="255"
              class="flex-1 rounded-lg border px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-black"
              @keyup.enter="saveEdit(organization)"
              @keyup.escape="cancelEdit"
            />
            <button
              @click="saveEdit(organization)"
              :disabled="savingId === organization.id"
              class="rounded-lg bg-black px-3 py-1.5 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              {{ savingId === organization.id ? "..." : "Сохранить" }}
            </button>
            <button
              @click="cancelEdit"
              :disabled="savingId === organization.id"
              class="rounded-lg border px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
            >
              Отмена
            </button>
          </template>

          <template v-else>
            <span class="flex-1 truncate text-sm text-gray-900">{{ organization.name }}</span>
            <button
              @click="startEdit(organization)"
              :disabled="savingId === organization.id"
              class="rounded-lg border px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50"
            >
              Переименовать
            </button>
            <button
              @click="handleDelete(organization)"
              :disabled="savingId === organization.id"
              class="rounded-lg border border-red-300 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 disabled:opacity-50"
            >
              {{ savingId === organization.id ? "..." : "Удалить" }}
            </button>
          </template>
        </li>
      </ul>
    </div>
  </main>
</template>
