"use client"

import { useState, useEffect } from "react"
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp } from "lucide-react"

type DataPoint = { day: string; price: number }

const FALLBACK: DataPoint[] = [
  { day: "Mon", price: 168 }, { day: "Tue", price: 172 }, { day: "Wed", price: 165 },
  { day: "Thu", price: 178 }, { day: "Fri", price: 184 }, { day: "Sat", price: 192 }, { day: "Sun", price: 188 },
]

export default function PriceChart({ refreshKey = 0 }: { refreshKey?: number }) {
  const [data, setData] = useState<DataPoint[]>(FALLBACK)

  useEffect(() => {
    fetch("/api/history?days=7")
      .then(r => r.json())
      .then((rows: { date: string; price: number }[]) => {
        if (rows && rows.length > 0) {
          setData(rows.map(r => ({ day: r.date.slice(5), price: r.price })))
        }
      })
      .catch(() => {})
  }, [refreshKey])

  return (
    <Card className="border-white/5 bg-white/[0.03]">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
          <TrendingUp className="size-3.5 text-emerald-400" />
          Price Trends (7 days)
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-2">
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} domain={['dataMin - 10', 'dataMax + 10']} />
            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: '#94a3b8' }} formatter={(value: number) => [`€${value}`, "Price"]} />
            <Area type="monotone" dataKey="price" stroke="#34d399" strokeWidth={2} fill="url(#chartGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
