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

export const updateDocument = async (documentId, document) => {
    const { data } = await api.put(`/documents/${documentId}`, document);
    return data;
};

export const archiveDocument = async (documentId) => {
    const { data } = await api.put(`/documents/${documentId}/archive`);
    return data;
};

export const fetchArchivedDocuments = async () => {
    const { data } = await api.get("/documents/archived");
    return data;
};

export const restoreDocument = async (documentId) => {
    const { data } = await api.put(`/documents/${documentId}/restore`);
    return data;
};
