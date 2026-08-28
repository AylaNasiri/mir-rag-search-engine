
import { BrowserRouter, Routes, Route } from "react-router-dom"

import MainLayout from "./layouts/MainLayout"
import Search from "./pages/Search"
import Dashboard from "./pages/Dashboard"


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={
            <MainLayout>
              <Search />
            </MainLayout>
          }
        />


        <Route
          path="/dashboard"
          element={
            <MainLayout>
              <Dashboard />
            </MainLayout>
          }
        />

      </Routes>

    </BrowserRouter>
  )
}

export default App