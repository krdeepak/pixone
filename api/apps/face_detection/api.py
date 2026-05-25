from ninja import Router, File
from ninja.files import UploadedFile
from apps.core.models import ProcessingRequest, ProcessingResult
from apps.core.storage import get_storage
from .schemas import FaceDetectionResponse, FaceRectSchema
from .services import get_detector

router = Router(tags=["face-detection"])


@router.post("/", response=FaceDetectionResponse)
def detect_faces(request, image: UploadedFile = File(...)):
    image_bytes = b"".join(image.chunks())
    input_url = get_storage().upload(image_bytes, folder="uploads", filename=image.name)

    proc_request = ProcessingRequest.objects.create(
        feature=ProcessingRequest.Feature.FACE_DETECTION,
        status=ProcessingRequest.Status.PENDING,
        input_params={"filename": image.name},
        input_file_url=input_url,
    )

    try:
        detector = get_detector()
        faces = detector.detect(image_bytes)

        face_dicts = [
            {"x": f.x, "y": f.y, "width": f.width, "height": f.height,
             "confidence": f.confidence, "landmarks": f.landmarks}
            for f in faces
        ]

        ProcessingResult.objects.create(
            request=proc_request,
            output_url="",
            metadata={"faces": face_dicts, "face_count": len(faces)},
        )
        proc_request.status = ProcessingRequest.Status.DONE
        proc_request.save()

    except Exception as e:
        proc_request.status = ProcessingRequest.Status.FAILED
        proc_request.save()
        raise e

    return FaceDetectionResponse(
        request_id=proc_request.id,
        faces=[FaceRectSchema(**f) for f in face_dicts],
        face_count=len(faces),
    )
