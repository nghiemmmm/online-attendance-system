"use client"

import { cn } from "@/lib/utils"

type StatusType = "present" | "late" | "absent" | "pending"

interface StatusBadgeProps {
  status: StatusType
  className?: string
  showIcon?: boolean
}

const statusConfig: Record<StatusType, { label: string; bgClass: string; textClass: string; icon: string }> = {
  present: {
    label: "Có mặt",
    bgClass: "bg-[#DCFCE7]",
    textClass: "text-[#166534]",
    icon: "✓"
  },
  late: {
    label: "Muộn",
    bgClass: "bg-[#FEF9C3]",
    textClass: "text-[#92400E]",
    icon: "⏰"
  },
  absent: {
    label: "Vắng",
    bgClass: "bg-[#FEE2E2]",
    textClass: "text-[#991B1B]",
    icon: "✗"
  },
  pending: {
    label: "Chờ duyệt",
    bgClass: "bg-[#DBEAFE]",
    textClass: "text-[#1E40AF]",
    icon: "⏳"
  }
}

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium",
        config.bgClass,
        config.textClass,
        className
      )}
    >
      {showIcon && <span>{config.icon}</span>}
      {config.label}
    </span>
  )
}

export function RoleBadge({ role, className }: { role: "student" | "lecturer" | "admin"; className?: string }) {
  const roleConfig = {
    student: { label: "Sinh viên", bgClass: "bg-blue-100", textClass: "text-blue-700" },
    lecturer: { label: "Giảng viên", bgClass: "bg-purple-100", textClass: "text-purple-700" },
    admin: { label: "Quản trị viên", bgClass: "bg-[#0A2540]", textClass: "text-white" }
  }

  const config = roleConfig[role]

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium",
        config.bgClass,
        config.textClass,
        className
      )}
    >
      {config.label}
    </span>
  )
}

export function ConfidenceBadge({ level }: { level: "high" | "medium" | "low" }) {
  const config = {
    high: { label: "Cao", bgClass: "bg-[#DCFCE7]", textClass: "text-[#166534]" },
    medium: { label: "Trung bình", bgClass: "bg-[#FEF9C3]", textClass: "text-[#92400E]" },
    low: { label: "Thấp", bgClass: "bg-[#FEE2E2]", textClass: "text-[#991B1B]" }
  }

  const conf = config[level]

  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-xs font-medium", conf.bgClass, conf.textClass)}>
      {conf.label}
    </span>
  )
}
