from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import uuid
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRelay
from app.frontend.my_media_transform_check import VideoTransformTrack

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
@router.post("/offer", include_in_schema=False)
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

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
            pc.addTrack(VideoTransformTrack(relay.subscribe(track), transform=""))

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

    return JSONResponse(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type},
    )
