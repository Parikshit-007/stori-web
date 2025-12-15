"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Users, Menu, X } from "lucide-react"
// import { Zap, TrendingUp, Brain, Settings, Home } from "lucide-react"

const menuItems = [
  // { id: "dashboard", label: "Dashboard", path: "/", icon: Home },
  { id: "consumers", label: "Consumers", path: "/consumers", icon: Users },
  // { id: "score-builder", label: "Score Builder", path: "/score-builder", icon: Zap },
  // { id: "risk", label: "Risk Analysis", path: "/risk-analysis", icon: TrendingUp },
  // { id: "explainability", label: "Explainability", path: "/explainability", icon: Brain },
  // { id: "admin", label: "Admin", path: "/admin", icon: Settings },
]

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(true)
  const pathname = usePathname()

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white border border-gray-200 rounded-lg"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Sidebar */}
      <aside
        className={`${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 transition-transform duration-300 fixed lg:static w-64 h-screen bg-white border-r border-gray-200 flex flex-col z-40`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center text-white font-bold">
              K
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Kaj NBFC</h1>
              <p className="text-xs text-gray-500">Credit Builder</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.path || (item.path === "/consumers" && pathname === "/")
            return (
              <Link
                key={item.id}
                href={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                  isActive ? "bg-blue-50 text-blue-600 font-semibold" : "text-gray-700 hover:bg-gray-50"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <p className="font-semibold">Model Version</p>
            <p>GBM v1.2.3</p>
            <p className="text-gray-400 mt-2">Last updated: Jan 15, 2025</p>
          </div>
        </div>
      </aside>
    </>
  )
}
