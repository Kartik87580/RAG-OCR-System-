import { API_BASE_URL } from "./config";

export async function askQuestion(question) {
  const res = await fetch(`${API_BASE_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });


  return res.json();
}
