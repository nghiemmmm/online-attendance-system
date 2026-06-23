"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { StatusBadge, ConfidenceBadge } from "@/components/status-badge"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { 
  Play,
  Square,
  Settings,
  Clock,
  Users,
  Pencil,
  CheckCircle2,
  User,
  Video,
  VideoOff
} from "lucide-react"

type StudentStatus = "present" | "late" | "absent" | "pending"

interface StudentTile {
  id: string
  name: string
  studentId: string
  status: StudentStatus
  confidence: "high" | "medium" | "low"
  hasCamera: boolean
  verifiedAt?: string
}

const mockStudents: StudentTile[] = [
  { id: "1", name: "Nguyễn Văn A", studentId: "SV001", status: "present", confidence: "high", hasCamera: true, verifiedAt: "10:32:15" },
  { id: "2", name: "Trần Thị B", studentId: "SV002", status: "present", confidence: "high", hasCamera: true, verifiedAt: "10:31:45" },
  { id: "3", name: "Lê Văn C", studentId: "SV003", status: "late", confidence: "medium", hasCamera: true, verifiedAt: "10:45:20" },
  { id: "4", name: "Phạm Thị D", studentId: "SV004", status: "pending", confidence: "low", hasCamera: true },
  { id: "5", name: "Hoàng Văn E", studentId: "SV005", status: "present", confidence: "high", hasCamera: true, verifiedAt: "10:30:05" },
  { id: "6", name: "Đỗ Thị F", studentId: "SV006", status: "absent", confidence: "low", hasCamera: false },
  { id: "7", name: "Vũ Văn G", studentId: "SV007", status: "present", confidence: "high", hasCamera: true, verifiedAt: "10:33:22" },
  { id: "8", name: "Bùi Thị H", studentId: "SV008", status: "present", confidence: "medium", hasCamera: true, verifiedAt: "10:35:10" },
  { id: "9", name: "Ngô Văn I", studentId: "SV009", status: "pending", confidence: "low", hasCamera: true },
  { id: "10", name: "Dương Thị K", studentId: "SV010", status: "present", confidence: "high", hasCamera: true, verifiedAt: "10:29:55" },
  { id: "11", name: "Lý Văn L", studentId: "SV011", status: "present", confidence: "high", hasCamera: true, verifiedAt: "10:34:18" },
  { id: "12", name: "Trịnh Thị M", studentId: "SV012", status: "absent", confidence: "low", hasCamera: false },
]

