import { reactive } from "vue";
import { fetchCurrentUser } from "../api/auth.js";

/**
 * Глобальное реактивное состояние аутентификации (синглтон).
 * Токены сохраняются в localStorage для persistence между перезагрузками.
 */
const state = reactive({
  token: localStorage.getItem("access_token") || null,
  user: null,
});

export function useAuth() {
  const isAuthenticated = () => !!state.token;

  /**
   * Сохраняет пару токенов (access + refresh) в localStorage и стейте.
   */
  const setTokens = (accessToken, refreshToken) => {
    state.token = accessToken;
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  };

  const logout = () => {
    state.token = null;
    state.user = null;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
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

  return { state, isAuthenticated, setTokens, logout, fetchUser };
}
