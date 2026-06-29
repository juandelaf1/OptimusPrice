import { NextRequest, NextResponse } from 'next/server'

const API = 'http://localhost:8000/api/v1'

export async function GET(request: NextRequest) {
  const days = request.nextUrl.searchParams.get('days') || '7'
  const res = await fetch(`${API}/predict/history?days=${days}`)
  const data = await res.json()
  return NextResponse.json(data)
}
