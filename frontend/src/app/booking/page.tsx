"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

const SAGE = "#A3B18A"

export default function BookingPage() {
  const [loading, setLoading] = useState(false)
  const [price, setPrice] = useState<number | null>(null)

  const handleCheckPrice = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    const form = e.target as HTMLFormElement
    
    const data = {
      guests: parseInt((form.elements.namedItem("guests") as HTMLInputElement)?.value || "2"),
      nights: parseInt((form.elements.namedItem("nights") as HTMLInputElement)?.value || "1"),
      month: parseInt((form.elements.namedItem("month") as HTMLSelectElement)?.value || "7"),
    }

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      const json = await res.json()
      if (res.ok) setPrice(json.price)
    } catch {}
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <main className="max-w-md w-full space-y-4">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">Direct Booking</h1>
          <p className="text-slate-400 text-sm">Alojamiento - Reserva sin comisiones OTA</p>
        </div>

        <Card className="border-slate-800 bg-slate-900">
          <CardHeader>
            <CardTitle className="text-white">Reserva Directa</CardTitle>
            <CardDescription>Reserva aquí y ahorra el 15-30% de comisión</CardDescription>
          </CardHeader>
          <CardContent>
            {!price ? (
              <form onSubmit={handleCheckPrice} className="space-y-3">
                <div>
                  <label className="text-sm text-slate-300">Huéspedes</label>
                  <input name="guests" type="number" defaultValue={2} min={1} max={10} className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-slate-300">Noches</label>
                  <input name="nights" type="number" defaultValue={1} min={1} max={30} className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-slate-300">Mes llegada</label>
                  <select name="month" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white">
                    <option value="7">Julio</option>
                    <option value="8">Agosto</option>
                  </select>
                </div>
                <Button type="submit" disabled={loading} className="w-full bg-white text-slate-900">
                  {loading ? "Calculando..." : "Consultar Precio"}
                </Button>
              </form>
            ) : (
              <div className="text-center space-y-4">
                <div>
                  <p className="text-slate-400 text-sm">Precio recomendado</p>
                  <p className="text-4xl font-bold" style={{ color: SAGE }}>€{price}</p>
                  <p className="text-slate-400 text-xs mt-1">Precio directo sin comisiones</p>
                </div>
                
                <div className="bg-emerald-400/10 border border-emerald-400/20 rounded-md p-3">
                  <p className="text-emerald-400 font-semibold">¡Ahorras 20% vs Booking!</p>
                  <p className="text-slate-300 text-xs mt-1">El hotel se queda con el 100% del pago</p>
                </div>

                <div className="space-y-2">
                  <input placeholder="Nombre" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white text-sm" />
                  <input placeholder="Email" type="email" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white text-sm" />
                  <input placeholder="Teléfono" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white text-sm" />
                </div>

                <Button className="w-full bg-emerald-400 text-slate-900 font-semibold">
                  Confirmar Reserva - €{price}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <p className="text-center text-slate-500 text-xs">
          <span className="badge-gray px-2 py-1 rounded">Powered by Optimus Price AI</span>
        </p>
      </main>
    </div>
  )
}