<template>
  <!-- Общая обёртка приложения: шапка + контент -->
  <div class="min-h-screen bg-gray-50">

    <!-- Навигационная панель -->
    <nav class="border-b bg-white shadow-sm">
      <div class="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <span class="text-lg font-bold tracking-tight">📄 EndDocument</span>

        <div class="flex gap-3">
          <!-- RouterLink не перезагружает страницу, как обычный <a> -->
          <RouterLink
            to="/"
            class="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
            active-class="bg-gray-100"
          >
            Список
          </RouterLink>

          <RouterLink
            to="/create"
            class="rounded-lg bg-black px-3 py-1.5 text-sm font-medium text-white hover:opacity-90"
            active-class="opacity-80"
          >
            + Создать
          </RouterLink>

          <RouterLink
            to="/organizations/create"
            class="rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100"
            active-class="bg-gray-100"
          >
            + Организация
          </RouterLink>
        </div>
      </div>
    </nav>

    <!-- Сюда роутер подставляет нужный компонент (HomeView или CreateDocumentView) -->
    <RouterView />

  </div>
</template>