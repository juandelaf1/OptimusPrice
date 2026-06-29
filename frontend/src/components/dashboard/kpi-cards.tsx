"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { TrendingUp, Euro, CalendarDays, Bell, LucideIcon } from "lucide-react"

type Stats = {
  recommended_price: number
  monthly_revenue: number
  revenue_impact: number
  occupancy_forecast: number
  total_reservations: number
  active_alerts: number
  critical_alerts: number
}

type KPIItem = {
  label: string
  value: string
  change: string
  positive: boolean
  icon: LucideIcon
}

const DEFAULTS: KPIItem[] = [
  { label: "Recommended Price", value: "€--", change: "Loading...", positive: true, icon: Euro },
  { label: "Revenue Impact", value: "€--", change: "Loading...", positive: true, icon: TrendingUp },
  { label: "Occupancy Forecast", value: "--%", change: "Loading...", positive: true, icon: CalendarDays },
  { label: "Active Alerts", value: "-", change: "Loading...", positive: false, icon: Bell },
]

export default function KPICards({ refreshKey = 0 }: { refreshKey?: number }) {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    fetch("/api/stats")
      .then(r => r.json())
      .then(setStats)
      .catch(() => {})
  }, [refreshKey])

  function fmt(v: number): string {
    return v >= 1000 ? `${(v / 1000).toFixed(1)}K` : `${v.toFixed(0)}`
  }

  const items: KPIItem[] = stats ? [
    { label: "Recommended Price", value: `€${stats.recommended_price}`, change: `${fmt(stats.monthly_revenue)} monthly revenue`, positive: true, icon: Euro },
    { label: "Revenue Impact", value: `€${fmt(stats.revenue_impact)}`, change: "+30% potential uplift", positive: true, icon: TrendingUp },
    { label: "Occupancy Forecast", value: `${stats.occupancy_forecast}%`, change: `${stats.total_reservations} reservations this month`, positive: true, icon: CalendarDays },
    { label: "Active Alerts", value: `${stats.active_alerts}`, change: `${stats.critical_alerts} critical · ${stats.active_alerts - stats.critical_alerts} warning`, positive: stats.critical_alerts === 0, icon: Bell },
  ] : DEFAULTS

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {items.map((kpi) => {
        const Icon = kpi.icon
        return (
          <div key={kpi.label} className="rounded-xl border border-white/5 bg-white/[0.03] p-4">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <p className="text-xs font-medium text-slate-400">{kpi.label}</p>
                <p className="text-2xl font-bold text-white">{kpi.value}</p>
                <p className={cn("text-xs", kpi.positive ? "text-emerald-400" : "text-red-400")}>{kpi.change}</p>
              </div>
              <div className={cn("flex size-10 items-center justify-center rounded-lg", kpi.positive ? "bg-emerald-400/10" : "bg-red-400/10")}>
                <Icon className={cn("size-5", kpi.positive ? "text-emerald-400" : "text-red-400")} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
