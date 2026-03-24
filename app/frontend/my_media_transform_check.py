from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform

    async def recv(self):
        print(self.track)
        frame = await self.track.recv()
        print(frame)
        return frame