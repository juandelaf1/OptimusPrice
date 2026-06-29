"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CalendarCheck, Search, Filter } from "lucide-react"

type Reservation = {
  id: string
  guest_name: string
  email: string
  check_in: string
  check_out: string
  nights: number
  guests: number
  room_type: string
  final_price: number
  status: string
}

export default function ReservationsPage() {
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("/api/reservations")
      .then(r => r.json())
      .then(setReservations)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Reservations</h1>
          <p className="text-sm text-slate-400 mt-0.5">Manage bookings and direct reservations</p>
        </div>
        <Badge className="bg-emerald-400/10 text-emerald-400 border-emerald-400/20 px-3 py-1.5">
          <CalendarCheck className="size-3 mr-1" /> {reservations.length} total
        </Badge>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-lg border border-white/5 bg-white/5 px-3 py-1.5 flex-1 max-w-xs">
          <Search className="size-3.5 text-slate-500" />
          <input type="text" placeholder="Search guests..." className="flex-1 bg-transparent text-sm text-white placeholder:text-slate-600 focus:outline-none" />
        </div>
        <button className="flex items-center gap-1.5 rounded-lg border border-white/5 px-3 py-1.5 text-xs text-slate-400 hover:text-white transition-colors">
          <Filter className="size-3" /> Filter
        </button>
      </div>

      <Card className="border-white/5 bg-white/[0.03]">
        <CardContent className="p-0">
          {loading ? (
            <p className="text-center text-slate-500 text-xs py-8">Loading reservations...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left text-xs font-medium text-slate-400 px-4 py-3">Guest</th>
                    <th className="text-left text-xs font-medium text-slate-400 px-4 py-3">Check-in</th>
                    <th className="text-left text-xs font-medium text-slate-400 px-4 py-3">Check-out</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-4 py-3">Nights</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-4 py-3">Guests</th>
                    <th className="text-left text-xs font-medium text-slate-400 px-4 py-3">Room</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Amount</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {reservations.length === 0 ? (
                    <tr><td colSpan={8} className="text-center text-slate-500 text-xs py-8">No reservations yet</td></tr>
                  ) : (
                    reservations.map((r) => (
                      <tr key={r.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                        <td className="px-4 py-3">
                          <p className="text-white font-medium">{r.guest_name}</p>
                          <p className="text-xs text-slate-500">{r.email}</p>
                        </td>
                        <td className="px-4 py-3 text-slate-300">{r.check_in}</td>
                        <td className="px-4 py-3 text-slate-300">{r.check_out}</td>
                        <td className="px-4 py-3 text-center text-white">{r.nights}</td>
                        <td className="px-4 py-3 text-center text-white">{r.guests}</td>
                        <td className="px-4 py-3 text-slate-300">{r.room_type}</td>
                        <td className="px-4 py-3 text-right text-white font-medium">€{r.final_price}</td>
                        <td className="px-4 py-3 text-center">
                          <Badge className={
                            r.status === "confirmed" ? "bg-emerald-400/10 text-emerald-400 border-emerald-400/20" :
                            r.status === "pending" ? "bg-amber-400/10 text-amber-400 border-amber-400/20" :
                            "bg-red-400/10 text-red-400 border-red-400/20"
                          }>{r.status}</Badge>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