export default function LecturerLiveClassroom() {
  const [sessionActive, setSessionActive] = useState(true)
  const [sessionTime, setSessionTime] = useState(2537) // ~42 minutes
  const [lateMinutes, setLateMinutes] = useState(15)
  const [checkCount, setCheckCount] = useState(4)
  const [editingStudent, setEditingStudent] = useState<string | null>(null)
  const [students, setStudents] = useState(mockStudents)

  // Session timer
  useEffect(() => {
    if (!sessionActive) return
    const timer = setInterval(() => {
      setSessionTime((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [sessionActive])

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const stats = {
    present: students.filter(s => s.status === "present").length,
    late: students.filter(s => s.status === "late").length,
    absent: students.filter(s => s.status === "absent").length,
    pending: students.filter(s => s.status === "pending").length,
    total: students.length
  }

  const handleStatusChange = (studentId: string, newStatus: StudentStatus) => {
    setStudents(prev => prev.map(s => 
      s.id === studentId ? { ...s, status: newStatus } : s
    ))
    setEditingStudent(null)
  }

  return (
    <div className="min-h-screen bg-[#0D1117] text-white flex">
      {/* Main Grid Area */}
      <div className="flex-1 flex flex-col p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold">CS101 - Lập trình Web</h1>
            <span className="px-3 py-1 bg-[#22C55E]/20 text-[#22C55E] rounded-full text-sm font-medium">
              Buổi 8
            </span>
          </div>
          <div className="flex items-center gap-2">
            {sessionActive && (
              <div className="flex items-center gap-2 text-[#0EA5E9]">
                <div className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse" />
                <Clock className="w-4 h-4" />
                <span className="font-mono">{formatTime(sessionTime)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Student Grid */}
        <div className="flex-1 grid grid-cols-4 gap-3 overflow-y-auto">
          {students.map((student) => (
            <div
              key={student.id}
              className={cn(
                "relative rounded-lg overflow-hidden bg-[#161B22] border-2 aspect-video",
                student.status === "present" && "border-[#22C55E]",
                student.status === "late" && "border-[#F59E0B]",
                student.status === "absent" && "border-[#EF4444]",
                student.status === "pending" && "border-[#0EA5E9]"
              )}
            >
              {/* Video / Placeholder */}
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1A3A5C] to-[#0A2540]">
                {student.hasCamera ? (
                  <User className="w-12 h-12 text-white/30" />
                ) : (
                  <div className="text-center">
                    <VideoOff className="w-8 h-8 text-[#64748B] mx-auto" />
                    <p className="text-xs text-[#64748B] mt-1">Không có camera</p>
                  </div>
                )}
              </div>

              {/* Status badge */}
              <div className={cn(
                "absolute top-2 right-2 w-3 h-3 rounded-full",
                student.status === "present" && "bg-[#22C55E]",
                student.status === "late" && "bg-[#F59E0B]",
                student.status === "absent" && "bg-[#EF4444]",
                student.status === "pending" && "bg-[#0EA5E9] animate-pulse"
              )} />

              {/* Name overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium truncate">{student.name}</p>
                    <p className="text-xs text-[#94A3B8]">{student.studentId}</p>
                  </div>
                  <button
                    onClick={() => setEditingStudent(student.id)}
                    className="p-1 hover:bg-white/10 rounded"
                  >
                    <Pencil className="w-3 h-3 text-[#94A3B8]" />
                  </button>
                </div>
              </div>

              {/* Edit overlay */}
              {editingStudent === student.id && (
                <div className="absolute inset-0 bg-black/90 flex flex-col items-center justify-center p-2 gap-2">
                  <p className="text-sm font-medium mb-2">Sửa trạng thái</p>
                  {(["present", "late", "absent"] as StudentStatus[]).map((status) => (
                    <button
                      key={status}
                      onClick={() => handleStatusChange(student.id, status)}
                      className={cn(
                        "w-full py-1.5 rounded text-xs font-medium",
                        status === "present" && "bg-[#22C55E] text-white",
                        status === "late" && "bg-[#F59E0B] text-white",
                        status === "absent" && "bg-[#EF4444] text-white"
                      )}
                    >
                      {status === "present" ? "Có mặt" : status === "late" ? "Muộn" : "Vắng"}
                    </button>
                  ))}
                  <button
                    onClick={() => setEditingStudent(null)}
                    className="text-xs text-[#64748B] mt-1"
                  >
                    Hủy
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Right Sidebar - Command Center */}
      <div className="w-[32%] bg-[#161B22] border-l border-[#2D3748] flex flex-col overflow-hidden">
        {/* Attendance Summary */}
        <div className="p-4 border-b border-[#2D3748]">
          <h3 className="text-sm font-medium text-[#94A3B8] mb-4">Thống kê điểm danh</h3>
          
          {/* Donut Chart Placeholder */}
          <div className="flex items-center gap-4 mb-4">
            <div className="relative w-24 h-24">
              <svg className="w-full h-full" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#2D3748"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#22C55E"
                  strokeWidth="3"
                  strokeDasharray={`${(stats.present / stats.total) * 100}, 100`}
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#F59E0B"
                  strokeWidth="3"
                  strokeDasharray={`${(stats.late / stats.total) * 100}, 100`}
                  strokeDashoffset={`-${(stats.present / stats.total) * 100}`}
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#EF4444"
                  strokeWidth="3"
                  strokeDasharray={`${(stats.absent / stats.total) * 100}, 100`}
                  strokeDashoffset={`-${((stats.present + stats.late) / stats.total) * 100}`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-lg font-bold">{stats.total}</span>
              </div>
            </div>
            <div className="flex-1 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-[#22C55E]" />
                  <span className="text-sm text-[#94A3B8]">Có mặt</span>
                </div>
                <span className="font-medium">{stats.present}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                  <span className="text-sm text-[#94A3B8]">Muộn</span>
                </div>
                <span className="font-medium">{stats.late}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                  <span className="text-sm text-[#94A3B8]">Vắng</span>
                </div>
                <span className="font-medium">{stats.absent}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Session Controls */}
        <div className="p-4 border-b border-[#2D3748] space-y-3">
          <div className="flex items-center gap-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              sessionActive ? "bg-[#22C55E] animate-pulse" : "bg-[#64748B]"
            )} />
            <span className="text-sm font-medium">
              {sessionActive ? "Đang điểm danh — Buổi 8" : "Chưa bắt đầu"}
            </span>
          </div>

          {!sessionActive ? (
            <Button 
              className="w-full bg-[#22C55E] hover:bg-[#22C55E]/80 text-white"
              onClick={() => setSessionActive(true)}
            >
              <Play className="w-4 h-4 mr-2" />
              Bắt đầu phiên điểm danh
            </Button>
          ) : (
            <Button 
              className="w-full bg-[#EF4444] hover:bg-[#EF4444]/80 text-white"
              onClick={() => setSessionActive(false)}
            >
              <Square className="w-4 h-4 mr-2" />
              Kết thúc buổi học
            </Button>
          )}

          {/* Settings */}
          <div className="pt-3 border-t border-[#2D3748] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#94A3B8]">Phút muộn tối đa:</span>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  value={lateMinutes}
                  onChange={(e) => setLateMinutes(Number(e.target.value))}
                  className="w-16 h-8 bg-[#0D1117] border-[#2D3748] text-center"
                />
                <span className="text-sm text-[#64748B]">phút</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#94A3B8]">Số lần kiểm tra:</span>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  value={checkCount}
                  onChange={(e) => setCheckCount(Number(e.target.value))}
                  className="w-16 h-8 bg-[#0D1117] border-[#2D3748] text-center"
                  min={1}
                  max={10}
                />
                <span className="text-sm text-[#64748B]">lần</span>
              </div>
            </div>
          </div>
        </div>

        {/* Live Recognition Feed */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-4 pb-2">
            <h3 className="text-sm font-medium text-[#94A3B8]">
              Nhật ký nhận diện
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
            {students
              .filter(s => s.status !== "absent" || s.verifiedAt)
              .sort((a, b) => (b.verifiedAt || "").localeCompare(a.verifiedAt || ""))
              .map((student) => (
                <div
                  key={student.id}
                  className="flex items-center gap-3 p-2 bg-[#0D1117] rounded-lg"
                >
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-[#1A3A5C] text-white text-xs">
                      {student.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{student.name}</p>
                    <p className="text-xs text-[#64748B]">{student.studentId}</p>
                  </div>
                  <ConfidenceBadge level={student.confidence} />
                  <StatusBadge status={student.status} showIcon={false} />
                  <button
                    onClick={() => setEditingStudent(student.id)}
                    className="p-1 hover:bg-white/10 rounded"
                  >
                    <Pencil className="w-3 h-3 text-[#64748B]" />
                  </button>
                </div>
              ))}
          </div>
        </div>

        {/* Footer Stats */}
        <div className="p-4 border-t border-[#2D3748] text-sm text-[#64748B]">
          <div className="flex items-center justify-between">
            <span>Tổng sĩ số: {stats.total}</span>
            <span>Đã nhận diện: {stats.present + stats.late}</span>
            <span>Chưa nhận diện: {stats.absent + stats.pending}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
