export async function uploadPDF(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch("http://localhost:5000/api/documents/upload", {
    method: "POST",
    body: form
  });

  return res.json();
}
