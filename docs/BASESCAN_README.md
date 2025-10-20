# BaseScan / Etherscan v2 Quickstart (Base Chain 8453)

- Free tier: 5 calls/sec, up to 100,000 calls/day
- Endpoint: `https://api.etherscan.io/v2/api`
- Include `chainid=8453` for Base
- Put your key in `.env` as `BASESCAN_API_KEY=Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG`

Examples:

- Get ETH balance for address on Base:
  - `GET /v2/api?chainid=8453&module=account&action=balance&address=0x...&tag=latest&apikey=...`

- Get normal tx list:
  - `GET /v2/api?chainid=8453&module=account&action=txlist&address=0x...&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey=...`

- Get ERC-20 transfers:
  - `GET /v2/api?chainid=8453&module=account&action=tokentx&address=0x...&page=1&offset=100&startblock=0&endblock=99999999&sort=desc&apikey=...`

Python client:

- Use `EtherscanV2Client` in `basescan_client.py`.
- `client.get_balance(8453, address)` returns balance in wei as string.
