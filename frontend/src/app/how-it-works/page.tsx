import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Network, Cpu, Zap, Database, Globe, BarChart3 } from "lucide-react"

const STEPS = [
  { icon: Globe, title: "1. RASPAL Worker", desc: "Scrapes Booking, Expedia, Hotels.com, and Trivago in real-time using stealth engine. Updates competitor prices every 30 minutes." },
  { icon: Cpu, title: "2. ML Engine", desc: "GradientBoosting model with 41 features (26 base + 15 competitor). R² score of 0.9998. Predicts optimal price based on market conditions." },
  { icon: Database, title: "3. FastAPI Backend", desc: "REST API serves predictions via /api/v1/predict. WebSocket endpoints stream live price updates to the dashboard." },
  { icon: Zap, title: "4. Next.js Dashboard", desc: "Real-time UI with Recharts visualizations. Auto-refresh every 30s. Mobile-responsive with Tailwind CSS." },
]

const METRICS = [
  { label: "Model", value: "GradientBoosting" },
  { label: "Features", value: "41 (26+15)" },
  { label: "R² Score", value: "0.9998" },
  { label: "OTAs Tracked", value: "4" },
  { label: "Update Frequency", value: "30 min" },
  { label: "API Format", value: "REST + WebSocket" },
]

export default function HowItWorksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">How It Works</h1>
        <p className="text-sm text-slate-400 mt-0.5">Architecture pipeline from data collection to price recommendation</p>
      </div>

      {/* Pipeline Flow */}
      <div className="grid md:grid-cols-4 gap-3">
        {STEPS.map((step) => {
          const Icon = step.icon
          return (
            <Card key={step.title} className="border-white/5 bg-white/[0.03]">
              <CardContent className="p-4 text-center">
                <div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-xl bg-emerald-400/10">
                  <Icon className="size-5 text-emerald-400" />
                </div>
                <p className="text-sm font-semibold text-white mb-1">{step.title}</p>
                <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Pipeline Diagram */}
      <Card className="border-white/5 bg-white/[0.03]">
        <CardHeader>
          <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
            <Network className="size-3.5 text-emerald-400" /> Data Flow
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between px-4 py-6 overflow-x-auto">
            {[
              { label: "RASPAL", sub: "Web Scraper", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
              { label: "ML Engine", sub: "Python", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
              { label: "FastAPI", sub: "REST API", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
              { label: "Next.js", sub: "Dashboard", color: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
            ].map((step, i) => (
              <div key={step.label} className="flex items-center gap-3">
                <div className="flex flex-col items-center">
                  <Badge className={`px-3 py-1.5 text-xs font-semibold ${step.color}`}>{step.label}</Badge>
                  <span className="text-[10px] text-slate-500 mt-1">{step.sub}</span>
                </div>
                {i < 3 && <ArrowIcon />}
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 rounded-lg bg-white/5 text-xs text-slate-400">
            <p className="font-medium text-white mb-1">Data Flow:</p>
            <ol className="list-decimal list-inside space-y-1 text-slate-400">
              <li>RASPAL scrapes Booking, Expedia, Hotels, Trivago every 30 min</li>
              <li>ML Engine predicts optimal price with 41 features</li>
              <li>WebSocket pushes updates to dashboard in real-time</li>
              <li>Admin adjusts prices → override impacts predictions</li>
              <li>Customer books → feedback loop → retrain ML</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <Card className="border-white/5 bg-white/[0.03]">
        <CardHeader>
          <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
            <BarChart3 className="size-3.5 text-emerald-400" /> Model Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
            {METRICS.map((m) => (
              <div key={m.label} className="text-center">
                <p className="text-xs text-slate-400">{m.label}</p>
                <p className="text-sm font-semibold text-white mt-0.5">{m.value}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ArrowIcon() {
  return (
    <svg className="size-5 text-slate-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
    </svg>
  )
}
