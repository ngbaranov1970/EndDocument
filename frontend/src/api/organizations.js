import api from "./client.js";

/**
 * GET /organizations/
 * Возвращает список активных организаций: [{ id, name, is_active }, ...]
 */
export const fetchOrganizations = async () => {
  const { data } = await api.get("/organizations/");
  return data;
};

/**
 * POST /organizations/
 * Создает новую организацию (или возвращает существующую с тем же именем).
 */
export const createOrganization = async (payload) => {
  const { data } = await api.post("/organizations/", payload);
  return data;
};

/**
 * PUT /organizations/{id}
 * Переименовывает организацию.
 */
export const updateOrganization = async (id, payload) => {
  const { data } = await api.put(`/organizations/${id}`, payload);
  return data;
};

/**
 * DELETE /organizations/{id}
 * Удаляет организацию.
 */
export const deleteOrganization = async (id) => {
  await api.delete(`/organizations/${id}`);
};

