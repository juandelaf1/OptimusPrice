"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, Users } from "lucide-react"

type ReservationActivity = {
  id: string
  guest_name: string
  guests: number
  nights: number
  check_in: string
  final_price: number
  status: string
}

export default function ActivityFeed({ refreshKey = 0 }: { refreshKey?: number }) {
  const [activities, setActivities] = useState<ReservationActivity[]>([])

  useEffect(() => {
    fetch("/api/reservations")
      .then(r => r.json())
      .then((data: ReservationActivity[]) => setActivities(data.slice(0, 4)))
      .catch(() => {})
  }, [refreshKey])

  return (
    <Card className="border-white/5 bg-white/[0.03]">
      <CardHeader className="pb-3">
        <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
          <Clock className="size-3.5 text-emerald-400" />
          Recent Customer Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-white/5">
          {activities.length === 0 ? (
            <p className="text-center text-slate-500 text-xs py-8">No recent activity</p>
          ) : (
            activities.map((a) => (
              <div key={a.id} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className="flex size-8 items-center justify-center rounded-full bg-emerald-400/10">
                    <Users className="size-3.5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{a.guest_name}</p>
                    <p className="text-xs text-slate-400">{a.guests} guests · {a.nights} nights · {a.check_in}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-white">€{a.final_price}</p>
                  <Badge className={a.status === "confirmed" ? "bg-emerald-400/10 text-emerald-400 border-emerald-400/20" : "bg-amber-400/10 text-amber-400 border-amber-400/20"}>
                    {a.status}
                  </Badge>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
