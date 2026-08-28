
import axios from "axios"


const api = axios.create({
  baseURL:
    "http://127.0.0.1:8000/api/v1",
  timeout: 180000,
})


export async function searchDocuments({
  query,
  mode,
  limit = 10,
  prf = false,
}) {
  const response = await api.get(
    "/search",
    {
      params: {
        q: query,
        mode,
        limit,
        prf,
      },
    }
  )

  return response.data
}


export async function askRag({
  query,
  limit = 3,
}) {
  const response = await api.post(
    "/rag/ask",
    {
      query,
      limit,
    }
  )

  return response.data
}