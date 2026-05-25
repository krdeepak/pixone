import { useState } from "react";
import ImageCanvas from "./ImageCanvas";
import Controls from "./Controls";
import { reframeImage, smartReframeImage, type ReframeParams, type SmartReframeMode } from "../../api/pixone";

type Tab = "manual" | "smart";

const SMART_MODES: { value: SmartReframeMode; label: string; desc: string }[] = [
  { value: "zoomed",   label: "Zoomed",   desc: "Tight crop — face fills the frame" },
  { value: "standard", label: "Standard", desc: "Face + shoulders, balanced framing" },
  { value: "full",     label: "Full",     desc: "Wide crop — shows more of the scene" },
];

const ASPECT_PRESETS = ["1:1", "4:3", "16:9", "9:16", "3:4"];

export default function ReframePage() {
  const [tab, setTab] = useState<Tab>("manual");

  // shared
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);   // preview URL (blob or typed)
  const [typedUrl, setTypedUrl] = useState("");                     // raw text in the URL input
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // manual
  const [aspectRatio, setAspectRatio] = useState("Free");
  const [crop, setCrop] = useState<ReframeParams>({ x: 0, y: 0, width: 0, height: 0 });

  // smart
  const [smartMode, setSmartMode] = useState<SmartReframeMode>("standard");
  const [smartAspect, setSmartAspect] = useState("1:1");
  const [faceCount, setFaceCount] = useState<number | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImageUrl(URL.createObjectURL(file));
    setTypedUrl("");
    setResultUrl(null);
    setError(null);
    setFaceCount(null);
  };

  const handleUrlLoad = () => {
    if (!typedUrl.trim()) return;
    setImageFile(null);
    setImageUrl(typedUrl.trim());
    setResultUrl(null);
    setError(null);
    setFaceCount(null);
  };

  const imageSource: File | string | null = imageFile ?? (typedUrl.trim() ? typedUrl.trim() : null);

  const handleManualSubmit = async () => {
    if (!imageSource || !crop.width || !crop.height) return;
    setLoading(true);
    setError(null);
    try {
      const result = await reframeImage(imageSource, crop);
      setResultUrl(result.output_url);
    } catch {
      setError("Reframe failed. Check the API server.");
    } finally {
      setLoading(false);
    }
  };

  const handleSmartSubmit = async () => {
    if (!imageSource) return;
    setLoading(true);
    setError(null);
    setFaceCount(null);
    try {
      const result = await smartReframeImage(imageSource, smartMode, smartAspect);
      setResultUrl(result.output_url);
      setFaceCount(result.face_count);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Smart reframe failed. No face detected or API error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Reframe</h1>

      {/* Upload */}
      <div className="mb-6 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Upload Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
          />
        </div>
        <div className="flex-1 min-w-64">
          <label className="block text-sm text-gray-400 mb-2">Or paste image URL</label>
          <div className="flex gap-2">
            <input
              type="url"
              value={typedUrl}
              onChange={(e) => setTypedUrl(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleUrlLoad()}
              placeholder="https://..."
              className="flex-1 px-3 py-2 text-sm bg-gray-800 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleUrlLoad}
              disabled={!typedUrl.trim()}
              className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 disabled:opacity-40 rounded"
            >
              Load
            </button>
          </div>
        </div>
      </div>

      {/* Tab toggle */}
      <div className="flex gap-1 mb-6 bg-gray-900 rounded p-1 w-fit">
        {(["manual", "smart"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); setResultUrl(null); setError(null); }}
            className={`px-5 py-1.5 rounded text-sm font-medium capitalize transition-colors ${
              tab === t ? "bg-indigo-600 text-white" : "text-gray-400 hover:text-white"
            }`}
          >
            {t === "smart" ? "Smart / Auto" : "Manual"}
          </button>
        ))}
      </div>

      {imageUrl && tab === "manual" && (
        <div className="flex gap-8 flex-wrap">
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Drag to select crop area</p>
            <ImageCanvas
              imageUrl={imageUrl}
              aspectRatio={aspectRatio}
              onCropChange={(c) => setCrop({ x: c.x, y: c.y, width: c.width, height: c.height })}
            />
          </div>
          <div className="w-64 flex flex-col gap-6">
            <Controls
              aspectRatio={aspectRatio}
              onAspectChange={setAspectRatio}
              onSubmit={handleManualSubmit}
              loading={loading}
            />
            {error && <p className="text-sm text-red-400">{error}</p>}
            <ResultPanel url={resultUrl} />
          </div>
        </div>
      )}

      {imageUrl && tab === "smart" && (
        <div className="flex gap-8 flex-wrap">
          {/* Preview */}
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Original</p>
            <img src={imageUrl} alt="Original" className="rounded border border-gray-700 max-w-full max-h-[500px] object-contain" />
          </div>

          {/* Smart controls */}
          <div className="w-64 flex flex-col gap-6">
            {/* Mode selector */}
            <div>
              <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Mode</p>
              <div className="flex flex-col gap-2">
                {SMART_MODES.map(({ value, label, desc }) => (
                  <button
                    key={value}
                    onClick={() => setSmartMode(value)}
                    className={`text-left px-3 py-2.5 rounded border transition-colors ${
                      smartMode === value
                        ? "bg-indigo-600 border-indigo-500 text-white"
                        : "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
                    }`}
                  >
                    <div className="font-medium text-sm">{label}</div>
                    <div className="text-xs opacity-70 mt-0.5">{desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Aspect ratio */}
            <div>
              <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Aspect Ratio</p>
              <div className="flex flex-wrap gap-2">
                {ASPECT_PRESETS.map((p) => (
                  <button
                    key={p}
                    onClick={() => setSmartAspect(p)}
                    className={`px-3 py-1.5 text-sm rounded border ${
                      smartAspect === p
                        ? "bg-indigo-600 border-indigo-500 text-white"
                        : "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleSmartSubmit}
              disabled={loading}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded text-sm font-medium"
            >
              {loading ? "Processing..." : "Auto Reframe"}
            </button>

            {faceCount !== null && (
              <p className="text-xs text-gray-400">{faceCount} face{faceCount !== 1 ? "s" : ""} detected</p>
            )}
            {error && <p className="text-sm text-red-400">{error}</p>}
            <ResultPanel url={resultUrl} />
          </div>
        </div>
      )}
    </div>
  );
}

function ResultPanel({ url }: { url: string | null }) {
  if (!url) return null;
  return (
    <div>
      <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Result</p>
      <img src={url} alt="Result" className="rounded border border-gray-700 w-full" />
      <a href={url} download className="mt-2 block text-center text-sm text-indigo-400 hover:text-indigo-300">
        Download
      </a>
    </div>
  );
}
