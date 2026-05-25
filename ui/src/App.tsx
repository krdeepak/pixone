import { Routes, Route, Link } from "react-router-dom";
import ReframePage from "./components/reframe/ReframePage";
import FaceDetectPage from "./components/face_detection/FaceDetectPage";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="flex items-center gap-6 px-8 py-4 bg-gray-900 border-b border-gray-800">
        <span className="text-xl font-bold tracking-tight text-indigo-400">Pixone</span>
        <Link to="/reframe" className="text-sm text-gray-300 hover:text-white">Reframe</Link>
        <Link to="/face-detection" className="text-sm text-gray-300 hover:text-white">Face Detection</Link>
      </nav>

      <main className="p-8">
        <Routes>
          <Route path="/" element={<ReframePage />} />
          <Route path="/reframe" element={<ReframePage />} />
          <Route path="/face-detection" element={<FaceDetectPage />} />
        </Routes>
      </main>
    </div>
  );
}
