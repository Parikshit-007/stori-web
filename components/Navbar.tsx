"use client"

import { useState } from "react"
import { Search, Bell, Settings } from "lucide-react"

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-40">
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Global search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="flex items-center gap-6 ml-6">
        <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition">
          <Settings className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
          <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
            JD
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-gray-900">John Doe</p>
            <p className="text-xs text-gray-500">Analyst</p>
          </div>
        </div>
      </div>
    </nav>
  )
}
