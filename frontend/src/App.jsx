import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import Header from "./components/Header";
import HomePage from "./pages/HomePage";
import FichePage from "./pages/FichePage";

// Layout : élément partagé (l'en-tête) qui entoure toutes les pages.
// <Outlet /> est l'endroit où React Router insère la page active.
function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <Header />
      <Outlet />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/fiches/:id" element={<FichePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}