from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uuid
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRelay
from fastapi.templating import Jinja2Templates
from app.webrtc.webrtc import VideoTransformTrack


templates = Jinja2Templates(directory="app/templates")
# Global state
pcs = set()
dcs = set()
relay = MediaRelay()
root_logger = logging.getLogger("app")

router = APIRouter(
    prefix="/webrtc",
    tags=["webrtc"]
)

@router.get("/offer", include_in_schema=False)
async def offer(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/offer", include_in_schema=False)
async def offer(request: Request):
    pc: Optional[RTCPeerConnection] = None
    try:
        try:
            params = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

        sdp = params.get("sdp") if isinstance(params, dict) else None
        offer_type = params.get("type") if isinstance(params, dict) else None
        ma_buoi_hoc = params.get("ma_buoi_hoc") if isinstance(params, dict) else None

        if not sdp or not offer_type:
            raise HTTPException(status_code=422, detail="Missing required fields: sdp, type")

        try:
            offer = RTCSessionDescription(sdp=sdp, type=offer_type)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid WebRTC offer") from exc

        pc = RTCPeerConnection()
        pc_id = "PeerConnection(%s)" % uuid.uuid4()
        pcs.add(pc)

        def log_info(msg, *args):
            root_logger.info(pc_id + " " + msg, *args)

        # Media recorder
        recorder = MediaBlackhole()

        @pc.on("datachannel")
        def on_datachannel(channel):
            dcs.add(channel)

            @channel.on("message")
            def on_message(message):
                if isinstance(message, str) and message.startswith("ping"):
                    channel.send("pong" + message[4:])

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            log_info("Connection state is %s", pc.connectionState)
            if pc.connectionState == "failed":
                await pc.close()
                pcs.discard(pc)

        @pc.on("track")
        def on_track(track):
            log_info("Track %s received", track.kind)

            if track.kind == "video":
                vt = VideoTransformTrack(relay.subscribe(track), ma_buoi_hoc=ma_buoi_hoc)
                pc.addTrack(vt)


            @track.on("ended")
            async def on_ended():
                log_info("Track %s ended", track.kind)
                await recorder.stop()

        # Handle WebRTC offer
        await pc.setRemoteDescription(offer)
        await recorder.start()

        # Send answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        if pc.localDescription is None or not pc.localDescription.sdp:
            raise HTTPException(status_code=500, detail="Failed to generate SDP answer")

        return JSONResponse(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type},
        )
    except HTTPException:
        if pc is not None:
            pcs.discard(pc)
            await pc.close()
        raise
    except Exception:
        if pc is not None:
            pcs.discard(pc)
            await pc.close()
        root_logger.exception("Unexpected error while processing /webrtc/offer")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing WebRTC offer",
        )


@router.post("/message", include_in_schema=False)
async def message(request: Request):
    try:
        try:
            params = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

        message_text = params.get("message") if isinstance(params, dict) else None
        if not message_text:
            raise HTTPException(status_code=422, detail="Missing required field: message")

        for dc in dcs:
            dc.send(message_text)

        return JSONResponse({"message": "Message sent"})
    except HTTPException:
        raise
    except Exception:
        root_logger.exception("Unexpected error while processing /webrtc/message")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while sending message",
        )
