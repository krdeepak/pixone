interface Props {
  aspectRatio: string;
  onAspectChange: (ratio: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

const PRESETS = ["Free", "1:1", "4:3", "16:9", "9:16", "3:4"];

export default function Controls({ aspectRatio, onAspectChange, onSubmit, loading }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">Aspect Ratio</p>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p}
              onClick={() => onAspectChange(p)}
              className={`px-3 py-1.5 text-sm rounded border ${
                aspectRatio === p
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
        onClick={onSubmit}
        disabled={loading}
        className="mt-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded text-sm font-medium"
      >
        {loading ? "Processing..." : "Apply Reframe"}
      </button>
    </div>
  );
}