import urllib.request
from ninja import Router, File, Form
from ninja.files import UploadedFile
from ninja.errors import HttpError
from apps.core.models import ProcessingRequest
from apps.core.storage import get_storage
from .schemas import ReframeParams, ReframeResponse, SmartReframeParams, SmartReframeResponse
from .service import reframe_image, smart_reframe_image

router = Router(tags=["reframe"])


def _read_and_upload(image: UploadedFile) -> tuple[bytes, str]:
    data = b"".join(image.chunks())
    url = get_storage().upload(data, folder="uploads", filename=image.name)
    return data, url


def _fetch_url_and_upload(image_url: str) -> tuple[bytes, str]:
    with urllib.request.urlopen(image_url) as resp:
        data = resp.read()
    filename = image_url.split("/")[-1].split("?")[0] or "image.jpg"
    url = get_storage().upload(data, folder="uploads", filename=filename)
    return data, url


def _resolve_image(image: UploadedFile | None, image_url: str | None) -> tuple[bytes, str, str]:
    if image and image_url:
        raise HttpError(422, "Provide either image or image_url, not both.")
    if image:
        data, url = _read_and_upload(image)
        return data, url, image.name
    if image_url:
        data, url = _fetch_url_and_upload(image_url)
        filename = image_url.split("/")[-1].split("?")[0] or "image.jpg"
        return data, url, filename
    raise HttpError(422, "Provide either image or image_url.")


@router.post("/", response=ReframeResponse)
def reframe(request, params: ReframeParams = Form(...), image: UploadedFile | None = File(None)):
    image_bytes, input_url, filename = _resolve_image(image, params.image_url)

    proc_request = ProcessingRequest.objects.create(
        feature=ProcessingRequest.Feature.REFRAME,
        status=ProcessingRequest.Status.PENDING,
        input_params=params.model_dump(),
        input_file_url=input_url,
    )

    try:
        result = reframe_image(image_bytes, filename, params, proc_request)
        proc_request.status = ProcessingRequest.Status.DONE
        proc_request.save()
    except Exception as e:
        proc_request.status = ProcessingRequest.Status.FAILED
        proc_request.save()
        raise e

    return ReframeResponse(
        request_id=proc_request.id,
        output_url=result.output_url,
        metadata=result.metadata,
    )


@router.post("/smart/", response=SmartReframeResponse)
def smart_reframe(request, params: SmartReframeParams = Form(...), image: UploadedFile | None = File(None)):
    image_bytes, input_url, filename = _resolve_image(image, params.image_url)

    proc_request = ProcessingRequest.objects.create(
        feature=ProcessingRequest.Feature.REFRAME,
        status=ProcessingRequest.Status.PENDING,
        input_params={"mode": params.mode.value, "aspect_ratio": params.aspect_ratio, "smart": True},
        input_file_url=input_url,
    )

    try:
        result, face_count = smart_reframe_image(image_bytes, filename, params.mode, params.aspect_ratio, proc_request)
        proc_request.status = ProcessingRequest.Status.DONE
        proc_request.save()
    except ValueError as e:
        proc_request.status = ProcessingRequest.Status.FAILED
        proc_request.save()
        raise HttpError(422, str(e))
    except Exception as e:
        proc_request.status = ProcessingRequest.Status.FAILED
        proc_request.save()
        raise e

    return SmartReframeResponse(
        request_id=proc_request.id,
        output_url=result.output_url,
        face_count=face_count,
        mode=params.mode.value,
        metadata=result.metadata,
    )