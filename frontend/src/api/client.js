import axios from "axios";
import { refreshTokens } from "./auth.js";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Флаг для предотвращения одновременных попыток рефреша
let isRefreshing = false;
let failedQueue = [];

/** Обрабатывает очередь запросов, ожидавших рефреш */
const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  failedQueue = [];
};

// Добавляет JWT-токен в заголовок Authorization при каждом запросе
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Автоматически обновляет access-токен при 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Рефрешим только если 401 и это не сам запрос рефреша или логина
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/users/login") &&
      !originalRequest.url?.includes("/users/refresh")
    ) {
      if (isRefreshing) {
        // Если уже идёт рефреш, ставим запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedRefresh = localStorage.getItem("refresh_token");
      if (!storedRefresh) {
        // Нет refresh-токена — просто проваливаемся
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const data = await refreshTokens(storedRefresh);
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);

        processQueue(null, data.access_token);

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        // Можно сделать редирект на логин через window.location,
        // но лучше через роутер — поэтому просто пробрасываем ошибку
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default api;