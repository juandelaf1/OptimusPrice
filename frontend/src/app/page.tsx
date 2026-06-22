"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    const form = e.target as HTMLFormElement
    const data = {
      property_type: (form.elements.namedItem("property_type") as HTMLSelectElement)?.value || "hotel",
      guests: parseInt((form.elements.namedItem("guests") as HTMLInputElement)?.value || "2"),
      nights: parseInt((form.elements.namedItem("nights") as HTMLInputElement)?.value || "1"),
      month: parseInt((form.elements.namedItem("month") as HTMLSelectElement)?.value || "7"),
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
      else setError(json.detail || "Error")
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <main className="max-w-2xl w-full space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-white tracking-tight">Optimus Price</h1>
          <p className="text-slate-400">AI-powered pricing for any accommodation — hotels, Airbnb, hostels, rural houses</p>
        </div>

        <Card className="border-slate-800 bg-slate-900">
          <CardHeader>
            <CardTitle className="text-white">Get Your Optimal Price</CardTitle>
            <CardDescription>Enter your property details and see how much you should charge today</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Property Type</label>
                  <select name="property_type" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white">
                    <option value="hotel">Hotel</option>
                    <option value="airbnb">Airbnb</option>
                    <option value="hostel">Hostel</option>
                    <option value="rural">Rural House</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Location</label>
                  <input name="location" type="text" placeholder="e.g., Barcelona, Costa del Sol" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white placeholder:text-slate-500" />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Guests</label>
                  <input name="guests" type="number" defaultValue={2} min={1} max={20} className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Nights</label>
                  <input name="nights" type="number" defaultValue={1} min={1} max={30} className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Check-in Month</label>
                  <select name="month" className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white">
                    <option value="6">June</option>
                    <option value="7" selected>July</option>
                    <option value="8">August</option>
                    <option value="9">September</option>
                  </select>
                </div>
              </div>

              <Button type="submit" disabled={loading} className="w-full bg-white text-slate-900 hover:bg-emerald-400">
                {loading ? "Calculating..." : "Calculate Optimal Price"}
              </Button>
            </form>

            {error && <p className="text-red-400 mt-4">{error}</p>}

            {result && (
              <div className="mt-6 p-4 bg-emerald-400/10 border border-emerald-400/20 rounded-lg">
                <p className="text-emerald-400 font-semibold">Recommended Price: €{result.price}</p>
                {result.competitor_avg && (
                  <p className="text-slate-300 mt-1">OTA Average: €{result.competitor_avg} · You save by going direct!</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div><p className="text-2xl font-bold text-emerald-400">+30%</p><p className="text-slate-400 text-sm">Revenue vs OTA</p></div>
          <div><p className="text-2xl font-bold text-emerald-400">4 OTAs</p><p className="text-slate-400 text-sm">Live data</p></div>
          <div><p className="text-2xl font-bold text-emerald-400">41 features</p><p className="text-slate-400 text-sm">ML-driven</p></div>
        </div>

        <div className="flex justify-center gap-2 text-sm">
          <a href="/docs" className="text-slate-400 hover:text-white">Documentation</a>
          <span className="text-slate-600">·</span>
          <a href="/api-docs" className="text-slate-400 hover:text-white">API Docs</a>
          <span className="text-slate-600">·</span>
          <a href="https://github.com/juandelaf1/OptimusPrice" className="text-slate-400 hover:text-white">GitHub</a>
        </div>
      </main>
    </div>
  )
}