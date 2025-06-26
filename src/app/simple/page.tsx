'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function SimplePage() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-purple-950 to-black p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold text-white mb-8 text-center">
          🚀 MCPVots - AGI Ecosystem Platform
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-900/80 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-400">System Status</CardTitle>
              <CardDescription className="text-gray-300">Core services operational</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant="default" className="bg-green-600 text-white">
                ✅ Online
              </Badge>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/80 border-gray-700">
            <CardHeader>
              <CardTitle className="text-blue-400">DeepSeek R1</CardTitle>
              <CardDescription className="text-gray-300">Advanced reasoning models</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant="default" className="bg-blue-600 text-white">
                🧠 Ready
              </Badge>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/80 border-gray-700">
            <CardHeader>
              <CardTitle className="text-purple-400">Gemini CLI</CardTitle>
              <CardDescription className="text-gray-300">1M token context processing</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant="default" className="bg-purple-600 text-white">
                🔥 Active
              </Badge>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <Button 
            onClick={() => setCount(count + 1)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold"
          >
            Test Button (Clicked {count} times)
          </Button>
        </div>

        <div className="mt-12 text-center text-gray-300">
          <p className="text-lg">
            🎯 <strong>Frontend Status:</strong> ✅ Operational<br/>
            🔧 <strong>Build Status:</strong> ✅ Success<br/>
            🚀 <strong>Ready for:</strong> Full ecosystem integration
          </p>
        </div>
      </div>
    </div>
  )
}
