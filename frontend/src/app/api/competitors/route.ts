import { NextResponse } from 'next/server'

const API = 'http://localhost:8000/api/v1'

export async function GET() {
  const res = await fetch(`${API}/competitors/prices`)
  const data = await res.json()
  return NextResponse.json(data)
}

export async function POST() {
  const res = await fetch(`${API}/competitors/check`, { method: 'POST' })
  const data = await res.json()
  return NextResponse.json(data)
}
