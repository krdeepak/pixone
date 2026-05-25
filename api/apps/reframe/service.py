import io
import time
from PIL import Image
from apps.core.models import ProcessingRequest, ProcessingResult
from apps.core.storage import get_storage
from apps.face_detection.services import get_detector
from .schemas import ReframeParams, SmartReframeMode


def reframe_image(
    image_bytes: bytes,
    filename: str,
    params: ReframeParams,
    request: ProcessingRequest,
) -> ProcessingResult:
    with Image.open(io.BytesIO(image_bytes)) as img:
        cropped = img.crop((params.x, params.y, params.x + params.width, params.y + params.height))

        if params.output_width and params.output_height:
            cropped = cropped.resize((params.output_width, params.output_height), Image.LANCZOS)

        buf = io.BytesIO()
        cropped.save(buf, format="JPEG", quality=92)
        result_bytes = buf.getvalue()

        output_url = get_storage().upload(result_bytes, folder="results/reframe", filename=f"{request.id}_{filename}")

        return ProcessingResult.objects.create(
            request=request,
            output_url=output_url,
            metadata={
                "original_size": list(img.size),
                "crop_box": [params.x, params.y, params.x + params.width, params.y + params.height],
                "output_size": list(cropped.size),
            },
        )


# Padding added around the face bbox on each side, as a fraction of face size.
SMART_MODE_PADDING: dict[SmartReframeMode, float] = {
    SmartReframeMode.ZOOMED: 0.3,
    SmartReframeMode.STANDARD: 0.5,
    SmartReframeMode.FULL: 1.8,
}

ASPECT_RATIO_MAP = {
    "1:1": 1.0,
    "4:3": 4 / 3,
    "16:9": 16 / 9,
    "9:16": 9 / 16,
    "3:4": 3 / 4,
}


def _parse_aspect(aspect_ratio: str) -> float:
    return ASPECT_RATIO_MAP.get(aspect_ratio, 1.0)


def _compute_smart_crop(
    img_width: int,
    img_height: int,
    face_x: int,
    face_y: int,
    face_w: int,
    face_h: int,
    mode: SmartReframeMode,
    aspect_ratio: float,
) -> tuple[int, int, int, int]:
    """Return (left, top, right, bottom) crop box.

    Logic:
    1. Add padding around all 4 sides of the face bbox — mode controls how much.
    2. Fit the padded region into the target aspect ratio, centered on the face center.
    3. Cap to image bounds while preserving aspect ratio (scale both axes together).
    4. Shift box to stay within image — no stretching, no ratio distortion.
    """
    pad_fraction = SMART_MODE_PADDING[mode]
    face_size = max(face_w, face_h)
    pad = face_size * pad_fraction

    padded_w = face_w + pad * 2
    padded_h = face_h + pad * 2

    if aspect_ratio >= 1.0:
        crop_w = max(padded_w, padded_h * aspect_ratio)
        crop_h = crop_w / aspect_ratio
    else:
        crop_h = max(padded_h, padded_w / aspect_ratio)
        crop_w = crop_h * aspect_ratio

    # Cap to image bounds preserving aspect ratio
    scale_w = img_width / crop_w if crop_w > img_width else 1.0
    scale_h = img_height / crop_h if crop_h > img_height else 1.0
    scale = min(scale_w, scale_h)
    crop_w *= scale
    crop_h *= scale

    # Center strictly on face center
    cx = face_x + face_w / 2
    cy = face_y + face_h / 2

    left = cx - crop_w / 2
    top = cy - crop_h / 2
    right = left + crop_w
    bottom = top + crop_h

    # Shift into image bounds without changing crop size
    if left < 0:
        right -= left
        left = 0.0
    if top < 0:
        bottom -= top
        top = 0.0
    if right > img_width:
        left -= right - img_width
        right = float(img_width)
    if bottom > img_height:
        top -= bottom - img_height
        bottom = float(img_height)

    return int(max(0, left)), int(max(0, top)), int(min(img_width, right)), int(min(img_height, bottom))


def smart_reframe_image(
    image_bytes: bytes,
    filename: str,
    mode: SmartReframeMode,
    aspect_ratio: str,
    request: ProcessingRequest,
) -> tuple[ProcessingResult, int]:
    detector = get_detector()
    faces = detector.detect(image_bytes)

    if not faces:
        raise ValueError("No faces detected in the image.")

    primary = max(faces, key=lambda f: f.width * f.height)
    ar = _parse_aspect(aspect_ratio)

    with Image.open(io.BytesIO(image_bytes)) as img:
        img_w, img_h = img.size
        left, top, right, bottom = _compute_smart_crop(
            img_w, img_h,
            primary.x, primary.y, primary.width, primary.height,
            mode, ar,
        )

        cropped = img.crop((left, top, right, bottom))

        buf = io.BytesIO()
        cropped.save(buf, format="JPEG", quality=92)
        result_bytes = buf.getvalue()

        output_url = get_storage().upload(result_bytes, folder="results/reframe", filename=f"{request.id}_smart_{filename}")

        result = ProcessingResult.objects.create(
            request=request,
            output_url=output_url,
            metadata={
                "original_size": [img_w, img_h],
                "crop_box": [left, top, right, bottom],
                "output_size": list(cropped.size),
                "face_count": len(faces),
                "primary_face": {"x": primary.x, "y": primary.y, "w": primary.width, "h": primary.height},
                "mode": mode.value,
                "aspect_ratio": aspect_ratio,
            },
        )

    return result, len(faces)
