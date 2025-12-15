"use client"

import ConsumerProfile from "@/pages/ConsumerProfile"

export default function ConsumerProfilePage({ params }: { params: { id: string } }) {
  return <ConsumerProfile consumerId={params.id} />
}
