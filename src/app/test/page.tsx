'use client'

export default function TestPage() {
  return (
    <div className="min-h-screen bg-red-500 p-8">
      <h1 className="text-4xl font-bold text-white">Test Page</h1>
      <p className="text-xl text-white mt-4">If you can see this red background and white text, CSS is working!</p>
      <div className="bg-blue-500 p-4 mt-4 rounded">
        <p className="text-white">This should be a blue box</p>
      </div>
    </div>
  )
}
