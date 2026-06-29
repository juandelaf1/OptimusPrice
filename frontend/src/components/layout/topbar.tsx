"use client"

import { Bell, Search, User } from "lucide-react"

const NOTIFICATIONS = 3

export default function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-white/5 bg-[#0B1121]/80 backdrop-blur-xl px-6">
      {/* Search */}
      <div className="flex flex-1 items-center gap-2 rounded-lg border border-white/5 bg-white/5 px-3 py-1.5 max-w-md">
        <Search className="size-3.5 text-slate-500" />
        <input
          type="text"
          placeholder="Search properties, reservations..."
          className="flex-1 bg-transparent text-sm text-white placeholder:text-slate-600 focus:outline-none"
        />
        <kbd className="hidden md:inline-flex items-center gap-1 rounded border border-white/5 bg-white/5 px-1.5 py-0.5 text-[10px] text-slate-500">
          ⌘K
        </kbd>
      </div>

      <div className="flex items-center gap-3">
        {/* Notifications */}
        <button className="relative flex size-8 items-center justify-center rounded-lg text-slate-400 hover:bg-white/5 hover:text-white transition-colors">
          <Bell className="size-4" />
          {NOTIFICATIONS > 0 && (
            <span className="absolute -top-0.5 -right-0.5 flex size-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white">
              {NOTIFICATIONS}
            </span>
          )}
        </button>

        {/* User */}
        <div className="flex items-center gap-2.5 border-l border-white/5 pl-3">
          <div className="flex size-8 items-center justify-center rounded-full bg-emerald-400/20">
            <User className="size-4 text-emerald-400" />
          </div>
          <div className="hidden md:block">
            <p className="text-xs font-medium text-white leading-tight">Demo Hotel</p>
            <p className="text-[10px] text-slate-500 leading-tight">Premium Plan</p>
          </div>
        </div>
      </div>
    </header>
  )
}
