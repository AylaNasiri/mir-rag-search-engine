import {
  useEffect,
  useRef,
} from "react"


function UploadBox({
  selectedFile,
  onFileChange,
  onUpload,
  uploading,
}) {
  const fileInputRef =
    useRef(null)


  useEffect(() => {
    if (
      !selectedFile
      && fileInputRef.current
    ) {
      fileInputRef.current.value = ""
    }
  }, [selectedFile])


  function handleFileChange(
    event
  ) {
    const file =
      event.target.files?.[0]

    onFileChange(
      file ?? null
    )
  }


  return (
    <section className="app-panel upload-card upload-card-horizontal">
      <div className="upload-layout">
        <div className="upload-info">
          <div className="upload-header">
            <div className="upload-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                width="23"
                height="23"
                aria-hidden="true"
              >
                <path
                  d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                <path
                  d="M5 14v5h14v-5"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>

            <div>
              <p className="app-eyebrow">
                Corpus Input
              </p>

              <h2
                className="app-section-title"
                style={{
                  marginTop: "3px",
                }}
              >
                Upload Document
              </h2>
            </div>
          </div>

          <p className="app-section-copy">
            Add a text-based PDF or DOCX
            to the searchable corpus.
          </p>
        </div>

        <div className="upload-field-wrap">
          <div
            className="file-drop"
            style={{
              marginTop: 0,
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              disabled={uploading}
              onChange={handleFileChange}
              className="file-input"
            />

            {selectedFile ? (
              <div
                className="app-panel-flat"
                style={{
                  marginTop: "14px",
                  padding: "14px",
                }}
              >
                <p
                  style={{
                    margin: 0,
                    color: "#132238",
                    fontWeight: 700,
                    overflowWrap: "anywhere",
                  }}
                >
                  {selectedFile.name}
                </p>

                <p
                  style={{
                    margin: "6px 0 0",
                    color: "#718196",
                    fontSize: "0.88rem",
                  }}
                >
                  {(
                    selectedFile.size
                    / 1024
                  ).toFixed(1)}
                  {" "}
                  KB selected
                </p>
              </div>
            ) : (
              <p
                style={{
                  margin: "14px 0 0",
                  color: "#7a8a9d",
                  fontSize: "0.9rem",
                  lineHeight: 1.6,
                }}
              >
                Choose a document before uploading.
              </p>
            )}
          </div>
        </div>

        <div className="upload-button-wrap">
          <button
            type="button"
            onClick={onUpload}
            disabled={
              !selectedFile
              || uploading
            }
            className="btn btn-primary"
            style={{
              width: "100%",
              minHeight: "54px",
            }}
          >
            {uploading
              ? "Uploading..."
              : "Upload Document"}
          </button>
        </div>
      </div>
    </section>
  )
}


export default UploadBox
