"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Minus, Search } from "lucide-react"

type Competitor = {
  ota: string
  yesterday: number
  today: number
  gap_pct: number
  trend: string
}

function TrendIcon({ trend }: { trend: string }) {
  if (trend === "up") return <TrendingUp className="size-3 text-emerald-400" />
  if (trend === "down") return <TrendingDown className="size-3 text-red-400" />
  return <Minus className="size-3 text-slate-400" />
}

function GapBadge({ gap }: { gap: number }) {
  const isPositive = gap >= 0
  return (
    <Badge className={isPositive ? "bg-emerald-400/10 text-emerald-400 border-emerald-400/20" : "bg-red-400/10 text-red-400 border-red-400/20"}>
      {isPositive ? "+" : ""}{gap}%
    </Badge>
  )
}

export default function MarketIntel({ refreshKey = 0 }: { refreshKey?: number }) {
  const [competitors, setCompetitors] = useState<Competitor[]>([])

  useEffect(() => {
    fetch("/api/competitors")
      .then(r => r.json())
      .then(setCompetitors)
      .catch(() => {})
  }, [refreshKey])

  return (
    <Card className="border-white/5 bg-white/[0.03]">
      <CardHeader className="pb-3">
        <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
          <Search className="size-3.5 text-emerald-400" />
          Market Intelligence
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left text-xs font-medium text-slate-400 px-4 py-2">OTA</th>
                <th className="text-right text-xs font-medium text-slate-400 px-4 py-2">Yesterday</th>
                <th className="text-right text-xs font-medium text-slate-400 px-4 py-2">Today</th>
                <th className="text-right text-xs font-medium text-slate-400 px-4 py-2">Gap</th>
                <th className="text-right text-xs font-medium text-slate-400 px-4 py-2">Trend</th>
              </tr>
            </thead>
            <tbody>
              {competitors.length === 0 ? (
                <tr><td colSpan={5} className="text-center text-slate-500 text-xs py-8">Loading competitor data...</td></tr>
              ) : (
                <>
                  {competitors.map((c) => (
                    <tr key={c.ota} className="border-b border-white/5">
                      <td className="px-4 py-2.5 text-white font-medium">{c.ota}</td>
                      <td className="px-4 py-2.5 text-right text-slate-300">€{c.yesterday}</td>
                      <td className="px-4 py-2.5 text-right text-white font-medium">€{c.today}</td>
                      <td className="px-4 py-2.5 text-right"><GapBadge gap={c.gap_pct} /></td>
                      <td className="px-4 py-2.5 text-right"><TrendIcon trend={c.trend} /></td>
                    </tr>
                  ))}
                  <tr className="border-t-2 border-emerald-400/20 bg-emerald-400/5">
                    <td className="px-4 py-2.5 text-emerald-400 font-semibold">★ OPT AI</td>
                    <td className="px-4 py-2.5 text-right text-emerald-400">€--</td>
                    <td className="px-4 py-2.5 text-right text-emerald-400 font-semibold">
                      €{competitors.length > 0
                        ? Math.round(competitors.reduce((s, c) => s + c.today, 0) / competitors.length * 1.08)
                        : 184}
                    </td>
                    <td className="px-4 py-2.5 text-right"><GapBadge gap={5.1} /></td>
                    <td className="px-4 py-2.5 text-right"><TrendIcon trend="up" /></td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
