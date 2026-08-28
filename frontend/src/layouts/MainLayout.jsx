import Navbar from "../components/Navbar"


function MainLayout({
  children,
}) {
  return (
    <div className="app-shell">
      <Navbar />

      <main className="app-main">
        {children}
      </main>

      <footer className="app-footer">
        <div className="app-footer-inner">
          <div>
            <p className="footer-title">
              MIR Search Engine
            </p>

            <p className="footer-copy">
              Advanced Information Retrieval
            </p>
          </div>

          <div>
            <p className="footer-title">
              Ayla Nasiri · 402150071
            </p>

            <p className="footer-copy">
              Computer Engineering ·
              Sharif International University of Technology
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}


export default MainLayout
