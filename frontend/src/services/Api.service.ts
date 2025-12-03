import axios from "axios";

const baseURL = "http://localhost:8000";

export const api = axios.create({
  baseURL,
  validateStatus: (status) => status >= 200 && status <= 500,
});
