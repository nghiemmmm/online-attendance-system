from aiortc import RTCPeerConnection
from aiortc.contrib.media import MediaRelay

class WebRTCManager:
    """Manage WebRTC PeerConnections, DataChannels, and MediaRelays."""

    def __init__(self) -> None:
        self.pcs: set[RTCPeerConnection] = set()
        self.dcs: set[any] = set()
        self.relay: MediaRelay = MediaRelay()

    def add_peer_connection(self, pc: RTCPeerConnection) -> None:
        """Add peer connection to the managed set."""
        self.pcs.add(pc)

    def discard_peer_connection(self, pc: RTCPeerConnection) -> None:
        """Discard peer connection from the managed set."""
        self.pcs.discard(pc)

    def add_data_channel(self, channel: any) -> None:
        """Add data channel to the managed set."""
        self.dcs.add(channel)

    def discard_data_channel(self, channel: any) -> None:
        """Discard data channel from the managed set."""
        self.dcs.discard(channel)

    async def close_all(self) -> None:
        """Close all managed peer connections and clear sets."""
        for pc in list(self.pcs):
            await pc.close()
        self.pcs.clear()
        self.dcs.clear()


# Create singleton instance
webrtc_manager = WebRTCManager()

def get_webrtc_manager() -> WebRTCManager:
    """Dependency provider for WebRTCManager."""
    return webrtc_manager
