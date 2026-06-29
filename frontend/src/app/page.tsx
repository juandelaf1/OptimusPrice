"use client"

import KPICards from "@/components/dashboard/kpi-cards"
import PriceChart from "@/components/dashboard/price-chart"
import MarketIntel from "@/components/dashboard/market-intel"
import ActivityFeed from "@/components/dashboard/activity-feed"
import { useAutoRefresh } from "@/hooks/useAutoRefresh"
import { useState } from "react"

export default function Dashboard() {
  const { refreshKey, triggerRefresh } = useAutoRefresh(30_000)
  const [scraping, setScraping] = useState(false)

  async function handleScrape() {
    setScraping(true)
    try {
      await fetch("/api/competitors", { method: "POST" })
      triggerRefresh()
    } catch { /* ignore */ }
    setScraping(false)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-0.5">Real-time overview of your property performance</p>
        </div>
        <button
          onClick={handleScrape}
          disabled={scraping}
          className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 text-sm font-medium text-emerald-400 hover:bg-emerald-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {scraping ? "Scraping..." : "Scrape Now"}
        </button>
      </div>

      {/* KPI Cards */}
      <KPICards refreshKey={refreshKey} />

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-4">
        <PriceChart refreshKey={refreshKey} />
        <MarketIntel refreshKey={refreshKey} />
      </div>

      {/* Activity Feed */}
      <ActivityFeed refreshKey={refreshKey} />
    </div>
  )
}
