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

// Поля формы — reactive-объект (удобнее, чем несколько ref)
const form = reactive({
  organization_id: "",   // строка из <select>, конвертируем в Number перед отправкой
  user_name: "",
  start_at: "",          // формат YYYY-MM-DD (нативный <input type="date">)
  end_at: "",
});

// Состояния отправки
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
 * Отправка формы.
 * Бэк ожидает: { organization_id: int, user_name: str, start_at: date, end_at: date }
 */
const handleSubmit = async () => {
  submitError.value = "";
  successMessage.value = "";

  // Простая валидация на стороне клиента
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
    await createDocument({
      organization_id: Number(form.organization_id), // <select> отдаёт строку — конвертируем
      user_name: form.user_name.trim(),
      start_at: form.start_at,
      end_at: form.end_at,
    });

    successMessage.value = "Документ успешно создан!";

    // Через 1.5 секунды переходим на главную страницу со списком
    setTimeout(() => router.push("/"), 1500);
  } catch (e) {
    submitError.value =
      e?.response?.data?.detail || e?.message || "Ошибка при создании документа";
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <main class="mx-auto max-w-lg px-4 py-6">
    <h1 class="mb-6 text-2xl font-bold">Создать документ</h1>

    <!-- Форма -->
    <form
      @submit.prevent="handleSubmit"
      class="flex flex-col gap-5 rounded-xl border bg-white p-6 shadow-sm"
    >

      <!-- Организация -->
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Организация</label>

        <p v-if="orgsLoading" class="text-sm text-gray-400">Загрузка...</p>
        <p v-else-if="orgsError" class="text-sm text-red-600">{{ orgsError }}</p>
        <p v-else-if="organizations.length === 0" class="text-sm text-amber-700">
          Нет активных организаций.
          <RouterLink to="/organizations/create" class="underline hover:no-underline">
            Добавить организацию
          </RouterLink>
        </p>

        <!--
          v-model привязывает выбранное значение к form.organization_id.
          Значение <option> — это строка "1", "2" и т.д.
          Конвертация в Number происходит в handleSubmit.
        -->
        <select
          v-else
          v-model="form.organization_id"
          required
          class="rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
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
        <RouterLink
          v-if="!orgsLoading && !orgsError"
          to="/organizations/create"
          class="w-fit text-xs text-gray-500 underline hover:text-gray-700 hover:no-underline"
        >
          + Добавить организацию
        </RouterLink>
      </div>

      <!-- Ф.И.О. работника -->
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

      <!-- Даты — два поля в ряд -->
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

      <!-- Сообщение об ошибке -->
      <p
        v-if="submitError"
        class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
      >
        {{ submitError }}
      </p>

      <!-- Сообщение об успехе -->
      <p
        v-if="successMessage"
        class="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700"
      >
        {{ successMessage }}
      </p>

      <!-- Кнопки -->
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
          :disabled="submitting || orgsLoading"
          class="rounded-lg bg-black px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
        >
          {{ submitting ? "Сохранение..." : "Создать" }}
        </button>
      </div>

    </form>
  </main>
</template>

