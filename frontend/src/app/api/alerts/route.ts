import { NextResponse } from 'next/server'

const API = 'http://localhost:8000/api/v1'

export async function GET() {
  const res = await fetch(`${API}/admin/alerts`)
  const data = await res.json()
  return NextResponse.json(data)
}
