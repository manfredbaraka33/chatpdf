import axios from "axios";

const API_URL = "https://chatpdf-production.up.railway.app";

export const uploadPDFs = (files) => {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  return axios.post(`${API_URL}/upload/`, formData);
};

export const askQuestion = (query) => {
  return axios.post(`${API_URL}/ask/`, { query });
};
