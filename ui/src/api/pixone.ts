import axios from "axios";

const client = axios.create({ baseURL: (import.meta.env.VITE_API_URL ?? "") + "/api" });

export interface ReframeParams {
  x: number;
  y: number;
  width: number;
  height: number;
  output_width?: number;
  output_height?: number;
}

export interface ReframeResponse {
  request_id: number;
  output_url: string;
  metadata: Record<string, unknown>;
}

export interface FaceRect {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  landmarks: Record<string, { x: number; y: number }> | null;
}

export interface FaceDetectionResponse {
  request_id: number;
  faces: FaceRect[];
  face_count: number;
}

export async function reframeImage(image: File | string, params: ReframeParams): Promise<ReframeResponse> {
  const form = new FormData();
  if (typeof image === "string") {
    form.append("image_url", image);
  } else {
    form.append("image", image);
  }
  form.append("x", String(Math.round(params.x)));
  form.append("y", String(Math.round(params.y)));
  form.append("width", String(Math.round(params.width)));
  form.append("height", String(Math.round(params.height)));
  if (params.output_width) form.append("output_width", String(params.output_width));
  if (params.output_height) form.append("output_height", String(params.output_height));
  const { data } = await client.post<ReframeResponse>("/reframe/", form);
  return data;
}

export type SmartReframeMode = "zoomed" | "standard" | "full";

export interface SmartReframeResponse {
  request_id: number;
  output_url: string;
  face_count: number;
  mode: SmartReframeMode;
  metadata: Record<string, unknown>;
}

export async function smartReframeImage(
  image: File | string,
  mode: SmartReframeMode,
  aspect_ratio: string
): Promise<SmartReframeResponse> {
  const form = new FormData();
  if (typeof image === "string") {
    form.append("image_url", image);
  } else {
    form.append("image", image);
  }
  form.append("mode", mode);
  form.append("aspect_ratio", aspect_ratio);
  const { data } = await client.post<SmartReframeResponse>("/reframe/smart/", form);
  return data;
}

export async function detectFaces(image: File): Promise<FaceDetectionResponse> {
  const form = new FormData();
  form.append("image", image);
  const { data } = await client.post<FaceDetectionResponse>("/face-detection/", form);
  return data;
}
