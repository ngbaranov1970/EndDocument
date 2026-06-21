import api from "./client.js";

/**
 * Возвращает список всех пользователей (только для суперпользователей).
 */
export const fetchAllUsers = async () => {
  const res = await api.get("/users/admin/list");
  return res.data;
};

/**
 * Активирует пользователя по id.
 */
export const activateUser = async (userId) => {
  const res = await api.patch(`/users/admin/${userId}/activate`);
  return res.data;
};

/**
 * Деактивирует пользователя по id.
 */
export const deactivateUser = async (userId) => {
  const res = await api.patch(`/users/admin/${userId}/deactivate`);
  return res.data;
};
