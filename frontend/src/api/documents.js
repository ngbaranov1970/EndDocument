import api from "./client.js";

// Подстраивание путей под реальные эндпоинты вашего бэкенда
export const fetchDocuments = async () => {
    const { data } = await api.get("/documents/");
    return data;
};

export const createDocument = async (document) => {
    const { data } = await api.post("/documents/", document);
    return data;
};

