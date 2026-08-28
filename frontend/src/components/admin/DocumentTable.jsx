function formatFileSize(bytes) {
  if (
    bytes === null
    || bytes === undefined
  ) {
    return "-"
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  const kilobytes =
    bytes / 1024

  if (kilobytes < 1024) {
    return `${kilobytes.toFixed(1)} KB`
  }

  return `${(
    kilobytes / 1024
  ).toFixed(2)} MB`
}


function formatDate(value) {
  if (!value) {
    return "-"
  }

  return new Date(
    value
  ).toLocaleString()
}


function StatusBadge({
  status,
}) {
  const normalized =
    status?.toLowerCase()

  return (
    <span
      className={
        `status ${
          normalized
          || ""
        }`
      }
    >
      {status}
    </span>
  )
}


function DocumentTable({
  documents,
  onProcess,
  onDelete,
  onDetails,
  processingDocumentId,
  deletingDocumentId,
  detailsDocumentId,
}) {
  return (
    <section className="app-panel table-card">
      <div className="table-head">
        <div>
          <p className="app-eyebrow">
            Search Corpus
          </p>

          <h2
            className="app-section-title"
            style={{
              marginTop: "4px",
            }}
          >
            Document Library
          </h2>

          <p className="app-section-copy">
            Inspect and manage every indexed source.
          </p>
        </div>

        <span className="meta-pill">
          {documents.length}
          {" "}
          document
          {documents.length === 1
            ? ""
            : "s"}
        </span>
      </div>

      <div className="table-scroll">
        <table className="doc-table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Type</th>
              <th>Size</th>
              <th>Chunks</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {documents.map(
              (document) => {
                const isProcessing =
                  processingDocumentId
                  === document.id

                const isDeleting =
                  deletingDocumentId
                  === document.id

                const isLoadingDetails =
                  detailsDocumentId
                  === document.id

                const isBusy =
                  isProcessing
                  || isDeleting
                  || isLoadingDetails

                return (
                  <tr key={document.id}>
                    <td>
                      <div className="doc-main">
                        <div className="doc-icon">
                          {
                            document
                              .file_type
                              ?.slice(0, 1)
                              ?.toUpperCase()
                          }
                        </div>

                        <div>
                          <div className="doc-title">
                            {document.title}
                          </div>

                          <div className="doc-file">
                            {document.filename}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td>
                      {document.file_type}
                    </td>

                    <td>
                      {formatFileSize(
                        document.file_size
                      )}
                    </td>

                    <td>
                      <strong>
                        {document.chunk_count ?? 0}
                      </strong>
                    </td>

                    <td>
                      <StatusBadge
                        status={
                          document.indexing_status
                        }
                      />
                    </td>

                    <td>
                      {formatDate(
                        document.created_at
                      )}
                    </td>

                    <td>
                      <div className="action-row">
                        <button
                          type="button"
                          onClick={() =>
                            onDetails(
                              document.id
                            )
                          }
                          disabled={isBusy}
                          className="btn btn-secondary"
                          style={{
                            minHeight: "39px",
                            padding: "0 12px",
                          }}
                        >
                          {isLoadingDetails
                            ? "Loading..."
                            : "Details"}
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            onProcess(
                              document.id
                            )
                          }
                          disabled={isBusy}
                          className="btn btn-primary"
                          style={{
                            minHeight: "39px",
                            padding: "0 12px",
                          }}
                        >
                          {isProcessing
                            ? "Processing..."
                            : document
                                  .indexing_status ===
                              "indexed"
                              ? "Re-index"
                              : "Process"}
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            onDelete(
                              document
                            )
                          }
                          disabled={isBusy}
                          className="btn btn-danger"
                          style={{
                            minHeight: "39px",
                            padding: "0 12px",
                          }}
                        >
                          {isDeleting
                            ? "Deleting..."
                            : "Delete"}
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              }
            )}
          </tbody>
        </table>
      </div>

      {documents.length === 0 && (
        <div
          style={{
            padding: "34px",
            textAlign: "center",
          }}
        >
          <p
            style={{
              margin: 0,
              color: "#405268",
              fontWeight: 700,
            }}
          >
            No documents available.
          </p>

          <p
            style={{
              margin: "7px 0 0",
              color: "#7a899b",
              fontSize: "0.9rem",
            }}
          >
            Upload a PDF or DOCX to start
            building the corpus.
          </p>
        </div>
      )}
    </section>
  )
}


export default DocumentTable
