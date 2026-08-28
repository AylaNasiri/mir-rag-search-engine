function SearchBar({
  value,
  onChange,
}) {
  return (
    <div>
      <p className="app-label">
        Search Query
      </p>

      <p className="field-helper">
        Search an exact identifier,
        a concept, or a natural-language question.
      </p>

      <div
        className="search-field"
        style={{
          marginTop: "12px",
        }}
      >
        <div className="search-icon">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            width="22"
            height="22"
            aria-hidden="true"
          >
            <path
              d="M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"
              stroke="currentColor"
              strokeWidth="2"
            />

            <path
              d="m21 21-4.35-4.35"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>

        <input
          type="text"
          value={value}
          onChange={
            (event) =>
              onChange(
                event.target.value
              )
          }
          placeholder="Try: semantic retrieval, LEXICAL-DOCX-731, or ask a question..."
          className="search-input"
        />
      </div>
    </div>
  )
}


export default SearchBar
