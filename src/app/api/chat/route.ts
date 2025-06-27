// Next.js API route to proxy requests to backend services
// This avoids CORS issues by making server-side requests

import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { message, model } = await request.json()

    console.log('🔄 API route received request:', { message, model })

    if (model === 'gemini-2.5') {
      // For Gemini, we need to handle WebSocket differently
      // For now, let's proxy to a simple HTTP endpoint we can add to the backend
      return NextResponse.json({
        content: "Gemini WebSocket proxy not implemented yet. Please use DeepSeek for now.",
        tokens: 0,
        executionTime: 0,
        model: 'gemini-2.5',
        status: 'error',
        error: 'WebSocket proxy not implemented'
      })
    } else if (model === 'deepseek-r1') {
      // Proxy DeepSeek request to backend
      const backendResponse = await fetch('http://localhost:8095/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          model: 'deepseek-r1',
          stream: false
        })
      })

      const data = await backendResponse.json()
      
      console.log('📥 Backend response:', data)

      if (backendResponse.ok) {
        return NextResponse.json({
          content: data.response,
          tokens: data.tokens || 0,
          executionTime: 0.5, // Approximate
          reasoning: data.reasoning || [],
          model: 'deepseek-r1',
          status: 'success'
        })
      } else {
        return NextResponse.json({
          content: `Backend error: ${data.error || 'Unknown error'}`,
          tokens: 0,
          executionTime: 0,
          model: 'deepseek-r1',
          status: 'error',
          error: data.error
        })
      }
    } else {
      return NextResponse.json({
        content: 'Unknown model',
        tokens: 0,
        executionTime: 0,
        model: model,
        status: 'error',
        error: 'Unknown model'
      })
    }
  } catch (error) {
    console.error('❌ API route error:', error)
    
    return NextResponse.json({
      content: `API proxy error: ${error instanceof Error ? error.message : String(error)}`,
      tokens: 0,
      executionTime: 0,
      model: 'unknown',
      status: 'error',
      error: String(error)
    }, { status: 500 })
  }
}
