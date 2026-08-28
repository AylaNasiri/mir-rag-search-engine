function RagAnswer({
  answer,
  sources,
}) {
  return (
    <div className="results-stack">
      <section className="rag-answer">
        <p
          className="app-eyebrow"
          style={{
            color: "#8de8f2",
          }}
        >
          Grounded Generation
        </p>

        <h2 className="rag-title">
          AI Generated Answer
        </h2>

        <div className="rag-copy">
          {answer}
        </div>
      </section>

      {sources.length > 0 ? (
        <section>
          <div className="app-section-header">
            <div>
              <p className="app-eyebrow">
                Evidence
              </p>

              <h2 className="app-section-title">
                Retrieved Sources
              </h2>
            </div>

            <span className="meta-pill">
              {sources.length} retrieved
            </span>
          </div>

          <div className="results-stack">
            {sources.map(
              (
                source,
                index
              ) => {
                const formattedScore =
                  typeof source.score === "number"
                    ? source.score.toFixed(4)
                    : source.score ?? "-"

                return (
                  <article
                    key={
                      `${source.document_id}-${source.chunk_id}-${index}`
                    }
                    className="source-card"
                  >
                    <div className="result-head">
                      <div className="result-title-wrap">
                        <div className="rank-badge">
                          {index + 1}
                        </div>

                        <div>
                          <p className="app-label">
                            Source {index + 1}
                          </p>

                          <h3 className="result-title">
                            {source.document_title}
                          </h3>

                          <p className="result-filename">
                            {source.filename}
                          </p>
                        </div>
                      </div>

                      <div className="score-box">
                        <p className="app-label">
                          Score
                        </p>

                        <p className="score-value">
                          {formattedScore}
                        </p>
                      </div>
                    </div>

                    {source.chunk_text && (
                      <div className="result-text">
                        {source.chunk_text}
                      </div>
                    )}

                    <div className="result-meta">
                      <span className="meta-pill">
                        Document #{source.document_id}
                      </span>

                      <span className="meta-pill">
                        Chunk #{source.chunk_id}
                      </span>

                      <span className="meta-pill">
                        Index {source.chunk_index}
                      </span>
                    </div>
                  </article>
                )
              }
            )}
          </div>
        </section>
      ) : (
        <div className="app-panel-flat">
          <p
            className="app-body"
            style={{
              padding: "20px",
              margin: 0,
            }}
          >
            No document sources were used.
          </p>
        </div>
      )}
    </div>
  )
}


export default RagAnswer
