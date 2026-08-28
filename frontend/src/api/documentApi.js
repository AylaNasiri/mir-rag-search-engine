

import axios from "axios"


const api = axios.create({
  baseURL:
    "http://127.0.0.1:8000/api/v1",
  timeout: 180000,
})


export async function getDocuments() {
  const response = await api.get(
    "/documents"
  )

  return response.data
}


export async function getDocumentDetails(
  documentId
) {
  const response = await api.get(
    `/documents/${documentId}`
  )

  return response.data
}


export async function uploadDocument(
  file
) {
  const formData = new FormData()

  formData.append(
    "file",
    file
  )

  const response = await api.post(
    "/documents/upload",
    formData
  )

  return response.data
}


export async function processDocument(
  documentId
) {
  const response = await api.post(
    `/documents/${documentId}/process`
  )

  return response.data
}


export async function deleteDocument(
  documentId
) {
  await api.delete(
    `/documents/${documentId}`
  )
}