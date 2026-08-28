import {
  useState,
} from "react"

import {
  Link,
} from "react-router-dom"

import {
  askRag,
  searchDocuments,
} from "../api/searchApi"

import AlgorithmSelector from "../components/search/AlgorithmSelector"
import PrfToggle from "../components/search/PrfToggle"
import RagAnswer from "../components/search/RagAnswer"
import ResultCard from "../components/search/ResultCard"
import SearchBar from "../components/search/SearchBar"


const methodNames = {
  vsm: "VSM / TF-IDF",
  bm25: "BM25",
  semantic: "Semantic Search",
  hybrid: "Hybrid Search",
  rag: "Ask AI / RAG",
}


function IdentityCard({
  label,
  value,
  large = false,
}) {
  return (
    <div className="identity-card">
      <p className="app-label">
        {label}
      </p>

      <p
        className={
          `identity-value ${
            large
              ? "large"
              : ""
          }`
        }
      >
        {value}
      </p>
    </div>
  )
}


function Search() {
  const [
    query,
    setQuery,
  ] = useState("")

  const [
    lastSearchQuery,
    setLastSearchQuery,
  ] = useState("")

  const [
    algorithm,
    setAlgorithm,
  ] = useState("vsm")

  const [
    prfEnabled,
    setPrfEnabled,
  ] = useState(false)

  const [
    prfInfo,
    setPrfInfo,
  ] = useState(null)

  const [
    results,
    setResults,
  ] = useState([])

  const [
    ragResult,
    setRagResult,
  ] = useState(null)

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState("")


  async function handleSearch(
    event
  ) {
    event.preventDefault()

    const normalizedQuery =
      query.trim()

    if (!normalizedQuery) {
      setError(
        "Please enter a search query."
      )

      return
    }

    setLoading(true)
    setError("")
    setResults([])
    setRagResult(null)
    setPrfInfo(null)
    setLastSearchQuery(
      normalizedQuery
    )

    try {
      if (algorithm === "rag") {
        const data =
          await askRag({
            query: normalizedQuery,
            limit: 3,
          })

        setRagResult(data)

        return
      }

      const data =
        await searchDocuments({
          query: normalizedQuery,
          mode: algorithm,
          limit: 10,
          prf:
            algorithm === "vsm"
            && prfEnabled,
        })

      setResults(
        data.results ?? []
      )

      if (algorithm === "vsm") {
        setPrfInfo(
          data.prf ?? null
        )
      }
    } catch (requestError) {
      console.error(
        "Search request failed:",
        requestError
      )

      const detail =
        requestError.response
          ?.data
          ?.detail

      if (
        typeof detail === "string"
      ) {
        setError(detail)
      } else {
        setError(
          "The request failed. Please make sure the backend is running."
        )
      }
    } finally {
      setLoading(false)
    }
  }


  function handleAlgorithmChange(
    nextAlgorithm
  ) {
    setAlgorithm(
      nextAlgorithm
    )

    if (
      nextAlgorithm !== "vsm"
    ) {
      setPrfEnabled(false)
    }

    setResults([])
    setRagResult(null)
    setPrfInfo(null)
    setLastSearchQuery("")
    setError("")
  }


  const shouldHighlight =
    algorithm === "vsm"
    || algorithm === "bm25"

  const highlightQuery =
    algorithm === "vsm"
    && prfInfo?.applied
      ? prfInfo.expanded_query
      : lastSearchQuery


  return (
    <>
      <section className="hero-card">
        <div className="hero-content">
          <div className="hero-badges">
            <span className="hero-badge">
              Academic Search System
            </span>

            <span className="hero-badge secondary">
              MIR · RAG · Retrieval
            </span>
          </div>

          <h1 className="hero-title">
            Advanced search,
            <span className="hero-title-accent">
              explained visually.
            </span>
          </h1>

          <p className="hero-copy">
            Compare lexical retrieval,
            semantic embeddings, hybrid ranking,
            pseudo relevance feedback, and
            grounded RAG without changing the corpus.
          </p>

          <div className="hero-actions">
            <a
              href="#search-console"
              className="btn btn-primary"
            >
              Start Searching
            </a>

            <Link
              to="/dashboard"
              className="btn btn-light"
            >
              Manage Corpus →
            </Link>
          </div>
        </div>

        <div className="hero-image-wrap">
          <img
            src="/search-hero.svg"
            alt="Visual illustration of lexical, semantic, hybrid, and RAG retrieval pipelines"
            className="hero-image"
          />
        </div>
      </section>

      <section className="app-section">
        <div className="identity-strip">
          <IdentityCard
            label="Student"
            value="Ayla Nasiri"
            large
          />

          <IdentityCard
            label="Student ID"
            value="402150071"
          />

          <IdentityCard
            label="Major"
            value="Computer Engineering"
          />

          <IdentityCard
            label="Course"
            value="Advanced Information Retrieval"
          />
        </div>

        <div
          className="identity-card"
          style={{
            marginTop: "14px",
          }}
        >
          <p className="app-label">
            University
          </p>

          <p className="identity-value large">
            Sharif International University of Technology
          </p>
        </div>
      </section>

      <form
        id="search-console"
        onSubmit={handleSearch}
        className="app-panel console app-section"
      >
        <div className="console-top">
          <div>
            <p className="app-eyebrow">
              Retrieval Console
            </p>

            <h2 className="app-section-title">
              Build your search
            </h2>

            <p className="app-section-copy">
              Run the same query through
              multiple retrieval strategies.
            </p>
          </div>

          <div className="active-pipeline">
            <p className="app-label">
              Active Pipeline
            </p>

            <p className="active-pipeline-value">
              {methodNames[algorithm]}
            </p>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gap: "24px",
          }}
        >
          <SearchBar
            value={query}
            onChange={setQuery}
          />

          <AlgorithmSelector
            value={algorithm}
            onChange={
              handleAlgorithmChange
            }
          />

          {algorithm === "vsm" && (
            <PrfToggle
              enabled={prfEnabled}
              onChange={setPrfEnabled}
            />
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              width: "100%",
              minHeight: "54px",
              fontSize: "1rem",
            }}
          >
            {loading
              ? "Processing..."
              : algorithm === "rag"
                ? "Ask AI"
                : "Search"}
          </button>
        </div>
      </form>

      {error && (
        <div className="alert error app-section">
          {error}
        </div>
      )}

      {algorithm === "vsm"
        && prfInfo?.enabled && (
          <section className="app-panel console app-section">
            <div className="app-section-header">
              <div>
                <p className="app-eyebrow">
                  Query Expansion
                </p>

                <h2 className="app-section-title">
                  Pseudo Relevance Feedback
                </h2>
              </div>

              <span className="meta-pill">
                {prfInfo.applied
                  ? "PRF Applied"
                  : "No Expansion"}
              </span>
            </div>

            <div className="app-grid-2">
              <div className="app-panel-flat">
                <div style={{ padding: "18px" }}>
                  <p className="app-label">
                    Original Query
                  </p>

                  <p className="identity-value">
                    {prfInfo.original_query}
                  </p>
                </div>
              </div>

              <div className="app-panel-flat">
                <div style={{ padding: "18px" }}>
                  <p className="app-label">
                    Expanded Query
                  </p>

                  <p className="identity-value">
                    {prfInfo.expanded_query}
                  </p>
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: "18px",
              }}
            >
              <p className="app-label">
                Expansion Terms
              </p>

              <div
                className="result-meta"
                style={{
                  marginTop: "10px",
                }}
              >
                {(
                  prfInfo.expansion_terms
                  ?? []
                ).map(
                  (term) => (
                    <span
                      key={term}
                      className="meta-pill"
                    >
                      {term}
                    </span>
                  )
                )}
              </div>
            </div>
          </section>
        )}

      <section className="app-section">
        {results.length > 0 && (
          <>
            <div className="app-section-header">
              <div>
                <p className="app-eyebrow">
                  Ranked Retrieval
                </p>

                <h2 className="app-section-title">
                  Search Results
                </h2>
              </div>

              <span className="meta-pill">
                {results.length} results
              </span>
            </div>

            <div className="results-stack">
              {results.map(
                (
                  result,
                  index
                ) => (
                  <ResultCard
                    key={result.chunk_id}
                    result={result}
                    rank={index + 1}
                    highlightQuery={
                      shouldHighlight
                        ? highlightQuery
                        : ""
                    }
                  />
                )
              )}
            </div>
          </>
        )}

        {!loading
          && !ragResult
          && results.length === 0
          && lastSearchQuery
          && !error && (
            <div
              className="app-panel-flat"
              style={{
                padding: "24px",
                color: "#718196",
              }}
            >
              No results found for this query.
            </div>
          )}

        {ragResult && (
          <RagAnswer
            answer={ragResult.answer}
            sources={
              ragResult.sources
              ?? []
            }
          />
        )}
      </section>
    </>
  )
}


export default Search
