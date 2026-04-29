import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "../public")));

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok", pythonBackend: PYTHON_API_URL });
});

// Proxy chat requests to Python backend
app.post("/api/chat", async (req, res) => {
  try {
    const { message, session_id = "default" } = req.body;

    console.log(`[PROXY] Forwarding chat request to Python backend`);

    const response = await fetch(`${PYTHON_API_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message, session_id }),
    });

    if (!response.ok) {
      throw new Error(`Python API error: ${response.status}`);
    }

    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error("[PROXY] Error:", error);
    res.status(500).json({
      error: "Failed to connect to Python backend",
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

app.listen(PORT, () => {
  console.log(`\n🚀 Server running on http://localhost:${PORT}`);
  console.log(`📡 Python backend: ${PYTHON_API_URL}`);
  console.log(`\n✨ Open http://localhost:${PORT} in your browser\n`);
});
