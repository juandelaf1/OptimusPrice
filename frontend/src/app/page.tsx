import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <main className="max-w-2xl w-full space-y-6">
        {/* Logo/Title */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-white tracking-tight">
            Optimus Price
          </h1>
          <p className="text-slate-400">
            AI-powered pricing for any accommodation — hotels, Airbnb, hostels, rural houses
          </p>
        </div>

        {/* Main Demo Card */}
        <Card className="border-slate-800 bg-slate-900">
          <CardHeader>
            <CardTitle className="text-white">Get Your Optimal Price</CardTitle>
            <CardDescription>
              Enter your property details and see how much you should charge today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Property Type</label>
                  <select className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white">
                    <option>Hotel</option>
                    <option>Airbnb</option>
                    <option>Hostel</option>
                    <option>Rural House</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Location</label>
                  <input 
                    type="text" 
                    placeholder="e.g., Barcelona, Costa del Sol"
                    className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white placeholder:text-slate-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Guests</label>
                  <input type="number" defaultValue={2} min={1} max={20} className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Nights</label>
                  <input type="number" defaultValue={1} min={1} max={30} className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-slate-300 mb-1 block">Check-in Month</label>
                  <select className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white">
                    <option>July</option>
                    <option>August</option>
                    <option>September</option>
                  </select>
                </div>
              </div>

              <Button className="w-full bg-white text-slate-900 hover:bg-emerald-400">
                Calculate Optimal Price
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Value Proposition */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-emerald-400">+30%</p>
            <p className="text-slate-400 text-sm">Revenue vs OTA direct</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-emerald-400">4 OTAs</p>
            <p className="text-slate-400 text-sm">Live scraping</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-emerald-400">41 features</p>
            <p className="text-slate-400 text-sm">ML-powered pricing</p>
          </div>
        </div>

        {/* Footer */}
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