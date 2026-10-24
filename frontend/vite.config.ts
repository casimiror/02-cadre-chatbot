import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // In dev the UI runs on :5173 and forwards API calls to FastAPI; in prod FastAPI serves dist/.
  server: { proxy: { "/api": "http://localhost:8000" } },
});
