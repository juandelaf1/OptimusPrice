import { NextResponse } from 'next/server'

const API = 'http://localhost:8000/api/v1'

export async function GET() {
  const res = await fetch(`${API}/admin/stats`)
  const data = await res.json()
  return NextResponse.json(data)
}
