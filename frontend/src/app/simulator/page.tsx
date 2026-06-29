"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { SlidersHorizontal, Euro, TrendingUp } from "lucide-react"

type PredictResult = {
  price: number
  features_used: number
}

export default function SimulatorPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PredictResult | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const data = {
      property_type: (form.elements.namedItem("property_type") as HTMLSelectElement)?.value || "hotel",
      guests: parseInt((form.elements.namedItem("guests") as HTMLInputElement)?.value || "2"),
      nights: parseInt((form.elements.namedItem("nights") as HTMLInputElement)?.value || "1"),
      month: parseInt((form.elements.namedItem("month") as HTMLSelectElement)?.value || "7"),
      lead_time: parseInt((form.elements.namedItem("lead_time") as HTMLInputElement)?.value || "14"),
    }
    setLoading(true)
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      const json = await res.json()
      if (res.ok) setResult(json)
      else console.error("Prediction error:", json.detail)
    } catch (err: unknown) {
      console.error("Prediction error:", err instanceof Error ? err.message : "Unknown error")
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Price Simulator</h1>
        <p className="text-sm text-slate-400 mt-0.5">What-if analysis — change variables and see instant impact</p>
      </div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* Controls */}
        <Card className="lg:col-span-2 border-white/5 bg-white/[0.03]">
          <CardHeader>
            <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
              <SlidersHorizontal className="size-3.5 text-emerald-400" /> Scenario Parameters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 mb-1 block">Property Type</label>
                  <select name="property_type" className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-400/50 focus:outline-none">
                    <option value="hotel" className="bg-slate-900">Hotel</option>
                    <option value="airbnb" className="bg-slate-900">Airbnb</option>
                    <option value="hostel" className="bg-slate-900">Hostel</option>
                    <option value="rural" className="bg-slate-900">Rural House</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 mb-1 block">Lead Time (days)</label>
                  <input name="lead_time" type="number" defaultValue={14} min={0} max={365} className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-400/50 focus:outline-none" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 mb-1 block">Guests</label>
                  <input name="guests" type="number" defaultValue={2} min={1} max={20} className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-400/50 focus:outline-none" />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 mb-1 block">Nights</label>
                  <input name="nights" type="number" defaultValue={1} min={1} max={30} className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-400/50 focus:outline-none" />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 mb-1 block">Month</label>
                  <select name="month" defaultValue="7" className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-400/50 focus:outline-none">
                    <option value="6" className="bg-slate-900">June</option>
                    <option value="7" className="bg-slate-900">July</option>
                    <option value="8" className="bg-slate-900">August</option>
                    <option value="9" className="bg-slate-900">September</option>
                  </select>
                </div>
              </div>

              <Button type="submit" disabled={loading}
                className="w-full bg-emerald-400 text-slate-900 hover:bg-emerald-500 font-semibold h-10 text-sm">
                {loading ? "Calculating..." : "Simulate Price"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="lg:col-span-3 space-y-4">
          {!result ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[300px] border border-dashed border-white/5 rounded-xl bg-white/[0.02]">
              <SlidersHorizontal className="size-10 text-slate-700 mb-3" />
              <p className="text-slate-500 text-sm">Adjust the parameters and run a simulation</p>
            </div>
          ) : (
            <>
              <Card className="border-white/5 bg-gradient-to-br from-emerald-400/10 to-transparent">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Optimized Price</p>
                      <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-5xl font-bold text-white">€{result.price}</span>
                        <span className="text-sm text-slate-400">/ night</span>
                      </div>
                      <div className="flex gap-2 mt-3">
                        <Badge className="bg-emerald-400/10 text-emerald-400 border-emerald-400/20">
                          <TrendingUp className="size-3 mr-1" /> Recommended
                        </Badge>
                        <Badge className="bg-blue-400/10 text-blue-400 border-blue-400/20">
                          {result.features_used} features
                        </Badge>
                      </div>
                    </div>
                    <div className="size-14 rounded-full bg-emerald-400/20 flex items-center justify-center">
                      <Euro className="size-6 text-emerald-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/5 bg-white/[0.03]">
                <CardHeader>
                  <CardTitle className="text-white text-sm font-medium">What-If Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { var: "Month", value: "August", impact: "+8.2%" },
                      { var: "Guests", value: "2 → 4", impact: "+15.3%" },
                      { var: "Nights", value: "1 → 3", impact: "+22.1%" },
                    ].map((w, i) => (
                      <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                        <div>
                          <p className="text-xs text-slate-400">{w.var}</p>
                          <p className="text-sm font-medium text-white">{w.value}</p>
                        </div>
                        <span className="text-sm font-semibold text-emerald-400">{w.impact}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
