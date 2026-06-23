"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { 
  Mic, 
  MicOff, 
  Video, 
  VideoOff, 
  Hand, 
  MessageSquare, 
  LogOut,
  Clock,
  BookOpen,
  User,
  CheckCircle2,
  AlertTriangle,
  Loader2
} from "lucide-react"

type VerificationStatus = "verified" | "pending" | "failed"

export default function StudentLiveClassroom() {
  const [micEnabled, setMicEnabled] = useState(true)
  const [cameraEnabled, setCameraEnabled] = useState(true)
  const [handRaised, setHandRaised] = useState(false)
  const [sessionTime, setSessionTime] = useState(0)
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus>("pending")
  const [confidence, setConfidence] = useState(0)
  const [showAntiSpoof, setShowAntiSpoof] = useState(false)

  // Session timer
  useEffect(() => {
    const timer = setInterval(() => {
      setSessionTime((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // Simulate AI verification
  useEffect(() => {
    const verifyTimer = setTimeout(() => {
      setShowAntiSpoof(true)
      setTimeout(() => {
        setShowAntiSpoof(false)
        setConfidence(94)
        setVerificationStatus("verified")
      }, 3000)
    }, 2000)
    return () => clearTimeout(verifyTimer)
  }, [])

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const checkpoints = [
    { time: "10:00", done: true },
    { time: "10:30", done: false, next: true },
    { time: "11:00", done: false },
    { time: "11:30", done: false }
  ]

  return (
    <div className="min-h-screen bg-[#0D1117] text-white flex">
      {/* Main Video Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Overlay Bar */}
        <div className="absolute top-0 left-0 right-[27%] z-10 bg-gradient-to-b from-black/80 to-transparent p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-[#0EA5E9]" />
                <span className="font-semibold">CS101 - Lập trình Web</span>
              </div>
              <span className="text-[#64748B]">|</span>
              <span className="text-[#94A3B8]">Buổi 8</span>
            </div>
            <div className="flex items-center gap-2 text-[#0EA5E9]">
              <div className="w-2 h-2 rounded-full bg-[#EF4444] animate-pulse" />
              <Clock className="w-4 h-4" />
              <span className="font-mono">{formatTime(sessionTime)}</span>
            </div>
          </div>
        </div>

        {/* Main Video */}
        <div className="flex-1 relative flex items-center justify-center bg-[#0D1117]">
          {/* Placeholder for shared screen/slides */}
          <div className="w-full h-full max-w-5xl max-h-[70vh] bg-[#161B22] rounded-lg flex items-center justify-center">
            <div className="text-center">
              <div className="w-32 h-32 mx-auto mb-4 bg-[#1A3A5C] rounded-lg flex items-center justify-center">
                <Video className="w-16 h-16 text-[#0EA5E9]" />
              </div>
              <p className="text-[#94A3B8]">Màn hình chia sẻ của giảng viên</p>
              <p className="text-sm text-[#64748B] mt-2">Bài giảng: Introduction to React.js</p>
            </div>
          </div>

          {/* Lecturer PiP */}
          <div className="absolute bottom-4 left-4 w-32 h-24 rounded-xl bg-[#1A3A5C] border-2 border-white/20 overflow-hidden">
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#0A2540] to-[#1A3A5C]">
              <User className="w-8 h-8 text-white/50" />
            </div>
            <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-2 py-1">
              <p className="text-xs text-white truncate">GV: Nguyễn Văn B</p>
            </div>
          </div>
        </div>

        {/* Bottom Control Toolbar */}
        <div className="p-4 flex justify-center">
          <div className="flex items-center gap-2 bg-[#161B22]/90 backdrop-blur-sm rounded-full px-4 py-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMicEnabled(!micEnabled)}
              className={cn(
                "rounded-full w-12 h-12",
                micEnabled ? "bg-[#1A3A5C] text-white hover:bg-[#1A3A5C]/80" : "bg-[#EF4444] text-white hover:bg-[#EF4444]/80"
              )}
            >
              {micEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCameraEnabled(!cameraEnabled)}
              className={cn(
                "rounded-full w-12 h-12",
                cameraEnabled ? "bg-[#1A3A5C] text-white hover:bg-[#1A3A5C]/80" : "bg-[#EF4444] text-white hover:bg-[#EF4444]/80"
              )}
            >
              {cameraEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setHandRaised(!handRaised)}
              className={cn(
                "rounded-full w-12 h-12",
                handRaised ? "bg-[#F59E0B] text-white hover:bg-[#F59E0B]/80" : "bg-[#1A3A5C] text-white hover:bg-[#1A3A5C]/80"
              )}
            >
              <Hand className="w-5 h-5" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="rounded-full w-12 h-12 bg-[#1A3A5C] text-white hover:bg-[#1A3A5C]/80"
            >
              <MessageSquare className="w-5 h-5" />
            </Button>

            <div className="w-px h-8 bg-[#2D3748] mx-2" />

            <Button
              variant="ghost"
              size="icon"
              className="rounded-full w-12 h-12 bg-[#EF4444] text-white hover:bg-[#EF4444]/80"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* AI Verification Sidebar */}
      <div className="w-[27%] bg-[#161B22] border-l border-[#2D3748] flex flex-col">
        {/* My Camera Preview */}
        <div className="p-4 border-b border-[#2D3748]">
          <h3 className="text-sm font-medium text-[#94A3B8] mb-3">Camera của bạn</h3>
          <div className="relative aspect-square rounded-lg overflow-hidden bg-[#0D1117]">
            {cameraEnabled ? (
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1A3A5C] to-[#0A2540]">
                <User className="w-16 h-16 text-white/30" />
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-[#0D1117]">
                <VideoOff className="w-12 h-12 text-[#64748B]" />
                <p className="text-sm text-[#64748B] absolute bottom-4">Camera đã tắt</p>
              </div>
            )}
            
            {/* Face tracking brackets */}
            {cameraEnabled && verificationStatus !== "failed" && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className={cn(
                  "w-32 h-40 border-2 rounded-lg",
                  verificationStatus === "verified" ? "border-[#22C55E]" : "border-[#0EA5E9]",
                  verificationStatus === "pending" && "animate-pulse"
                )}>
                  {/* Corner brackets */}
                  <div className={cn("absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 rounded-tl", 
                    verificationStatus === "verified" ? "border-[#22C55E]" : "border-[#0EA5E9]")} />
                  <div className={cn("absolute -top-1 -right-1 w-4 h-4 border-t-2 border-r-2 rounded-tr",
                    verificationStatus === "verified" ? "border-[#22C55E]" : "border-[#0EA5E9]")} />
                  <div className={cn("absolute -bottom-1 -left-1 w-4 h-4 border-b-2 border-l-2 rounded-bl",
                    verificationStatus === "verified" ? "border-[#22C55E]" : "border-[#0EA5E9]")} />
                  <div className={cn("absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 rounded-br",
                    verificationStatus === "verified" ? "border-[#22C55E]" : "border-[#0EA5E9]")} />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* AI Verification Status */}
        <div className="p-4 border-b border-[#2D3748] space-y-4">
          <h3 className="text-sm font-medium text-[#94A3B8]">Trạng thái xác thực AI</h3>

          {/* Anti-spoof Alert */}
          {showAntiSpoof && (
            <div className="p-3 bg-[#FEF9C3]/10 border border-[#F59E0B] rounded-lg animate-pulse">
              <div className="flex items-center gap-2 text-[#F59E0B]">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">Kiểm tra chống giả mạo</span>
              </div>
              <p className="text-xs text-[#F59E0B]/80 mt-1">
                Hãy chớp mắt hoặc xoay đầu nhẹ để xác minh
              </p>
            </div>
          )}

          {/* Confidence Meter */}
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-[#94A3B8]">Độ khớp:</span>
              <span className={cn(
                "font-medium",
                confidence >= 85 ? "text-[#22C55E]" : confidence >= 70 ? "text-[#F59E0B]" : "text-[#EF4444]"
              )}>
                {confidence}%
              </span>
            </div>
            <div className="h-2 bg-[#0D1117] rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all duration-500",
                  confidence >= 85 ? "bg-gradient-to-r from-[#0A2540] to-[#22C55E]" : 
                  confidence >= 70 ? "bg-gradient-to-r from-[#0A2540] to-[#F59E0B]" :
                  "bg-gradient-to-r from-[#0A2540] to-[#EF4444]"
                )}
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>

          {/* Status Badge */}
          <div className={cn(
            "p-4 rounded-lg text-center",
            verificationStatus === "verified" && "bg-[#22C55E]/10 border border-[#22C55E]",
            verificationStatus === "pending" && "bg-[#F59E0B]/10 border border-[#F59E0B]",
            verificationStatus === "failed" && "bg-[#EF4444]/10 border border-[#EF4444]"
          )}>
            {verificationStatus === "verified" && (
              <>
                <CheckCircle2 className="w-8 h-8 mx-auto text-[#22C55E] mb-2" />
                <p className="font-medium text-[#22C55E]">Đã xác minh - Có mặt</p>
              </>
            )}
            {verificationStatus === "pending" && (
              <>
                <Loader2 className="w-8 h-8 mx-auto text-[#F59E0B] mb-2 animate-spin" />
                <p className="font-medium text-[#F59E0B]">Đang nhận diện...</p>
              </>
            )}
            {verificationStatus === "failed" && (
              <>
                <AlertTriangle className="w-8 h-8 mx-auto text-[#EF4444] mb-2" />
                <p className="font-medium text-[#EF4444]">Xác minh thất bại</p>
              </>
            )}
          </div>

          {/* Last verified */}
          {verificationStatus === "verified" && (
            <p className="text-xs text-[#64748B] text-center">
              Xác minh lần cuối: 10:32:15
            </p>
          )}
        </div>

        {/* Session Info */}
        <div className="p-4 border-b border-[#2D3748] space-y-3">
          <h3 className="text-sm font-medium text-[#94A3B8]">Thông tin buổi học</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[#64748B]">Môn học:</span>
              <span className="text-white">Lập trình Web</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#64748B]">Buổi:</span>
              <span className="text-white">Buổi 8</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#64748B]">Giảng viên:</span>
              <span className="text-white">Nguyễn Văn B</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#64748B]">Còn lại:</span>
              <span className="text-[#0EA5E9] font-mono">01:17:43</span>
            </div>
          </div>
        </div>

        {/* Check Schedule */}
        <div className="p-4 flex-1">
          <h3 className="text-sm font-medium text-[#94A3B8] mb-3">Lịch kiểm tra</h3>
          <div className="flex items-center justify-between gap-2">
            {checkpoints.map((cp, index) => (
              <div key={index} className="flex flex-col items-center">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium",
                  cp.done ? "bg-[#22C55E] text-white" :
                  cp.next ? "bg-[#0EA5E9] text-white ring-2 ring-[#0EA5E9]/50" :
                  "bg-[#2D3748] text-[#64748B]"
                )}>
                  {cp.done ? "✓" : index + 1}
                </div>
                <span className="text-xs text-[#64748B] mt-1">{cp.time}</span>
                {index < checkpoints.length - 1 && (
                  <div className="absolute top-4 left-full w-full h-0.5 bg-[#2D3748]" />
                )}
              </div>
            ))}
          </div>
          <p className="text-xs text-[#64748B] mt-4 text-center">
            Bạn cần hiện diện đủ 4 lần kiểm tra để được tính có mặt.
          </p>
        </div>
      </div>
    </div>
  )
}
