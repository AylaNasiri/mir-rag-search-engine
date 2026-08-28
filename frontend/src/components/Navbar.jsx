import {
  NavLink,
} from "react-router-dom"


function Navbar() {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <NavLink
          to="/"
          className="brand"
        >
          <div className="brand-logo">
            MIR
          </div>

          <div>
            <p className="brand-title">
              MIR Search Engine
            </p>

            <p className="brand-subtitle">
              Advanced Information Retrieval
            </p>
          </div>
        </NavLink>

        <div className="topbar-actions">
          <nav className="nav-switch">
            <NavLink
              to="/"
              end
              className={({
                isActive,
              }) =>
                `nav-link ${
                  isActive
                    ? "active"
                    : ""
                }`
              }
            >
              Search
            </NavLink>

            <NavLink
              to="/dashboard"
              className={({
                isActive,
              }) =>
                `nav-link ${
                  isActive
                    ? "active"
                    : ""
                }`
              }
            >
              Admin Dashboard
            </NavLink>
          </nav>

          <div className="student-chip">
            <div className="student-avatar">
              AN
            </div>

            <div>
              <p className="student-name">
                Ayla Nasiri
              </p>

              <p className="student-meta">
                402150071 · Computer Engineering
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}


export default Navbar
