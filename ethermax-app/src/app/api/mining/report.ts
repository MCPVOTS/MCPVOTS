import crypto from 'crypto'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        const { address, uptime, peers, dataPinned, score, signature } = body

        // Validate required fields
        if (!address || typeof score !== 'number' || !signature) {
            return NextResponse.json({ error: 'Missing required fields' }, { status: 400 })
        }

        // Verify signature to prevent spoofing
        const message = `${address}:${uptime}:${peers}:${dataPinned}:${score}`
        const isValidSignature = await verifySignature(message, signature, address)

        if (!isValidSignature) {
            return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
        }

        // Rate limiting check (implement in production)
        // const rateLimitOk = await checkRateLimit(address)
        // if (!rateLimitOk) {
        //     return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 })
        // }

        // Store mining data securely (encrypt sensitive fields)
        const encryptedData = encryptMiningData({
            address,
            uptime,
            peers,
            dataPinned,
            score,
            timestamp: new Date().toISOString()
        })

        console.log('Encrypted mining report received:', encryptedData.reportId)

        // Calculate rewards based on score
        const rewards = Math.floor(score / 10) // 1 MCPVOTS per 10 score points

        return NextResponse.json({
            success: true,
            rewards,
            reportId: encryptedData.reportId,
            message: 'Mining report received and verified'
        })

    } catch (error) {
        console.error('Mining report error:', error)
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
    }
}

async function verifySignature(message: string, signature: string, address: string): Promise<boolean> {
    // In production, verify against blockchain signature
    // For now, implement basic HMAC verification
    try {
        const expectedSignature = crypto
            .createHmac('sha256', process.env.MINING_API_SECRET || 'default-secret')
            .update(message)
            .digest('hex')

        return signature === expectedSignature
    } catch {
        return false
    }
}

function encryptMiningData(data: any) {
    // Encrypt sensitive mining data before storage
    const algorithm = 'aes-256-cbc'
    const key = crypto.scryptSync(process.env.ENCRYPTION_KEY || 'default-key', 'salt', 32)
    const iv = crypto.randomBytes(16)

    const cipher = crypto.createCipheriv(algorithm, key, iv)
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex')
    encrypted += cipher.final('hex')

    return {
        reportId: crypto.randomUUID(),
        encryptedData: encrypted,
        iv: iv.toString('hex')
    }
}
