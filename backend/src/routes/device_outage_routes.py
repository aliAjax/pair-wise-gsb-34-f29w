from fastapi import APIRouter

from src.controllers.device_outage_controller import (
    cancel_outage,
    change_outage_window,
    get_batch,
    get_outage,
    list_batches,
    list_outages,
    occupied_preview,
    resume_batch,
    review_draft,
    submit_outages,
)

router = APIRouter(prefix="/api/device-outage", tags=["DeviceOutage"])
router.get("", response_model=None)(list_outages)
router.get("/batch", response_model=None)(list_batches)
router.get("/batch/{batch_id}", response_model=None)(get_batch)
router.get("/occupied", response_model=None)(occupied_preview)
router.get("/{outage_id}", response_model=None)(get_outage)
router.post("", response_model=None)(submit_outages)
router.post("/batch/{batch_id}/resume", response_model=None)(resume_batch)
router.post("/{outage_id}/review", response_model=None)(review_draft)
router.patch("/{outage_id}/window", response_model=None)(change_outage_window)
router.post("/{outage_id}/cancel", response_model=None)(cancel_outage)
