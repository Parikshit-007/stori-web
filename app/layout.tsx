import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import Layout from "@/components/Layout"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Stori AI",
  description: "Stori AI Credit Scoring Platform - Advanced Credit Scoring powered by AI",
  metadataBase: new URL('https://mycfo.club/stori'),
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32x32.svg", sizes: "32x32", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "any" }
    ],
    apple: [
      { url: "/apple-touch-icon.svg", sizes: "180x180", type: "image/svg+xml" }
    ],
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/stori/manifest.json" />
        <meta name="theme-color" content="#667eea" />
      </head>
      <body className={`font-sans antialiased`} suppressHydrationWarning>
        <Layout>{children}</Layout>
        <Analytics />
      </body>
    </html>
  )
}
