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

