import { useRef, useEffect, useState } from "react";
import { Stage, Layer, Image as KonvaImage, Rect, Transformer } from "react-konva";
import Konva from "konva";

interface CropBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface Props {
  imageUrl: string;
  aspectRatio: string;
  onCropChange: (crop: CropBox) => void;
}

export default function ImageCanvas({ imageUrl, aspectRatio, onCropChange }: Props) {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [stageSize, setStageSize] = useState({ width: 800, height: 600 });
  const [crop, setCrop] = useState<CropBox>({ x: 50, y: 50, width: 300, height: 200 });
  const rectRef = useRef<Konva.Rect>(null);
  const trRef = useRef<Konva.Transformer>(null);

  useEffect(() => {
    const img = new window.Image();
    img.src = imageUrl;
    img.onload = () => {
      setImage(img);
      setStageSize({ width: img.width, height: img.height });
      const initialCrop = { x: 0, y: 0, width: img.width, height: img.height };
      setCrop(initialCrop);
      onCropChange(initialCrop);
    };
  }, [imageUrl]);

  useEffect(() => {
    if (trRef.current && rectRef.current) {
      trRef.current.nodes([rectRef.current]);
      trRef.current.getLayer()?.batchDraw();
    }
  }, [image]);

  const getAspectRatio = (): number | null => {
    const map: Record<string, number> = { "1:1": 1, "4:3": 4 / 3, "16:9": 16 / 9, "9:16": 9 / 16, "3:4": 3 / 4 };
    return map[aspectRatio] ?? null;
  };

  // When aspect ratio preset changes, resize crop box to match
  useEffect(() => {
    if (!image) return;
    const ratio = getAspectRatio();
    if (ratio === null) return; // Free — don't force resize
    setCrop((prev) => {
      const newWidth = Math.min(prev.width, image.width);
      const newHeight = Math.round(newWidth / ratio);
      const adjusted = {
        x: Math.min(prev.x, image.width - newWidth),
        y: Math.min(prev.y, image.height - newHeight),
        width: newWidth,
        height: newHeight,
      };
      onCropChange(adjusted);
      return adjusted;
    });
  }, [aspectRatio]);

  const handleDragEnd = (e: Konva.KonvaEventObject<DragEvent>) => {
    const node = e.target;
    const updated = { ...crop, x: node.x(), y: node.y() };
    setCrop(updated);
    onCropChange(updated);
  };

  const handleTransformEnd = () => {
    const node = rectRef.current!;
    const scaleX = node.scaleX();
    const scaleY = node.scaleY();
    node.scaleX(1);
    node.scaleY(1);
    const updated = {
      x: node.x(),
      y: node.y(),
      width: Math.max(20, node.width() * scaleX),
      height: Math.max(20, node.height() * scaleY),
    };
    setCrop(updated);
    onCropChange(updated);
  };

  const scale = Math.min(800 / stageSize.width, 600 / stageSize.height, 1);

  return (
    <div className="overflow-auto rounded border border-gray-700">
      <Stage width={stageSize.width * scale} height={stageSize.height * scale} scaleX={scale} scaleY={scale}>
        <Layer>
          {image && <KonvaImage image={image} x={0} y={0} />}
          <Rect
            ref={rectRef}
            x={crop.x}
            y={crop.y}
            width={crop.width}
            height={crop.height}
            stroke="#6366f1"
            strokeWidth={2}
            fill="rgba(99,102,241,0.15)"
            draggable
            onDragEnd={handleDragEnd}
            onTransformEnd={handleTransformEnd}
          />
          <Transformer
            ref={trRef}
            keepRatio={getAspectRatio() !== null}
            enabledAnchors={["top-left", "top-right", "bottom-left", "bottom-right"]}
          />
        </Layer>
      </Stage>
    </div>
  );
}
