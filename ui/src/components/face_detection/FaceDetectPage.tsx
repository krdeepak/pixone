import { useState, useRef, useCallback } from "react";
import { detectFaces, type FaceRect } from "../../api/pixone";

export default function FaceDetectPage() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [faces, setFaces] = useState<FaceRect[]>([]);
  const [naturalSize, setNaturalSize] = useState({ w: 1, h: 1 });
  const [displaySize, setDisplaySize] = useState({ w: 1, h: 1 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImageUrl(URL.createObjectURL(file));
    setFaces([]);
    setError(null);
  };

  // Capture both natural (original) and rendered dimensions once image loads
  const handleImageLoad = useCallback(() => {
    const img = imgRef.current;
    if (!img) return;
    setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
    setDisplaySize({ w: img.clientWidth, h: img.clientHeight });
  }, []);

  // Re-measure if the container resizes
  const handleImageResize = useCallback(() => {
    const img = imgRef.current;
    if (!img) return;
    setDisplaySize({ w: img.clientWidth, h: img.clientHeight });
  }, []);

  const handleDetect = async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);
    try {
      const result = await detectFaces(imageFile);
      setFaces(result.faces);
    } catch {
      setError("Detection failed. Check the API server and AWS credentials.");
    } finally {
      setLoading(false);
    }
  };

  // Scale face coords from original image pixels → displayed image pixels
  const scaleX = displaySize.w / naturalSize.w;
  const scaleY = displaySize.h / naturalSize.h;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Face Detection</h1>

      <div className="mb-6">
        <label className="block text-sm text-gray-400 mb-2">Upload Image</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
        />
      </div>

      {imageUrl && (
        <>
          <div className="relative inline-block mb-6">
            <img
              ref={imgRef}
              src={imageUrl}
              alt="Upload"
              className="rounded border border-gray-700 max-w-full block"
              onLoad={handleImageLoad}
              onResize={handleImageResize}
            />
            {faces.map((face, i) => (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left:   face.x      * scaleX,
                  top:    face.y      * scaleY,
                  width:  face.width  * scaleX,
                  height: face.height * scaleY,
                }}
                className="border-2 border-indigo-400"
              >
                <span className="absolute -top-5 left-0 text-xs bg-indigo-600 px-1 rounded whitespace-nowrap">
                  {face.confidence.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={handleDetect}
              disabled={loading}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded text-sm font-medium"
            >
              {loading ? "Detecting..." : "Detect Faces"}
            </button>
            {faces.length > 0 && (
              <span className="text-sm text-gray-400">
                {faces.length} face{faces.length !== 1 ? "s" : ""} found
              </span>
            )}
          </div>

          {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
        </>
      )}
    </div>
  );
}