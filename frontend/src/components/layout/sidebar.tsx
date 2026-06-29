"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard, TrendingUp, CalendarCheck, SlidersHorizontal,
  Network, Settings, ChevronLeft, ChevronRight,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/monitor", label: "Market Monitor", icon: TrendingUp },
  { href: "/reservations", label: "Reservations", icon: CalendarCheck },
  { href: "/simulator", label: "Price Simulator", icon: SlidersHorizontal },
  { href: "/how-it-works", label: "How It Works", icon: Network },
  { href: "/settings", label: "Settings", icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside className={cn(
      "fixed left-0 top-0 z-40 h-screen border-r border-white/5 bg-[#0B1121] transition-all duration-300",
      collapsed ? "w-16" : "w-56"
    )}>
      {/* Logo */}
      <div className={cn(
        "flex h-16 items-center border-b border-white/5 px-4",
        collapsed && "justify-center px-0"
      )}>
        {collapsed ? (
          <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-400/20">
            <TrendingUp className="size-4 text-emerald-400" />
          </div>
        ) : (
          <div className="flex items-center gap-2.5">
            <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-400/20">
              <TrendingUp className="size-4 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white leading-tight">Optimus</p>
              <p className="text-[10px] font-medium text-emerald-400 leading-tight tracking-widest uppercase">Price</p>
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                collapsed && "justify-center px-2",
                isActive
                  ? "bg-emerald-400/10 text-emerald-400"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              )}
            >
              <item.icon className="size-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Collapse button */}
      <div className="absolute -right-3 top-20">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex size-6 items-center justify-center rounded-full border border-white/5 bg-[#0B1121] text-slate-400 hover:text-white"
        >
          {collapsed ? <ChevronRight className="size-3" /> : <ChevronLeft className="size-3" />}
        </button>
      </div>
    </aside>
  )
}
