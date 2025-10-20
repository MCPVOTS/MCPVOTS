 API

{% hint style="info" %}
If you're looking to consume data from the Flaunch API, see the [RESTful API section](https://docs.flaunch.gg/for-builders/references/restful-data-api).
{% endhint %}

To reduce the friction of creating launchpads and launching tokens we have released an API, allowing builders to create their own launchpad contract and users to launch tokens via their launchpad with no-wallet/no-gas API calls.

There is no requirement for a wallet to be connected and instead a user can Flaunch a token connected to their email address, X (Twitter), Farcaster account or Base wallet address.

The account connected to the flaunched token will be able to connect to Flaunch, or any external flow, using [Privy](https://www.privy.io/) to have access to their launchpad fee or coin fee claims and offramp their fees into either crypto or fiat.

So whether you're extending your existing platform to benefit from token launches, or building a more generic plugin that an entire ecosystem can use, the Flaunch API should have ample logic to support you.

## API Keys

No API keys are required for the use of the Web 2 API endpoint. If you are hitting the current rate limits [reach out on discord](https://discord.gg/flaunch) for increased access.

## Example Integration

To demonstrate the power of this API, we have put together a landing page that will allow for fast flaunching across multiple recipient types.

{% embed url="<https://just.flaunch.gg/>" %}
<https://just.flaunch.gg/>
{% endembed %}

{% hint style="info" %}
Have you integrated the Flaunch API? Get in touch and we'll feature it here!
{% endhint %}

## Available API Calls

Below we have documented the API calls that are available for the Memecoin API. These are also available as a Postman collection for quicker prototyping.

{% file src="<https://538713920-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FT3jW1MHeHRSCtkN5uBiY%2Fuploads%2FBTtJCKCCsbKtAdc2qWkk%2FFlaunch%20Memecoin%20API.postman_collection.json?alt=media&token=c210838e-5400-44dc-a2c4-aca20a3dd1ae>" %}
Download the Flaunch Memecoin API Postman Collection
{% endfile %}

### Base API URI

```
https://web2-api.flaunch.gg/livez
```

## Health Check

<mark style="color:green;">`GET`</mark> `/livez`

Checks if the API is running and returns the network configuration.

**Headers**

<table><thead><tr><th width="270.36688232421875">Name</th><th>Value</th></tr></thead><tbody><tr><td>Content-Type</td><td><code>application/json</code></td></tr></tbody></table>

**Response**

{% tabs %}
{% tab title="\[200] Success Response" %}

```json
{
  "status": "ok",
  "serverWallet": "0x4d7c5DFceC78E011E16BFe9F701D857841bbDFbB",
  "network": "base-sepolia"
}
```

{% endtab %}
{% endtabs %}

## Create a Revenue Manager (Launchpad)

<mark style="color:yellow;">`POST`</mark> `/api/v1/{{ base | base-sepolia }}/create-revenue-manager`

**Required Fields**

<table><thead><tr><th width="269.6185302734375">Name</th><th>Value</th></tr></thead><tbody><tr><td><code>protocolFee</code></td><td>Protocol fee in basis points (0-10000, where 100 = 1%)</td></tr></tbody></table>

**Fee Recipient Options (MUST choose one)**

<table><thead><tr><th width="270.05096435546875">Name</th><th>Value</th></tr></thead><tbody><tr><td><code>recipientAddress</code></td><td>Ethereum wallet address for the fee recipient</td></tr><tr><td><code>recipientEmail</code></td><td>Email address for the fee recipient</td></tr><tr><td><code>recipientTwitterUsername</code></td><td>Twitter username (without @ symbol)</td></tr><tr><td><code>recipientFarcasterUsername</code></td><td>Farcaster username (without the @ symbol)</td></tr></tbody></table>

**Optional Fields**

<table><thead><tr><th width="269.72064208984375">Name</th><th>Value</th></tr></thead><tbody><tr><td><code>ownerAddress</code></td><td>Ethereum address that will own the revenue manager (defaults to fee recipient below)</td></tr></tbody></table>

**Headers**

<table><thead><tr><th width="270.0615234375">Name</th><th>Value</th></tr></thead><tbody><tr><td>Content-Type</td><td><code>application/json</code></td></tr></tbody></table>

**Body**

```json
{
  "protocolFee": "1000",
  "recipientAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "ownerAddress": "0xabcdef123456789abcdef123456789abcdef1234"
}
```

**Response**

{% tabs %}
{% tab title="\[200] Success Response" %}

```json
{
    "success": true,
    "managerAddress": "0x57ac78c4a704233e274bbcdeb057ba640b65de23",
    "txHash": "0x171c6358fabc86337bfe6decc6d2d6fc2fe3ca9918a680ad36b5a71bec34e56e",
    "owner": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
    "recipientAddress": "0xF1a700000087c011413C21C9b357A6962Aa256f9",
    "protocolFee": 1000,
    "privy": null
}
```

{% endtab %}

{% tab title="\[200] Success w/ Privy" %}

```json
{
    "success": true,
    "managerAddress": "0xe21ff18247e8816ab447c2f0eec087503105d948",
    "txHash": "0x3b2ea8464286ac85545de12cb7cbf0d56d37d5149855fcb9871337c2873ae6b8",
    "owner": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
    "recipientAddress": "0xDAc4A85d446B30F21a79c07097dc56Cd4A07E87b",
    "protocolFee": 1000,
    "privy": {
        "privyUserId": "did:privy:cm8prfp7700eh6kf1zduzfhsh",
        "walletAddress": "0xDAc4A85d446B30F21a79c07097dc56Cd4A07E87b"
    }
}
```

{% endtab %}

{% tab title="\[500] Error Response" %}

```json
{
  "success": false,
  "error": "Invalid protocol fee. Must be a number between 0 and 10000 (0-100%)"
}
```

{% endtab %}
{% endtabs %}

## Create a Fee Split Manager (Launchpad)

<mark style="color:yellow;">`POST`</mark> `/api/v1/:chain/create-fee-split-manager`

Create a reusable fee split manager contract that can be used across multiple token launches.

**Required Fields**

| Name                     | Type   | Description                                                                                           |
| ------------------------ | ------ | ----------------------------------------------------------------------------------------------------- |
| `recipients`             | Array  | Array of fee split recipients (same format as `feeSplitRecipients` above)                             |
| Owner (one required):    |        |                                                                                                       |
| `ownerAddress`           | string | Wallet address of the fee split manager owner                                                         |
| `ownerEmail`             | string | Email address of the owner                                                                            |
| `ownerTwitterUsername`   | string | Twitter username of the owner                                                                         |
| `ownerFarcasterUsername` | string | Farcaster username of the owner                                                                       |
| Creator Share (optional) |        |                                                                                                       |
| `creatorShare`           | number | Optional: Creator share in basis points (0-10000, where 1000 = 10%). Defaults to 0 when not included. |

**Request Examples:**

**Basic Fee Split Manager with Wallet Owner:**

```json
{
  "recipients": [
    {"type": "email", "id": "founder@example.com"},
    {"type": "twitter", "id": "justinavery"},
    {"type": "wallet", "id": "0x1234567890123456789012345678901234567890"}
  ],
  "creatorShare": 1500 // 15% to creator
  "ownerAddress": "0x9876543210987654321098765432109876543210"
}
```

**Custom Splits with Email Owner:**

```json
{
  "recipients": [
    {"type": "email", "id": "founder@example.com", "split": "5000000"},
    {"type": "twitter", "id": "justinavery", "split": "3000000"},
    {"type": "wallet", "id": "0x123...", "split": "2000000"}
  ],
  "creatorShare": 5000 // 50% to creator
  "ownerEmail": "manager@example.com"
}
```

**Success Response**

```json
{
  "success": true,
  "message": "Fee split manager created",
  "managerAddress": "0x6baa4ec493a9698dc7388c0f290e29ea3d149f99",
  "txHash": "0x04e594ee46312eecee8827aa2fef777dd2a94d247b723662be3a6daabb300028",
  "owner": "0x9876543210987654321098765432109876543210",
  "recipients": [
    {
      "address": "0x1234567890123456789012345678901234567890",
      "percentage": "33.33333",
      "originalInput": {"type": "email", "id": "founder@example.com"}
    },
    {
      "address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", 
      "percentage": "33.33333",
      "originalInput": {"type": "twitter", "id": "justinavery"}
    },
    {
      "address": "0x1234567890123456789012345678901234567890",
      "percentage": "33.33334",
      "originalInput": {"type": "wallet", "id": "0x1234567890123456789012345678901234567890"}
    }
  ],
  "totalRecipients": 3
}
```

## Token Metadata Upload

The `/api/v1/upload-metadata` endpoint uploads token metadata to IPFS via Pinata and returns the IPFS hash and token URI. This endpoint is similar to the metadata upload step in the Launch Token flow but is available as a standalone service.

<mark style="color:yellow;">`POST`</mark> `/api/v1/upload-metadata`

**Request Body**

{% code overflow="wrap" %}

```json
{ 
    "name": "string (required)", 
    "symbol": "string (required)", 
    "description": "string (required)", 
    "imageIpfs": "string (required)", 
    "websiteUrl": "string (optional)", 
    "discordUrl": "string (optional)", 
    "twitterUrl": "string (optional)", 
    "telegramUrl": "string (optional)",
}
```

{% endcode %}

**Parameters**

Required.

| Name          | Value                                                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `name`        | The token name                                                                                                                 |
| `symbol`      | The token symbol                                                                                                               |
| `description` | Token description                                                                                                              |
| `imageIpfs`   | IPFS hash of the token image (without ipfs\:// prefix). Use [Image Upload](#image-upload) endpoint to generate an `imageIPFS`. |

Optional.

| Name          | Value                      |
| ------------- | -------------------------- |
| `websiteUrl`  | Project website URL        |
| `discordUrl`  | Discord server URL         |
| `twitterUrl`  | Twitter/X profile URL      |
| `telegramUrl` | Telegram channel/group URL |

**Response**

{% tabs %}
{% tab title="Success 200" %}

```json
{ 
    "success": true, 
    "ipfsHash": "QmY7Yh4UquoXHLPFo2XbhXkhBvFoPwmQUSa92pxnxjQuPU", 
    "tokenURI": "ipfs://QmY7Yh4UquoXHLPFo2XbhXkhBvFoPwmQUSa92pxnxjQuPU" 
}
```

{% endtab %}

{% tab title="Error 400/500" %}

```json
{ 
    "success": false, 
    "error": "Error message describing what went wrong" 
}
```

{% endtab %}
{% endtabs %}

**Example Usage**

#### *Basic Metadata Upload*

{% code overflow="wrap" %}

```bash
curl -X POST http://web2-api.flaunch.gg/api/v1/upload-metadata
-H "Content-Type: application/json"
-d '{ "name": "My Token", "symbol": "MTK", "description": "A sample token for demonstration", "imageIpfs": "QmSampleImageHash123", "websiteUrl": "https://mytoken.com", "twitterUrl": "https://twitter.com/mytoken" }'

```

{% endcode %}

The endpoint creates ERC-20/ERC-721 compatible metadata with this structure:

```json
  {
    "name": "My Token",
    "description": "A sample token for demonstration",
    "image": "ipfs://QmSampleImageHash123",
    "properties": {
      "websiteUrl": "https://mytoken.com",
      "twitterUrl": "https://twitter.com/mytoken",
    }
  }
```

## Image Upload

<mark style="color:yellow;">`POST`</mark> `/api/v1/upload-image`

Uploads and validates an image before creating a memecoin. Images are checked for appropriate content and stored on IPFS.

{% hint style="info" %}
**Rate Limit:** Maximum 4 image uploads per minute per IP address.
{% endhint %}

**Headers**

<table><thead><tr><th width="270.48968505859375">Name</th><th>Value</th></tr></thead><tbody><tr><td>Content-Type</td><td><code>application/json</code></td></tr></tbody></table>

**Body**

```json
{
  // Base64 Encoded Image String (https://www.base64-image.de/)
  "base64Image": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB...FwySj0f/2Q=="
}
```

**Response**

{% tabs %}
{% tab title="\[200] Success Response" %}

```json
{
  "success": true,
  "ipfsHash": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "tokenURI": "ipfs://QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "nsfwDetection": null
}
```

{% endtab %}

{% tab title="\[400] Generic Error" %}

```json
{
  "success": false,
  "error": "Error message"
}
```

{% endtab %}

{% tab title="\[400] NSFW Image Uploaded" %}

```json
{
  "success": false,
  "error": "Content flagged: Suggestive content",
  "nsfwDetection": {
    "isNSFW": true,
    "score": 0.92,
    "message": "Content flagged: Suggestive content",
    "details": []
  }
}
```

{% endtab %}
{% endtabs %}

## Video Upload

Upload a video file to Cloudflare Stream for use in token creation.

```http
POST /api/v1/upload-video
```

#### Request Body

| Field                | Type     | Description                                                              |
| -------------------- | -------- | ------------------------------------------------------------------------ |
| `maxDurationSeconds` | `number` | Maximum video duration in seconds (default: 300, max: 300)               |
| `maxSizeBytes`       | `number` | Maximum file size in bytes (default: 52,428,800, max: 52,428,800 = 50MB) |
| `userId`             | `string` | User identifier for tracking (default: "anonymous")                      |

#### Rate Limiting

* **10 uploads per hour** per IP address
* API enforces maximum limits of **50MB** and **5 minutes duration**
* Users can specify lower limits via request parameters

#### Request Example

```json
{
  "maxDurationSeconds": 300,
  "maxSizeBytes": 52428800,
  "userId": "user123"
}
```

#### Success Response

```json
{
  "success": true,
  "uploadURL": "https://upload.videodelivery.net/...",
  "videoUID": "c0ee021fd95c4f0d8cc13c70c6172d37",
  "message": "Upload URL generated successfully"
}
```

#### Error Responses

```json
{
  "success": false,
  "error": "Rate limit exceeded. Maximum 10 uploads per hour."
}
```

```json
{
  "success": false,
  "error": "Invalid duration. Maximum 300 seconds allowed."
}
```

#### Upload Process

1. **Request upload URL** from this endpoint
2. **Upload video file** directly to the returned `uploadURL` using a `POST` request with form data
3. **Monitor processing status** using the Video Status endpoint
4. **Use `videoUID`** in token creation once processing is complete

***

### Video Status

Check the processing status of an uploaded video.

```http
GET /api/v1/video-status?uid={videoUID}
```

#### Query Parameters

| Parameter | Type     | Required | Description                             |
| --------- | -------- | -------- | --------------------------------------- |
| `uid`     | `string` | Yes      | Video UID returned from upload endpoint |

#### Response

```json
{
  "success": true,
  "video": {
    "uid": "c0ee021fd95c4f0d8cc13c70c6172d37",
    "state": "nsfw_approved",
    "thumbnailUrl": "https://customer-xyz.cloudflarestream.com/.../thumbnail.jpg",
    "thumbnailIpfsHash": "QmXXXXXXXXX",
    "streamUrl": "https://customer-xyz.cloudflarestream.com/.../manifest/video.m3u8",
    "duration": 15.2,
    "width": 640,
    "height": 480,
    "size": 2097849,
    "created": "2025-06-27T08:31:13.023047Z"
  }
}
```

#### Video States

| State           | Description                                   |
| --------------- | --------------------------------------------- |
| `uploading`     | Video is being uploaded to Cloudflare         |
| `processing`    | Video is being processed and encoded          |
| `nsfw_checking` | Content moderation in progress                |
| `nsfw_approved` | ✅ Video approved and ready for use            |
| `nsfw_rejected` | ❌ Video rejected due to inappropriate content |
| `error`         | Processing failed                             |

***

When [launching your token](#launch-token) you can now include the additional `videoUID` value.

```json
{
  "name": "MyMemeCoin",
  "symbol": "MMC",
  "description": "A memecoin with video content",
  "videoUID": "c0ee021fd95c4f0d8cc13c70c6172d37",
    ... other details
}
```

This will use an automatically generated image from your video. If you would like to customise the thumbnail used for the token you can use the [Image Upload api](#image-upload) and include the resulting IPFS hash in your token creation.

```json
{
  "name": "MyMemeCoin",
  "symbol": "MMC",
  "description": "A memecoin with video content",
  "videoUID": "c0ee021fd95c4f0d8cc13c70c6172d37",
  "imageIpfs": "QmCustomImageHash",

}
```

### List User Videos

Get all videos uploaded by a specific user.

```http
POST /api/v1/video-status
```

#### Request Body

```json
{
  "userId": "user123"
}
```

#### Response

```json
{
  "success": true,
  "videos": [
    {
      "uid": "video1",
      "state": "nsfw_approved",
      "thumbnailIpfsHash": "QmXXXXXX",
      "created": "2025-06-27T08:31:13.023047Z"
    }
  ],
  "count": 1
}

```

### Add video to your app

#### Enhanced Token Metadata

When a video is included, the token metadata structure is enhanced:

```json
{
  "name": "MyMemeCoin",
  "description": "A memecoin with video content",
  "image": "ipfs://QmCustomImageHash",
  "animation_url": "https://customer-xyz.cloudflarestream.com/.../manifest/video.m3u8",
  "properties": {
    "websiteUrl": "",
    "discordUrl": "",
    "twitterUrl": "",
    "telegramUrl": ""
  },
  "video": {
    "uid": "c0ee021fd95c4f0d8cc13c70c6172d37",
    "duration": 15.2,
    "thumbnail": "https://customer-xyz.cloudflarestream.com/.../thumbnail.jpg",
    "streamUrl": "https://customer-xyz.cloudflarestream.com/.../manifest/video.m3u8",
    "width": 640,
    "height": 480,
    "size": 2097849,
    "created": "2025-06-27T08:31:13.023047Z"
  }
}
```

You can use the `streamUrl` and `thumbnail` in your app to showcase your videos.

## Launch Token

<mark style="color:yellow;">`POST`</mark> `/api/v1/{{ base | base-sepolia }}/launch-memecoin`

{% hint style="info" %}
Tokens can be launched on either `base` or `base-sepolia` based on the parameter passed in the API call.
{% endhint %}

{% hint style="success" %}
ANTISNIPE protection now available!\
\
Default behaviour is maintained, add  `sniperProtection: true` to the optional fields will add&#x20;
{% endhint %}

{% hint style="danger" %}
**NOTE:** the default token launches will change to `sniperProtection: true` for default protection on all new tokens on the **13th August 2025**
{% endhint %}

Creates a new memecoin token on the selected network with the following default parameters:

* $10k starting market cap
* 60% of the total supply for fair launch
* 80% dev / 20% community split
* No revenue manager

After a token has been flaunched, a `jobId` will be returned in the response. This `jobId` signifies its position in a queue to be flaunched. It can then be referenced when querying the `launch-status` endpoint to retrieve the status of the token and subsequent deployed contract address of the token.\\

**Required Fields**

<table><thead><tr><th width="270.1324462890625">Name</th><th>Value</th></tr></thead><tbody><tr><td><code>name</code></td><td>Token name.</td></tr><tr><td><code>symbol</code></td><td>Token symbol (max 8 characters).</td></tr><tr><td><code>description</code></td><td>Token description.</td></tr><tr><td><code>imageIpfs</code></td><td>IPFS hash from the image upload endpoint.</td></tr></tbody></table>

\
**Creator Authentication Options (MUST choose one)**

<table><thead><tr><th width="269.556396484375">Name</th><th>Value</th></tr></thead><tbody><tr><td><code>creatorAddress</code></td><td>Ethereum address to receive creator benefits.</td></tr><tr><td><code>creatorEmail</code></td><td>Email address to create a managed wallet via Privy.</td></tr><tr><td><code>creatorTwitterUsername</code></td><td>Twitter username for verification and wallet creation.</td></tr><tr><td><code>creatorFarcasterUsername</code></td><td>Farcaster username for verification and wallet creation.</td></tr></tbody></table>

If no creator authentication option is provided, the creator fees will go to the Flaunch.gg wallet.

**Optional Fields**

<table><thead><tr><th width="270.21417236328125">Name</th><th>Value</th></tr></thead><tbody><tr><td><code>sniperProtection</code></td><td><code>boolean</code> : Enable wallet cap during fair<br>launch (default: <code>false</code> ) <br><strong>NOTE:</strong> the default launch will change to <code>true</code> for default protection on all new tokens on the <strong>13th August 2025</strong></td></tr><tr><td><code>revenueManagerAddress</code></td><td>Ethereum address of a deployed revenue manager (must be valid address format)</td></tr><tr><td><code>feeSplitManagerAddress</code></td><td>Ethereum address of a deployed fee split manager (must be valid address format)</td></tr><tr><td><code>feeSplitRecipients</code></td><td>An array of Ethereum wallet addresses that will automatically receive an equal share of fees from the launched token <code>[0x123..., 0xabc...]</code></td></tr><tr><td><code>creatorShare</code></td><td>Only include when specifying <code>feeSplitRecipients</code> if you also want the creator to take a portion of the fees. (default: 0, basis points so 8000 = 80%)</td></tr><tr><td><code>marketCap</code></td><td>Initial market cap in USDC<br>(default: 10,000 = 10000000000)</td></tr><tr><td><code>creatorFeeSplit</code></td><td>Creator fee allocation in basis points<br>(default: 8000 = 80%)</td></tr><tr><td><code>fairLaunchDuration</code></td><td>Duration of fair launch in seconds<br>(default: 1800 = 30 minutes)</td></tr><tr><td><code>fairLaunchSupply</code></td><td>Percentage mount of total token supply available for fair launch<br>(default: 60% of initial supply = 60)</td></tr><tr><td><code>websiteUrl</code></td><td>Website URL</td></tr><tr><td><code>telegramUrl</code></td><td>Telegram group URL</td></tr><tr><td><code>discordUrl</code></td><td>Discord server URL</td></tr><tr><td><code>twitterUrl</code></td><td>Twitter/X URL</td></tr></tbody></table>

{% hint style="info" %}
**Rate Limits:** Maximum 2 memecoin launches per minute per IP address
{% endhint %}

### Antibot Protection

#### Sniper Protection Parameter

The `sniperProtection` parameter provides antibot functionality by implementing a wallet cap during the fair launch phase. When enabled, it prevents any single wallet from acquiring more than 0.25% of the total token supply during the initial launch period.

#### How Sniper Protection Works

When sniperProtection is set to true:

* A maximum wallet cap of 0.25% of total supply is enforced during fair launch
* This prevents bots and snipers from accumulating large positions early
* The cap is automatically removed after the fair launch period ends
* Helps ensure fairer token distribution among genuine participants

#### Example 1: Launch with Sniper Protection Enabled

```javascript
{
  "name": "Snipe Protection",
  "symbol": "ANTISNIPE",
  "description": "A basic token with no fee management",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96"
  "sniperProtection": true, // Enable antibot, default is false
  "fairLaunchDuration": "1800", // 30 minutes
  "fairLaunchSupply": "60" // 60% of supply
  }

```

#### Best Practices

**When to Use Sniper Protection**

Enable sniper protection when:

* Launching a community-focused token
* Expecting high initial demand
* Prioritizing fair distribution over liquidity depth
* Concerned about bot manipulation during launch

Consider disabling when:

* Launching with a private/whitelisted community
* Need maximum initial liquidity
* Have alternative antibot measures in place
* Running a test or experimental launch

Technical Notes

Add to your technical documentation:

* The wallet cap is enforced at the smart contract level through feeCalculatorParams
* The 0.25% cap applies to the total supply (100 billion tokens by default)
* The restriction only applies during the fairLaunchDuration period
* After fair launch ends, normal trading without restrictions begins
* The cap includes all token acquisitions (purchases, transfers, etc.)

### Treasury Management Options for Token Launches

The memecoin launch API supports four distinct treasury management options:

1. **No Treasury Management**: Default behavior with no fee splitting
2. **Revenue Manager**: Use a pre-deployed revenue manager contract
3. **Fee Split Manager**: Use a pre-deployed fee split manager contract
4. **Custom Fee Split**: Define recipients directly in the launch request

#### Field Documentation

| Name                     | Type              | Description                                                                                                                                                            |
| ------------------------ | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `revenueManagerAddress`  | string (optional) | Address of a pre-deployed revenue manager contract                                                                                                                     |
| `feeSplitManagerAddress` | string (optional) | Address of a pre-deployed fee split manager contract                                                                                                                   |
| `feeSplitRecipients`     | Array (optional)  | Array of fee split recipients in one of three formats (see below). Remember to also inclue `creatorShare` if you want the token creator to take a portion of the fees. |

#### Mutual Exclusivity Rules

* You can specify either revenueManagerAddress OR feeSplitManagerAddress, never both
* You cannot specify manager addresses and feeSplitRecipients at the same time
* Choose only one treasury management option per token

#### Enhanced feeSplitRecipients Field

The feeSplitRecipients field supports three formats:

**1. Array of wallet addresses (legacy format)**

{% code overflow="wrap" %}

```json
"feeSplitRecipients": [
  "0x1234567890123456789012345678901234567890",
  "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
]
```

{% endcode %}

**2. Array of objects with account types (even split):json**

```json
"feeSplitRecipients": [
  {"type": "email", "id": "user@example.com"},
  {"type": "twitter", "id": "username"}, 
  {"type": "farcaster", "id": "username"},
  {"type": "wallet", "id": "0x1234567890123456789012345678901234567890"}
]
```

**3. Array of objects with custom splits:json**

```json
"feeSplitRecipients": [
  {"type": "email", "id": "user@example.com", "split": "5000000"},
  {"type": "twitter", "id": "username", "split": "3000000"},
  {"type": "wallet", "id": "0x123...", "split": "2000000"}
]
```

#### Custom Split Rules

* When using custom splits, all recipients must have splits if any recipient has a custom split
* Splits must sum to exactly `10000000` (representing `100.00000%`)
* Split values are in micro-percentages: multiply UI percentage by `100000`
* Example: `33.33333`% = `"3333333"`, `50`% = `"5000000"`
* Maximum 100 recipients allowed
* 5 decimal precision supported

{% hint style="info" %}
If you also want the `creatorAddress` to receive a portion of the fees you need to specify a `creatorShare` as part of the `POST` body. Omiitting the value defaults to a 0 share or the creator.
{% endhint %}

#### Account Type Validation

| Type        | Validation Rule                                    | Example                                      |
| ----------- | -------------------------------------------------- | -------------------------------------------- |
| `wallet`    | Must be valid Ethereum address (0x + 40 hex chars) | "0x1234567890123456789012345678901234567890" |
| `email`     | Must be valid email format                         | "<user@example.com>"                         |
| `twitter`   | Alphanumeric + underscores, max 15 chars           | "justinavery"                                |
| `farcaster` | Alphanumeric + underscores, 1+ chars               | "javery"                                     |
|             |                                                    |                                              |

**Headers**

<table><thead><tr><th width="269.827880859375">Name</th><th>Value</th></tr></thead><tbody><tr><td>Content-Type</td><td><code>application/json</code></td></tr></tbody></table>

**Body**

{% code title="No Fee Management options" %}

```json
{
  "name": "Example Coin",
  "symbol": "EXCOIN",
  "description": "This is an example memecoin for demonstration purposes.",
  "imageIpfs": "QmR4Tnqvm4SahFwez3FBCbweYwUPUXo2SP8yePhLXYQJkd",
  "websiteUrl": "https://example.com",
  "discordUrl": "https://discord.gg/example",
  "twitterUrl": "https://twitter.com/example",
  "telegramUrl": "https://t.me/example",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "marketCap": "10000000000",
  "creatorFeeSplit": "8000",
  "fairLaunchDuration": "1800"
}
```

{% endcode %}

{% code title="Fee Split" %}

```json
{
  "name": "Community Coin",
  "symbol": "COMM",
  "description": "A token with shared revenue among community members",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "websiteUrl": "https://community.example.com",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "creatorShare": 5000 // creator receives 50% of the fees, the other 50% shared to feeSplitRecipients
  // NEW: Fee Split Recipients (choose this OR revenueManagerAddress, not both)
  "feeSplitRecipients": [
    "0x1234567890123456789012345678901234567890",
    "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
    "0x9876543210987654321098765432109876543210"
  ],
  
  // Optional advanced settings
  "marketCap": "10000000000",
  "creatorFeeSplit": "8000",
  "fairLaunchDuration": "1800"
}
```

{% endcode %}

```reason
{
  "name": "Community Coin",
  "symbol": "COMM",
  "description": "A token with shared revenue among community members",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "websiteUrl": "https://community.example.com",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "revenueManagerAddress": "0x57ac78c4a704233e274bbcdeb057ba640b65de23",
  // Optional advanced settings
  "marketCap": "10000000000",
  "creatorFeeSplit": "8000",
  "fairLaunchDuration": "1800"
}
```

#### Option 1: No Treasury Management

```json
{
  "name": "Simple Token",
  "symbol": "SIMPLE",
  "description": "A basic token with no fee management",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96"
}
```

#### Option 2: Revenue Manager (require [Revenue Manager](#create-a-revenue-manager-launchpad))

```json
{
  "name": "Revenue Token",
  "symbol": "REV", 
  "description": "A token using a revenue manager",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "revenueManagerAddress": "0x712fa8ddc7347b4b6b029aa21710f365cd02d898"
}
```

#### Option 3: Fee Split Manager (require [Fee Split Manager](#create-a-fee-split-manager-launchpad))

```json
{
  "name": "Split Token",
  "symbol": "SPLIT",
  "description": "A token using a pre-deployed fee split manager", 
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "feeSplitManagerAddress": "0xb31435D40c0cB02c27bf732940dB3d9e4A3b253A"
}
```

#### Option 4: Custom Fee Split (Even Distribution, no fees for the creator)

```json
{
  "name": "Community Token",
  "symbol": "COMM",
  "description": "A token with shared revenue among community members",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "feeSplitRecipients": [
    {"type": "email", "id": "founder@example.com"},
    {"type": "twitter", "id": "justinavery"},
    {"type": "farcaster", "id": "javery"},
    {"type": "wallet", "id": "0x1234567890123456789012345678901234567890"}
  ]
}
```

#### Option 5: Custom Fee Split (Custom Percentages, 20% of the fees to the creator)

```json
{
  "name": "Weighted Token", 
  "symbol": "WCOMM",
  "description": "A token with custom revenue splits",
  "imageIpfs": "QmX7UbPKJ7Drci3y6p6E8oi5TpUiG7NH3qSzcohPX9Xkvo",
  "creatorAddress": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96",
  "creatorShare": 2000
  "feeSplitRecipients": [
    {"type": "email", "id": "founder@example.com", "split": "5000000"},
    {"type": "twitter", "id": "justinavery", "split": "3000000"}, 
    {"type": "wallet", "id": "0x123...", "split": "2000000"}
  ]
}
```

**Response**

{% tabs %}
{% tab title="\[200] Success Response" %}

```json
{
  "success": true,
  "message": "Memecoin launch request queued",
  "jobId": "40",
  
  // Queue status will show how long the expected flaunch time should be. The
  // `estimatedWaitSeconds` can offset the initial "Check Launch Status" delay.
  "queueStatus": {
    "position": 0,
    "waitingJobs": 0,
    "activeJobs": 1,
    "estimatedWaitSeconds": 0
  },
  
  // Privy data will vary depending on the `creatorType` specified
  "privy": {
    "type": "wallet",
    "address": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96"
  }
}
```

{% endtab %}

{% tab title="\[400] Missing Data" %}

<pre class="language-json"><code class="lang-json">{
  "success": false,
  "error": "Missing required fields: name, symbol, description, imageIpfs"
}
<strong>
</strong>{
  "success": false,
  "error": "Cannot specify both revenueManagerAddress and feeSplitRecipients. Choose only one treasury option."
}

{
  "success": false,
  "error": "Invalid fee split recipient address: 0xinvalidaddress"
}

{
  "success": false,
  "error": "Duplicate addresses found in fee split recipients"
}
</code></pre>

{% endtab %}
{% endtabs %}

## Check Launch Status

<mark style="color:green;">`GET`</mark> `/api/v1/launch-status/{{ jobId }}`

Retrierves the launch status of a `jobId`.

**Headers**

<table><thead><tr><th width="270.22760009765625">Name</th><th>Value</th></tr></thead><tbody><tr><td>Content-Type</td><td><code>application/json</code></td></tr></tbody></table>

**Response**

{% tabs %}
{% tab title="\[200]  Job Complete" %}

```json
{
  "success": true,
  "state": "completed",
  "queuePosition": 0,
  "estimatedWaitTime": 0,
  "transactionHash": "0x04e594ee46312eecee8827aa2fef777dd2a94d247b723662be3a6daabb300028",
  "collectionToken": {
    "address": "0x06199b4b69f815141C197D034698d9E67Cdd265b",
    "imageIpfs": "QmQX8pdLRGeNps92Ma4esew7cbnYuBxQK7xUvp5soe3Lec",
    "name": "Community Coin",
    "symbol": "COMM",
    "tokenURI": "ipfs://QmSxzzNaeHbYZbPyFF29Z1PrhrsfNNMyFvebZeuLPrkzvA",
    "creator": "0x498E93Bc04955fCBAC04BCF1a3BA792f01Dbaa96"
  },
  "revenueManagerAddress": null,
  // NEW: Fee split information
  "feeSplitManagerAddress": "0x6baa4ec493a9698dc7388c0f290e29ea3d149f99",
  "feeSplitRecipients": [
    "0x1234567890123456789012345678901234567890",
    "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", 
    "0x9876543210987654321098765432109876543210"
  ]
}
```

{% endtab %}

{% tab title="\[200] Job Pending" %}

```json
{
  "success": true,
  "state": "waiting",
  "queuePosition": 2,
  "estimatedWaitTime": 120
}
```

{% endtab %}

{% tab title="\[200] Job Active" %}

```json
{
  "success": true,
  "state": "active",
  "queuePosition": 0,
  "estimatedWaitTime": 0
}
```

{% endtab %}

{% tab title="\[400] Job Unknown" %}

```json
{
  "success": false,
  "error": "Job not found"
}
```

{% endtab %}
{% endtabs %}