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


function DetailItem({
  label,
  value,
}) {
  return (
    <div className="detail-item">
      <p className="app-label">
        {label}
      </p>

      <p className="detail-value">
        {value}
      </p>
    </div>
  )
}


function DocumentDetails({
  document,
  loading,
  onClose,
}) {
  const chunks =
    document?.chunks ?? []

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-top">
          <div>
            <p className="app-eyebrow">
              Corpus Inspector
            </p>

            <h2
              className="app-section-title"
              style={{
                marginTop: "4px",
                fontSize: "1.9rem",
              }}
            >
              Document Details
            </h2>

            {document && (
              <p className="app-section-copy">
                {document.filename}
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="btn btn-secondary"
            style={{
              width: "46px",
              minHeight: "46px",
              padding: 0,
              fontSize: "1.25rem",
            }}
            aria-label="Close document details"
          >
            ×
          </button>
        </div>

        {loading && (
          <div
            className="app-panel-flat"
            style={{
              marginTop: "22px",
              padding: "40px",
              textAlign: "center",
              color: "#718196",
            }}
          >
            Loading document details...
          </div>
        )}

        {!loading && document && (
          <>
            <div className="detail-grid">
              <DetailItem
                label="Document ID"
                value={document.id}
              />

              <DetailItem
                label="Status"
                value={
                  document.indexing_status
                }
              />

              <DetailItem
                label="File Type"
                value={document.file_type}
              />

              <DetailItem
                label="File Size"
                value={
                  formatFileSize(
                    document.file_size
                  )
                }
              />

              <DetailItem
                label="Chunks"
                value={
                  document.chunk_count
                }
              />

              <DetailItem
                label="Embeddings"
                value={
                  document.embedding_count
                }
              />

              <DetailItem
                label="Created"
                value={
                  formatDate(
                    document.created_at
                  )
                }
              />

              <DetailItem
                label="Updated"
                value={
                  formatDate(
                    document.updated_at
                  )
                }
              />
            </div>

            <div
              className="detail-item"
              style={{
                marginTop: "12px",
              }}
            >
              <p className="app-label">
                Stored File Path
              </p>

              <p className="detail-value">
                {document.file_path}
              </p>
            </div>

            <div
              style={{
                marginTop: "26px",
              }}
            >
              <div className="app-section-header">
                <div>
                  <p className="app-eyebrow">
                    Indexed Content
                  </p>

                  <h3
                    className="app-section-title"
                    style={{
                      marginTop: "3px",
                    }}
                  >
                    Chunks
                  </h3>
                </div>

                <span className="meta-pill">
                  {chunks.length}
                </span>
              </div>

              {chunks.length === 0 ? (
                <div
                  className="app-panel-flat"
                  style={{
                    padding: "28px",
                    textAlign: "center",
                    color: "#718196",
                  }}
                >
                  This document has no chunks yet.
                </div>
              ) : (
                chunks.map(
                  (chunk) => (
                    <article
                      key={chunk.id}
                      className="chunk-card"
                    >
                      <div className="result-meta">
                        <span className="meta-pill">
                          Chunk #{chunk.chunk_index}
                        </span>

                        <span className="meta-pill">
                          ID {chunk.id}
                        </span>

                        <span className="meta-pill">
                          Tokens {chunk.token_count}
                        </span>

                        <span className="meta-pill">
                          {chunk.has_embedding
                            ? "Embedding ready"
                            : "No embedding"}
                        </span>
                      </div>

                      {chunk.vector_id && (
                        <p
                          style={{
                            margin: "12px 0 0",
                            color: "#7d8c9d",
                            fontSize: "0.84rem",
                            overflowWrap: "anywhere",
                          }}
                        >
                          Vector ID: {chunk.vector_id}
                        </p>
                      )}

                      <div className="chunk-text">
                        {chunk.chunk_text}
                      </div>
                    </article>
                  )
                )
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}


export default DocumentDetails
