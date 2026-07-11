import { Navigate, Route, Routes } from 'react-router-dom'
import ComparePage from './pages/ComparePage'
import HomePage from './pages/HomePage'
import ViewerPage from './pages/ViewerPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/doc/:id" element={<ViewerPage />} />
      <Route path="/compare/:stem" element={<ComparePage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
