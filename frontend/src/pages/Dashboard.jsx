import {
  useEffect,
  useState,
} from "react"

import {
  Link,
} from "react-router-dom"

import {
  deleteDocument,
  getDocumentDetails,
  getDocuments,
  processDocument,
  uploadDocument,
} from "../api/documentApi"

import DocumentDetails from "../components/admin/DocumentDetails"
import DocumentTable from "../components/admin/DocumentTable"
import UploadBox from "../components/admin/UploadBox"


function Dashboard() {
  const [
    selectedFile,
    setSelectedFile,
  ] = useState(null)

  const [
    documents,
    setDocuments,
  ] = useState([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    uploading,
    setUploading,
  ] = useState(false)

  const [
    processingDocumentId,
    setProcessingDocumentId,
  ] = useState(null)

  const [
    deletingDocumentId,
    setDeletingDocumentId,
  ] = useState(null)

  const [
    detailsDocumentId,
    setDetailsDocumentId,
  ] = useState(null)

  const [
    selectedDocumentDetails,
    setSelectedDocumentDetails,
  ] = useState(null)

  const [
    detailsOpen,
    setDetailsOpen,
  ] = useState(false)

  const [
    detailsLoading,
    setDetailsLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState("")

  const [
    successMessage,
    setSuccessMessage,
  ] = useState("")


  useEffect(() => {
    let cancelled = false

    getDocuments()
      .then((data) => {
        if (!cancelled) {
          setDocuments(data)
        }
      })
      .catch((requestError) => {
        console.error(
          "Failed to load documents:",
          requestError
        )

        if (!cancelled) {
          setError(
            "Failed to load documents."
          )
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])


  async function refreshDocuments() {
    try {
      const data =
        await getDocuments()

      setDocuments(data)
    } catch (requestError) {
      console.error(
        "Failed to refresh documents:",
        requestError
      )

      setError(
        "Failed to refresh documents."
      )
    }
  }


  async function handleUpload() {
    if (!selectedFile) {
      return
    }

    setUploading(true)
    setError("")
    setSuccessMessage("")

    try {
      const uploadedDocument =
        await uploadDocument(
          selectedFile
        )

      setSelectedFile(null)

      setSuccessMessage(
        `"${uploadedDocument.filename}" uploaded successfully.`
      )

      await refreshDocuments()
    } catch (requestError) {
      console.error(
        "Document upload failed:",
        requestError
      )

      const detail =
        requestError.response
          ?.data
          ?.detail

      setError(
        typeof detail === "string"
          ? detail
          : "Document upload failed."
      )
    } finally {
      setUploading(false)
    }
  }


  async function handleProcess(
    documentId
  ) {
    setProcessingDocumentId(
      documentId
    )

    setError("")
    setSuccessMessage("")

    try {
      const result =
        await processDocument(
          documentId
        )

      setSuccessMessage(
        `Document ${result.document_id} indexed successfully with ${result.chunk_count} chunk(s).`
      )

      await refreshDocuments()
    } catch (requestError) {
      console.error(
        "Document processing failed:",
        requestError
      )

      const detail =
        requestError.response
          ?.data
          ?.detail

      setError(
        typeof detail === "string"
          ? detail
          : "Document processing failed."
      )

      await refreshDocuments()
    } finally {
      setProcessingDocumentId(
        null
      )
    }
  }


  async function handleDelete(
    document
  ) {
    const confirmed =
      window.confirm(
        `Delete "${document.filename}"?\n\nThis will permanently remove the document and its indexed data.`
      )

    if (!confirmed) {
      return
    }

    setDeletingDocumentId(
      document.id
    )

    setError("")
    setSuccessMessage("")

    try {
      await deleteDocument(
        document.id
      )

      setSuccessMessage(
        `"${document.filename}" deleted successfully.`
      )

      if (
        selectedDocumentDetails
          ?.id === document.id
      ) {
        setDetailsOpen(false)

        setSelectedDocumentDetails(
          null
        )
      }

      await refreshDocuments()
    } catch (requestError) {
      console.error(
        "Document deletion failed:",
        requestError
      )

      const detail =
        requestError.response
          ?.data
          ?.detail

      setError(
        typeof detail === "string"
          ? detail
          : "Document deletion failed."
      )

      await refreshDocuments()
    } finally {
      setDeletingDocumentId(
        null
      )
    }
  }


  async function handleDetails(
    documentId
  ) {
    setDetailsDocumentId(
      documentId
    )

    setDetailsLoading(true)
    setDetailsOpen(true)

    setSelectedDocumentDetails(
      null
    )

    setError("")

    try {
      const details =
        await getDocumentDetails(
          documentId
        )

      setSelectedDocumentDetails(
        details
      )
    } catch (requestError) {
      console.error(
        "Failed to load document details:",
        requestError
      )

      const detail =
        requestError.response
          ?.data
          ?.detail

      setError(
        typeof detail === "string"
          ? detail
          : "Failed to load document details."
      )

      setDetailsOpen(false)
    } finally {
      setDetailsLoading(false)

      setDetailsDocumentId(
        null
      )
    }
  }


  function handleCloseDetails() {
    setDetailsOpen(false)

    setSelectedDocumentDetails(
      null
    )
  }


  const indexedDocuments =
    documents.filter(
      (document) =>
        document.indexing_status
          ?.toLowerCase()
        === "indexed"
    ).length

  const totalChunks =
    documents.reduce(
      (
        total,
        document
      ) =>
        total
        + (
          document.chunk_count
          ?? 0
        ),
      0
    )


  return (
    <>
      <section className="dashboard-hero">
        <div className="dashboard-hero-copy">
          <div className="hero-badges">
            <span className="hero-badge">
              Corpus Operations
            </span>

            <span className="hero-badge secondary">
              Admin Workspace
            </span>
          </div>

          <h1 className="dashboard-title">
            Manage the corpus
            <span>
              without losing control.
            </span>
          </h1>

          <p className="dashboard-copy">
            Upload files, index documents,
            inspect chunks and embeddings,
            re-index safely, and remove sources
            when they are no longer needed.
          </p>

          <div className="hero-actions">
            <Link
              to="/"
              className="btn btn-primary"
            >
              Open Search →
            </Link>

            <span className="btn btn-light">
              PDF + DOCX · Chunks · Embeddings
            </span>
          </div>
        </div>

        <div className="dashboard-visual">
          <img
            src="/corpus-hero.svg"
            alt="Visual illustration of the document corpus, chunks, embeddings, and indexing pipeline"
          />
        </div>
      </section>

      <section className="app-section">
        <div className="identity-strip">
          <div className="identity-card">
            <p className="app-label">
              Student
            </p>

            <p className="identity-value large">
              Ayla Nasiri
            </p>
          </div>

          <div className="identity-card">
            <p className="app-label">
              Student ID
            </p>

            <p className="identity-value">
              402150071
            </p>
          </div>

          <div className="identity-card">
            <p className="app-label">
              Course
            </p>

            <p className="identity-value">
              Advanced Information Retrieval
            </p>
          </div>

          <div className="identity-card">
            <p className="app-label">
              University
            </p>

            <p className="identity-value">
              Sharif International University of Technology
            </p>
          </div>
        </div>
      </section>

      <section className="stats-grid app-section">
        <div className="stat-card">
          <p className="app-label">
            Corpus Size
          </p>

          <p className="stat-value">
            {documents.length}
          </p>

          <p className="stat-note">
            Total documents
          </p>
        </div>

        <div className="stat-card">
          <p className="app-label">
            Indexed Documents
          </p>

          <p className="stat-value">
            {indexedDocuments}
          </p>

          <p className="stat-note">
            Ready for retrieval
          </p>
        </div>

        <div className="stat-card">
          <p className="app-label">
            Search Units
          </p>

          <p className="stat-value">
            {totalChunks}
          </p>

          <p className="stat-note">
            Total indexed chunks
          </p>
        </div>
      </section>

      {error && (
        <div className="alert error app-section">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert success app-section">
          {successMessage}
        </div>
      )}

      <section className="dashboard-content app-section">
        {loading ? (
          <div
            className="app-panel"
            style={{
              minHeight: "280px",
              display: "grid",
              placeItems: "center",
              color: "#718196",
            }}
          >
            Loading documents...
          </div>
        ) : (
          <DocumentTable
            documents={documents}
            onProcess={handleProcess}
            onDelete={handleDelete}
            onDetails={handleDetails}
            processingDocumentId={
              processingDocumentId
            }
            deletingDocumentId={
              deletingDocumentId
            }
            detailsDocumentId={
              detailsDocumentId
            }
          />
        )}

        <UploadBox
          selectedFile={selectedFile}
          onFileChange={setSelectedFile}
          onUpload={handleUpload}
          uploading={uploading}
        />
      </section>

      {detailsOpen && (
        <DocumentDetails
          document={
            selectedDocumentDetails
          }
          loading={detailsLoading}
          onClose={handleCloseDetails}
        />
      )}
    </>
  )
}


export default Dashboard
