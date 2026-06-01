<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { createOrganization } from "../api/organizations.js";

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

    // Удобный сценарий: после добавления организации перейти к созданию документа.
    setTimeout(() => {
      router.push("/create");
    }, 1200);
  } catch (e) {
    submitError.value =
      e?.response?.data?.detail || e?.message || "Не удалось сохранить организацию";
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <main class="mx-auto max-w-lg px-4 py-6">
    <h1 class="mb-6 text-2xl font-bold">Добавить организацию</h1>

    <form
      @submit.prevent="handleSubmit"
      class="flex flex-col gap-5 rounded-xl border bg-white p-6 shadow-sm"
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
  </main>
</template>

