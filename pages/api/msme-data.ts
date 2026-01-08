import type { NextApiRequest, NextApiResponse } from 'next'
import { generateMockMSMEs } from '@/lib/mockMSMEData'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const businesses = generateMockMSMEs(100)
    return res.status(200).json(businesses)
  } catch (error) {
    console.error('[MSME API] Error:', error)
    return res.status(500).json({ error: 'Failed to generate data' })
  }
}

