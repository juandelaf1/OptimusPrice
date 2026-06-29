"use client"

import { useEffect, useState, useCallback } from "react"

export function useAutoRefresh(intervalMs = 30_000) {
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setRefreshKey(k => k + 1), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs])

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout>

    function connect() {
      try {
        ws = new WebSocket("ws://localhost:8000/ws/prices/default")
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data)
            if (msg.event === "prices_updated") {
              setRefreshKey(k => k + 1)
            }
          } catch { /* ignore parse errors */ }
        }
        ws.onclose = () => {
          reconnectTimer = setTimeout(connect, 5000)
        }
      } catch { /* ignore connection errors */ }
    }

    connect()
    return () => {
      ws?.close()
      clearTimeout(reconnectTimer)
    }
  }, [])

  const triggerRefresh = useCallback(() => {
    setRefreshKey(k => k + 1)
  }, [])

  return { refreshKey, triggerRefresh }
}
