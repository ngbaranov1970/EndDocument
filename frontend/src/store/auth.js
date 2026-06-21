import { reactive } from "vue";
import { fetchCurrentUser } from "../api/auth.js";

/**
 * Глобальное реактивное состояние аутентификации (синглтон).
 * Токен сохраняется в localStorage для persistence между перезагрузками.
 */
const state = reactive({
  token: localStorage.getItem("access_token") || null,
  user: null,
});

export function useAuth() {
  const isAuthenticated = () => !!state.token;

  const setToken = (token) => {
    state.token = token;
    localStorage.setItem("access_token", token);
  };

  const logout = () => {
    state.token = null;
    state.user = null;
    localStorage.removeItem("access_token");
  };

  /**
   * Загружает данные текущего пользователя.
   * При ошибке (просроченный или невалидный токен) выполняет logout.
   */
  const fetchUser = async () => {
    if (!state.token) return;
    try {
      state.user = await fetchCurrentUser();
    } catch {
      logout();
    }
  };

  return { state, isAuthenticated, setToken, logout, fetchUser };
}
