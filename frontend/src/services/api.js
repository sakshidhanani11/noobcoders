// api.js
import axios from "axios";
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function postReading(payload) {
  return axios.post(`${API_BASE}/ingest/reading`, payload);
}

export async function getAlerts() {
  return axios.get(`${API_BASE}/alerts`);
}
