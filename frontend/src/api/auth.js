import api from "./client.js";

/**
 * Аутентификация пользователя.
 * Возвращает { access_token, token_type }.
 */
export const loginUser = async (username, password) => {
  const res = await api.post("/users/login", { username, password });
  return res.data;
};

/**
 * Регистрация нового пользователя.
 * Возвращает объект созданного пользователя.
 */
export const registerUser = async (username, password, email) => {
  const res = await api.post("/users/", { username, password, email });
  return res.data;
};

/**
 * Получение данных текущего пользователя (требует токен).
 */
export const fetchCurrentUser = async () => {
  const res = await api.get("/users/me");
  return res.data;
};
