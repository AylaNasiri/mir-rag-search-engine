const STOPWORDS = new Set([
  "a",
  "an",
  "and",
  "are",
  "as",
  "at",
  "be",
  "by",
  "for",
  "from",
  "has",
  "he",
  "in",
  "is",
  "it",
  "its",
  "of",
  "on",
  "that",
  "the",
  "to",
  "was",
  "were",
  "will",
  "with",
])


function escapeRegExp(value) {
  return value.replace(
    /[.*+?^${}()|[\]\\]/g,
    "\\$&"
  )
}


function getHighlightTerms(query) {
  if (!query) {
    return []
  }

  const matches =
    query
      .toLowerCase()
      .match(/[a-z0-9-]+/g)
      ?? []

  return [
    ...new Set(
      matches.filter(
        (term) =>
          term.length > 0
          && !STOPWORDS.has(term)
      )
    ),
  ].sort(
    (first, second) =>
      second.length
      - first.length
  )
}


function HighlightedText({
  text,
  query,
}) {
  const terms =
    getHighlightTerms(query)

  if (
    !text
    || terms.length === 0
  ) {
    return text
  }

  const pattern =
    new RegExp(
      `\\b(${terms
        .map(escapeRegExp)
        .join("|")})\\b`,
      "gi"
    )

  const termSet =
    new Set(
      terms.map(
        (term) =>
          term.toLowerCase()
      )
    )

  return text
    .split(pattern)
    .map(
      (part, index) => {
        const normalizedPart =
          part.toLowerCase()

        if (
          termSet.has(
            normalizedPart
          )
        ) {
          return (
            <mark
              key={
                `${index}-${part}`
              }
            >
              {part}
            </mark>
          )
        }

        return (
          <span
            key={
              `${index}-${part}`
            }
          >
            {part}
          </span>
        )
      }
    )
}


function ResultCard({
  result,
  rank,
  highlightQuery = "",
}) {
  const formattedScore =
    typeof result.score === "number"
      ? result.score.toFixed(4)
      : result.score

  return (
    <article
      className={
        `result-card ${
          rank === 1
            ? "top"
            : ""
        }`
      }
    >
      <div className="result-line" />

      <div className="result-head">
        <div className="result-title-wrap">
          <div className="rank-badge">
            #{rank}
          </div>

          <div>
            <h3 className="result-title">
              {result.document_title}
            </h3>

            <p className="result-filename">
              {result.filename}
            </p>
          </div>
        </div>

        <div className="score-box">
          <p className="app-label">
            Relevance
          </p>

          <p className="score-value">
            {formattedScore}
          </p>
        </div>
      </div>

      <div className="result-text">
        <HighlightedText
          text={result.chunk_text}
          query={highlightQuery}
        />
      </div>

      <div className="result-meta">
        <span className="meta-pill">
          Document #{result.document_id}
        </span>

        <span className="meta-pill">
          Chunk #{result.chunk_id}
        </span>

        <span className="meta-pill">
          Index {result.chunk_index}
        </span>
      </div>
    </article>
  )
}


export default ResultCard
