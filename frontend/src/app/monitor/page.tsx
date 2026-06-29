"use client"

import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Search, RefreshCw } from "lucide-react"

const DATA = [
  { day: "Mon", booking: 165, expedia: 170, hotels: 178, trivago: 166, optimus: 180 },
  { day: "Tue", booking: 167, expedia: 171, hotels: 177, trivago: 167, optimus: 182 },
  { day: "Wed", booking: 164, expedia: 169, hotels: 179, trivago: 165, optimus: 181 },
  { day: "Thu", booking: 168, expedia: 172, hotels: 176, trivago: 168, optimus: 183 },
  { day: "Fri", booking: 169, expedia: 172, hotels: 175, trivago: 168, optimus: 184 },
  { day: "Sat", booking: 170, expedia: 173, hotels: 174, trivago: 169, optimus: 185 },
  { day: "Sun", booking: 169, expedia: 172, hotels: 175, trivago: 168, optimus: 184 },
]

const MONITOR_COLORS = ["#64748b", "#3b82f6", "#f59e0b", "#06b6d4", "#34d399"]

export default function MonitorPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Market Monitor</h1>
          <p className="text-sm text-slate-400 mt-0.5">Live competitor pricing — auto-refresh every 30s</p>
        </div>
        <Badge className="bg-emerald-400/10 text-emerald-400 border-emerald-400/20 flex items-center gap-1.5 px-3 py-1.5">
          <RefreshCw className="size-3" /> Live
        </Badge>
      </div>

      {/* Price Comparison Chart */}
      <Card className="border-white/5 bg-white/[0.03]">
        <CardHeader>
          <CardTitle className="text-white text-sm font-medium">Price Position — 7 Day Trend</CardTitle>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#94a3b8' }}
                formatter={(value: number, name: string) => [`€${value}`, name]}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              {Object.keys(DATA[0]).filter(k => k !== "day").map((key, i) => (
                <Line key={key} type="monotone" dataKey={key} stroke={MONITOR_COLORS[i]} strokeWidth={key === "optimus" ? 3 : 1.5} dot={false} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Price Position Card */}
      <div className="grid lg:grid-cols-2 gap-4">
        <Card className="border-white/5 bg-white/[0.03]">
          <CardHeader>
            <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
              <Search className="size-3.5 text-emerald-400" /> Price Position
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative h-8 bg-white/5 rounded-full overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-between px-4 text-[10px] text-slate-500">
                <span>Below Market</span>
                <span>At Market</span>
                <span>Above Market</span>
              </div>
              <div className="absolute top-0 bottom-0 left-[70%] w-1 bg-emerald-400 rounded-full" style={{ boxShadow: '0 0 8px rgba(52,211,153,0.5)' }} />
            </div>
            <p className="text-xs text-slate-400 mt-3 text-center">OPT AI is positioned <span className="text-emerald-400 font-medium">above market</span> — premium positioning with justified value</p>
          </CardContent>
        </Card>

        <Card className="border-white/5 bg-white/[0.03]">
          <CardHeader>
            <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
              <TrendingUp className="size-3.5 text-emerald-400" /> Market Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "Average OTA Price", value: "€171", change: "+1.2%", up: true },
              { label: "Lowest Competitor", value: "€165", change: "Trivago", up: false },
              { label: "Highest Competitor", value: "€175", change: "Hotels.com", up: false },
              { label: "Your Advantage", value: "+€13", change: "vs market avg", up: true },
            ].map((s, i) => (
              <div key={i} className="flex items-center justify-between">
                <p className="text-xs text-slate-400">{s.label}</p>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">{s.value}</span>
                  <span className="text-xs text-slate-500">{s.change}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
