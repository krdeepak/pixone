from ninja import Router, File, Form
from ninja.files import UploadedFile
from apps.core.models import ProcessingRequest
from apps.core.storage import get_storage
from .schemas import ReframeParams, ReframeResponse, SmartReframeParams, SmartReframeResponse
from .service import reframe_image, smart_reframe_image

router = Router(tags=["reframe"])


def _read_and_upload(image: UploadedFile) -> tuple[bytes, str]:
    """Read uploaded file into bytes and store via configured backend. Returns (bytes, url)."""
    data = b"".join(image.chunks())
    url = get_storage().upload(data, folder="uploads", filename=image.name)
    return data, url


@router.post("/", response=ReframeResponse)
def reframe(request, image: UploadedFile = File(...), params: ReframeParams = Form(...)):
    image_bytes, input_url = _read_and_upload(image)

    proc_request = ProcessingRequest.objects.create(
        feature=ProcessingRequest.Feature.REFRAME,
        status=ProcessingRequest.Status.PENDING,
        input_params=params.model_dump(),
        input_file_url=input_url,
    )

    try:
        result = reframe_image(image_bytes, image.name, params, proc_request)
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
def smart_reframe(request, image: UploadedFile = File(...), params: SmartReframeParams = Form(...)):
    image_bytes, input_url = _read_and_upload(image)

    proc_request = ProcessingRequest.objects.create(
        feature=ProcessingRequest.Feature.REFRAME,
        status=ProcessingRequest.Status.PENDING,
        input_params={"mode": params.mode.value, "aspect_ratio": params.aspect_ratio, "smart": True},
        input_file_url=input_url,
    )

    try:
        result, face_count = smart_reframe_image(image_bytes, image.name, params.mode, params.aspect_ratio, proc_request)
        proc_request.status = ProcessingRequest.Status.DONE
        proc_request.save()
    except ValueError as e:
        proc_request.status = ProcessingRequest.Status.FAILED
        proc_request.save()
        from ninja.errors import HttpError
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