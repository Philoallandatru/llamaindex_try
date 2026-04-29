import { Workflow, StartEvent, StopEvent } from "@llamaindex/workflow";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

// Simple workflow that calls Python backend
export const workflow = async (input: { message: string }) => {
  console.log(`[WORKFLOW] Received query: ${input.message}`);

  try {
    console.log(`[WORKFLOW] Calling Python API: ${PYTHON_API_URL}/api/chat`);

    const response = await fetch(`${PYTHON_API_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: input.message,
        session_id: "default",
      }),
    });

    if (!response.ok) {
      throw new Error(
        `Python API error: ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();
    console.log(`[WORKFLOW] Received response from Python API`);

    return {
      message: data.response || data.message || "No response from backend",
    };
  } catch (error) {
    console.error("[WORKFLOW] Error calling Python API:", error);
    return {
      message: `Error: Unable to connect to Python backend at ${PYTHON_API_URL}. Please ensure the FastAPI server is running on port 8000.`,
    };
  }
};
