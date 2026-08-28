const algorithms = [
  {
    value: "vsm",
    label: "VSM",
    meta: "TF-IDF",
    description:
      "Classical vector-space lexical ranking",
    icon: "V",
    color:
      "linear-gradient(135deg, #06b6d4, #2563eb)",
  },
  {
    value: "bm25",
    label: "BM25",
    meta: "Lexical",
    description:
      "Probabilistic term-based relevance ranking",
    icon: "B",
    color:
      "linear-gradient(135deg, #2563eb, #4f46e5)",
  },
  {
    value: "semantic",
    label: "Semantic",
    meta: "Embeddings",
    description:
      "Dense-vector meaning-based retrieval",
    icon: "S",
    color:
      "linear-gradient(135deg, #7c3aed, #c026d3)",
  },
  {
    value: "hybrid",
    label: "Hybrid",
    meta: "Fusion",
    description:
      "Lexical and semantic rank fusion",
    icon: "H",
    color:
      "linear-gradient(135deg, #db2777, #f97316)",
  },
  {
    value: "rag",
    label: "Ask AI",
    meta: "RAG",
    description:
      "Grounded answer generation with sources",
    icon: "AI",
    color:
      "linear-gradient(135deg, #10b981, #0891b2)",
  },
]


function AlgorithmSelector({
  value,
  onChange,
}) {
  return (
    <div>
      <p className="app-label">
        Retrieval Strategy
      </p>

      <p className="field-helper">
        Select the retrieval pipeline
        used for this request.
      </p>

      <div
        className="algorithm-grid"
        style={{
          marginTop: "14px",
        }}
      >
        {algorithms.map(
          (algorithm) => {
            const isActive =
              value === algorithm.value

            return (
              <button
                key={algorithm.value}
                type="button"
                onClick={() =>
                  onChange(
                    algorithm.value
                  )
                }
                className={
                  `algorithm-card ${
                    isActive
                      ? "active"
                      : ""
                  }`
                }
              >
                <div
                  className="algorithm-accent"
                  style={{
                    background:
                      algorithm.color,
                  }}
                />

                <div
                  className="algorithm-icon"
                  style={{
                    background:
                      algorithm.color,
                  }}
                >
                  {algorithm.icon}
                </div>

                {isActive && (
                  <div className="algorithm-check">
                    ✓
                  </div>
                )}

                <p className="algorithm-title">
                  {algorithm.label}
                </p>

                <p className="algorithm-meta">
                  {algorithm.meta}
                </p>

                <p className="algorithm-copy">
                  {algorithm.description}
                </p>
              </button>
            )
          }
        )}
      </div>
    </div>
  )
}


export default AlgorithmSelector
