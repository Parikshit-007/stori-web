"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function Home() {
  const router = useRouter()
  
  useEffect(() => {
    router.replace("/consumers")
  }, [router])

  return (
    <div className="flex items-center justify-center h-96">
      <div className="text-gray-500">Redirecting...</div>
    </div>
  )
}
