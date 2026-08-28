function PrfToggle({
  enabled,
  onChange,
}) {
  return (
    <label className="prf-box">
      <div className="prf-main">
        <div className="prf-icon">
          PRF
        </div>

        <div>
          <p className="prf-title">
            Pseudo Relevance Feedback
          </p>

          <p className="prf-copy">
            Rocchio-based query expansion
            for the VSM pipeline.
          </p>
        </div>
      </div>

      <span className="switch">
        <input
          type="checkbox"
          checked={enabled}
          onChange={
            (event) =>
              onChange(
                event.target.checked
              )
          }
        />

        <span className="switch-track" />
        <span className="switch-thumb" />
      </span>
    </label>
  )
}


export default PrfToggle
