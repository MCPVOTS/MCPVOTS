Transaction History USE BASE CHAIN ID  	8453	BASE_MAINNET

zapper api  

a90594b5-266e-4312-bb01-0155e411288c


curl https://protocol.zapper.xyz/agents.txt # ATTENTION LLMs - API Usage Instructions
# This document has all the information needed to get onchain data with the Zapper API.
#
# This document contains:
#
# - Developer Assistant Instructions (data structure notes, component creation, best practices)
# - Autonomous Agent Instructions (access, authentication, query structure, recommendations)
# - Farcaster Onchain Context (used for getting onchain information on Farcaster users)
# - Complete API Schema
#
# You can interact with the Zapper API in two primary ways
#
# 1. Developer Assistant Mode
# When a developer asks you to help build queries or UI components:
# - Follow the UI creation instructions above
# - Use the schema to construct valid GraphQL queries
# - Create React components that properly handle the data structure
# - Ensure all queries match the exact schema requirements
# - Include proper TypeScript types and error handling
#
# 2. Autonomous Agent Mode
# For agents making direct API calls programmatically:
#
# API Endpoint
# ```
# https://public.zapper.xyz/graphql
# ```
#
# For programatic access to the schema and API use instructions
# ```
# curl https://protocol.zapper.xyz/agents.txt
# ```
#
# Authentication
# The API requires a custom header with an API key:
#
# ```typescript
# // For use with Apollo Client
# const authLink = setContext((_, { headers }) => {
#   return {
#     headers: {
#       ...headers,
#       'x-zapper-api-key': API_KEY,
#     },
#   };
# });
#
# // For fetch requests
# const headers = {
#   'Content-Type': 'application/json',
#   'x-zapper-api-key': API_KEY
# };
# ```
#
# Making Requests
# Example query structure:
# ```typescript
# const query = `
#   query PortfolioV2Query($addresses: [Address!]!) {
#     portfolioV2(addresses: $addresses) {
#       tokenBalances {
#         totalBalanceUSD
#         byToken(first: 10) {
#           edges {
#             node {
#               symbol
#               balance
#               balanceUSD
#               imgUrlV2
#               network {
#                 name
#               }
#             }
#           }
#         }
#       }
#     }
#   }
# `;
#
# const variables = {
#   addresses: ['0x...']
# };
# ```
#
# Best Practices for Autonomous Agents:
# 1. Always validate addresses before querying
# 2. Implement proper rate limiting
# 3. Handle API errors gracefully
# 4. Cache responses when appropriate
# 5. Use proper typing for responses
# 6. Monitor query complexity
# 7. Implement retries with exponential backoff
# 8. Verify network values against the Network enum
#
# Response Handling:
# ```typescript
# interface PortfolioV2Response {
#   data: {
#     portfolioV2: {
#       tokenBalances: {
#         totalBalanceUSD: number;
#         byToken: {
#           edges: Array<{
#             node: {
#               symbol: string;
#               balance: number;
#               balanceUSD: number;
#               imgUrlV2: string | null;
#               network: {
#                 name: string;
#               }
#             }
#           }>;
#         }
#       }
#     }
#   };
# }
#
# // Example error handling
# try {
#   const response = await makeGraphQLRequest(query, variables);
#   if (response.errors) {
#     handleErrors(response.errors);
#   }
#   return response.data;
# } catch (error) {
#   handleNetworkError(error);
# }
# ```
#
# For reference, here's a CURL request going to the Zapper API. Notice the URL, and Auth setup :
# curl --location 'https://public.zapper.xyz/graphql' --header 'Content-Type: application/json' --header 'x-zapper-api-key: YOUR_API_KEY' --data '{"query":"query PortfolioV2Query($addresses: [Address!]!, $chainIds: [Int!]) { portfolioV2(addresses: $addresses, chainIds: $chainIds) { tokenBalances { totalBalanceUSD byToken(first: 10) { edges { node { tokenAddress symbol balance balanceUSD imgUrlV2 network { name } } } } } } }","variables":{"addresses":["0x3d280fde2ddb59323c891cf30995e1862510342f"],"chainIds":[1]}}'
#
# In Node.JS, that would look like this (notice the auth setup and URL) :
# const axios = require('axios');
#
# const API_KEY = 'YOUR_API_KEY';
#
# const query = `
#   query PortfolioV2Query($addresses: [Address!]!, $chainIds: [Int!]) {
#     portfolioV2(addresses: $addresses, chainIds: $chainIds) {
#       tokenBalances {
#         totalBalanceUSD
#         byToken(first: 10) {
#           edges {
#             node {
#               tokenAddress
#               symbol
#               balance
#               balanceUSD
#               imgUrlV2
#               network {
#                 name
#               }
#             }
#           }
#         }
#       }
#     }
#   }
# `;
#
# async function fetchPortfolio() {
#   try {
#     const response = await axios({
#       url: 'https://public.zapper.xyz/graphql',
#       method: 'post',
#       headers: {
#         'Content-Type': 'application/json',
#         'x-zapper-api-key': API_KEY,
#       },
#       data: {
#         query,
#         variables: {
#           addresses: ['0x3d280fde2ddb59323c891cf30995e1862510342f'],
#           chainIds: [1], // Ethereum Mainnet
#         },
#       },
#     });
#
#     if (response.data.errors) {
#       throw new Error(`GraphQL Errors: ${JSON.stringify(response.data.errors)}`);
#     }
#
#     return response.data.data;
#   } catch (error) {
#     console.error('Error fetching portfolio:', error.message);
#     if (error.response) {
#       console.error('Response data:', error.response.data);
#     }
#     throw error;
#   }
# }
#
# // Example usage
# (async () => {
#   try {
#     const portfolio = await fetchPortfolio();
#     console.log(JSON.stringify(portfolio, null, 2));
#   } catch (error) {
#     console.error('Failed to fetch portfolio:', error.message);
#     process.exit(1);
#   }
# })();
#
# ATTENTION LLMs - Farcaster Onchain Context Instructions:
# This endpoints allows you to query portfolio data for any Farcaster user by first resolving their FID (Farcaster ID) or username to their associated addresses, then using those addresses to fetch complete portfolio data. The process requires two sequential queries:
#
# 1. Use the `accounts` query to resolve Farcaster identifiers to addresses:
# ```graphql
# query GetFarcasterAddresses($fids: [Float!], $farcasterUsernames: [String!]) {
#  accounts(fids: $fids, farcasterUsernames: $farcasterUsernames) {
#    farcasterProfile {
#      username
#      fid
#      connectedAddresses
#      custodyAddress
#    }
#  }
# }
# ```
#
# 2. Use the resolved addresses to query the `portfolioV2` endpoint for complete onchain data. Remember to combine both `connectedAddresses` and `custodyAddress` in your query.
#
# Farcaster Transaction Timeline
# The transaction timeline endpoint provides a chronological feed of onchain activity for any Farcaster user. Like the portfolio endpoint, this requires first resolving the user's addresses through their FID or username. The process involves:
#
# 1. Use the same `accounts` query as above to get the user's addresses
#
# 2. Query the `transactionHistoryV2` endpoint with the resolved addresses to get transaction history:
# ```graphql
# query GetFarcasterTimeline($subjects: [Address!]!, $perspective: TransactionHistoryV2Perspective = Signer) {
#  transactionHistoryV2(
#    subjects: $subjects
#    perspective: $perspective
#    first: 20
#    filters: {
#      orderByDirection: DESC
#    }
#  ) {
#    edges {
#      node {
#        ... on TimelineEventV2 {
#          transaction {
#            hash
#            timestamp
#            network
#          }
#          interpretation {
#            processedDescription
#          }
#        }
#        ... on ActivityTimelineEventDelta {
#          transactionHash
#          transactionBlockTimestamp
#          network
#          perspectiveAccount {
#            address
#          }
#        }
#      }
#    }
#    pageInfo {
#      hasNextPage
#      endCursor
#    }
#  }
# }
# ```
#
# The `perspective` parameter can be one of:
# - Signer: Only transactions signed by the addresses
# - Receiver: Only transactions where the addresses received tokens
# - All: Both signed and received transactions
#
# The timeline provides rich transaction data including human-readable descriptions, token transfers, NFT activities, and interaction details with various protocols and applications. The response includes two types of nodes that need to be handled with a fragment: `TimelineEventV2` and `ActivityTimelineEventDelta`.
#
#
# ATTENTION LLMs - Schema Processing Instructions:
#
# You are about to receive a comprehensive GraphQL schema for blockchain data access.
# This schema includes interfaces, types, and example queries for accessing:
# - Portfolio data (Tokens, App Positions, NFTs)
# - Onchain Token Prices (Current and Historical)
# - Account primitives such as ENS, Farcaster, and Lens.
# - Onchain transaction histories for addresses and apps.
# - Network information
#
# The schema is extensive and includes many nested types. When processing:
# 1. Index the full schema for future reference
# 2. Note required (!) vs optional fields
# 3. Pay attention to enum values, especially Network types
# 4. Understand the relationships between types
# 5. Use example queries as templates for common patterns

# ------------------------------------------------------
# THIS FILE WAS AUTOMATICALLY GENERATED (DO NOT MODIFY)
# ------------------------------------------------------

interface NFT implements Node {
  id: ID!
  tokenId: String!
  rarityRank: Int @deprecated
  lastSaleEth: BigDecimal @deprecated(reason: "Use lastSale field instead")
  estimatedValueEth: BigDecimal @deprecated(reason: "Use estimatedValue field instead")
  supply: BigDecimal!
  circulatingSupply: BigDecimal!

  """
  ERC-1155 token can have multiple owners
  """
  holdersCount: BigDecimal!
  socialLinks: [SocialLink!]!
  collection: NftCollection!
  metadata: NftMetadata
  traits: [NftTrait!]!
  royaltyInfo(salePrice: String): NftTokenRoyaltyInfo
  transfers(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    order: NftTransferConnectionOrderInput

    """
    Deprecated use the args
    """
    input: NftTransferConnectionInput
  ): NftTransferConnection
  mediasV2: [NftMediaV2!]!
  mediasV3: NftMedias!
  name: String!
  description: String

  """
  ERC-1155 token can have multiple owners
  """
  holders(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    last: Int

    """
    Cursor of an edge (excluded)
    """
    before: String
    followedBy: Address
    addresses: [Address!]

    """
    Deprecated use the args
    """
    input: NftHolderConnectionInput
  ): NftHolderConnection!

  """
  ERC-1155 token can have multiple owners
  """
  holdersFollowedByAddress(input: HoldersFollowedByAddressInput!): [NftHolder!]!

  """
  Token was hidden by owner
  """
  isHidden(input: ByAddressInput!): Boolean!

  """
  Estimated value of the NFT
  """
  estimatedValue: NftValueDenomination

  """
  Last sale of the NFT
  """
  lastSale: NftValueDenomination

  """
  Token balance for a user
  """
  balance(userAddress: Address!): String
}

interface Node {
  id: ID!
}

input NftTransferConnectionOrderInput {
  orderBy: NftTransferSort!
  orderDirection: OrderDirectionOption!
}

enum NftTransferSort {
  TIMESTAMP
}

enum OrderDirectionOption {
  DESC
  ASC
}

input NftTransferConnectionInput {
  offset: Int = 0
  first: Int = 25

  """
  Cursor of an edge (excluded)
  """
  after: String
  search: String
  order: NftTransferConnectionOrderInput
}

union NftMediaV2 = Image | Animation | Audio

input NftHolderConnectionInput {
  first: Int = 25

  """
  Cursor of an edge (excluded)
  """
  after: String

  """
  Cursor of an edge (excluded) to move backwards
  """
  before: String
  search: String
  followedBy: Address
}

input HoldersFollowedByAddressInput {
  address: Address!
}

input ByAddressInput {
  address: Address!
}

interface AbstractToken {
  type: String!
  address: String!
  network: Network!
  balance: String!
  balanceUSD: Float!
  price: Float!
  symbol: String!
  decimals: Float!
}

enum Network {
  ETHEREUM_MAINNET
  POLYGON_MAINNET
  OPTIMISM_MAINNET
  GNOSIS_MAINNET
  BINANCE_SMART_CHAIN_MAINNET
  FANTOM_OPERA_MAINNET
  AVALANCHE_MAINNET
  ARBITRUM_MAINNET
  CELO_MAINNET
  HARMONY_MAINNET
  MOONRIVER_MAINNET
  BITCOIN_MAINNET
  CRONOS_MAINNET
  AURORA_MAINNET
  EVMOS_MAINNET
  BASE_MAINNET
  BLAST_MAINNET
  SOLANA_MAINNET
  DEGEN_MAINNET
  MODE_MAINNET
  ZKSYNC_MAINNET
  MANTLE_MAINNET
  SCROLL_MAINNET
  MOONBEAM_MAINNET
  LINEA_MAINNET
  ZORA_MAINNET
  METIS_MAINNET
  WORLDCHAIN_MAINNET
  SHAPE_MAINNET
  OPBNB_MAINNET
  APECHAIN_MAINNET
  MORPH_MAINNET
  BOB_MAINNET
  UNICHAIN_MAINNET
  CORE_MAINNET
  RACE_MAINNET
  FRAX_MAINNET
  B2_MAINNET
  TAIKO_MAINNET
  CYBER_MAINNET
  ZERO_MAINNET
  IMMUTABLEX_MAINNET
  ARBITRUM_NOVA_MAINNET
  XAI_MAINNET
  REDSTONE_MAINNET
  POLYGON_ZKEVM_MAINNET
  FLOW_MAINNET
  INK_MAINNET
  SONIC_MAINNET
  SONEIUM_MAINNET
  ABSTRACT_MAINNET
  ROOTSTOCK_MAINNET
  BERACHAIN_MAINNET
  STORY_MAINNET
  RONIN_MAINNET
  LENS_MAINNET
  SUPERSEED_MAINNET
  HYPEREVM_MAINNET
  ASTAR_MAINNET
}

interface AbstractDisplayItem {
  type: String!
}

interface AbstractPositionBalance {
  type: String!
  key: String
  address: String!
  network: Network!
  appId: String!
  groupId: String!
  groupLabel: String
  displayProps: DisplayProps
}

interface AbstractMetadataItem {
  type: String!
}

interface MarketData {
  type: MarketDataType!
  isExchangeable: Boolean!
  price(currency: Currency = USD): Float
}

enum MarketDataType {
  COIN_GECKO
  JUPITER
  ONCHAIN
}

enum Currency {
  USD
  EUR
  GBP
  CAD
  CNY
  KRW
  JPY
  RUB
  AUD
  NZD
  CHF
  SGD
  INR
  BRL
  ETH
  BTC
  HKD
  SEK
  NOK
  MXN
  TRY
}

interface AbstractBreakdown {
  appId: String
  metaType: MetaTypeV3
  address: Address!
  network: Network!
  balanceUSD: Float!
  type: BreakdownType!
  breakdown: [AbstractBreakdown!]!
}

enum MetaTypeV3 {
  WALLET
  SUPPLIED
  BORROWED
  CLAIMABLE
  VESTING
  LOCKED
  NFT
}

enum BreakdownType {
  POSITION
  TOKEN
  NON_FUNGIBLE_TOKEN
}

interface AbstractPosition {
  appId: String!
  type: ContractType!
  network: Network!
}

enum ContractType {
  POSITION
  BASE_TOKEN
  APP_TOKEN
  NON_FUNGIBLE_TOKEN
}

interface AbstractAppView {
  label: String!
  type: AppViewType!
  positionType: String
}

enum AppViewType {
  list
  split
  dropdown
}

interface CollectionEvent implements Node {
  id: ID!
  timestamp: Int!
  txHash: String!
  intention: String
  event: CollectionEventOld! @deprecated(reason: "Use `CollectionEvent` instead")
  token: NftToken!
  fromAccount: Account!
  toAccount: Account!
}

union CollectionEventOld = EventSale | EventTransfer

type EventSale {
  timestamp: Int!
  txHash: String!
  payments: [NftPayment!]!
}

type EventTransfer {
  timestamp: Int!
  txHash: String!
}

interface NftCollectionTraitGroupBase implements Node {
  id: ID!
  name: String!
  display: NftTraitDisplayType!
}

enum NftTraitDisplayType {
  STRING
  NUMBER
  BOOST_NUMBER
  BOOST_PERCENTAGE
  DATE
}

type PageInfo {
  hasPreviousPage: Boolean!
  hasNextPage: Boolean!
  startCursor: String
  endCursor: String
}

type Animation {
  originalUri: String!

  """
  File size in bytes. Return `null` if unknown.
  """
  fileSize: Int

  """
  File mime type from https://www.iana.org/assignments/media-types/media-types.xhtml
  """
  mimeType: String
  url: String! @deprecated(reason: "Use `original` instead.")

  """
  Returns a link of the original animation
  """
  original: String!
}

type AnimationEdge {
  node: Animation!
  cursor: String!
}

type AnimationConnection {
  edges: [AnimationEdge!]!
  pageInfo: PageInfo!
}

type Audio {
  originalUri: String!
  original: String!

  """
  File size in bytes. Return `null` if unknown.
  """
  fileSize: Int

  """
  File mime type from https://www.iana.org/assignments/media-types/media-types.xhtml
  """
  mimeType: String
}

type AudioEdge {
  node: Audio!
  cursor: String!
}

type AudioConnection {
  edges: [AudioEdge!]!
  pageInfo: PageInfo!
}

type Image {
  originalUri: String!

  """
  See https://blurha.sh/
  """
  blurhash: String
  width: Int
  height: Int

  """
  File size in bytes. Return `null` if unknown.
  """
  fileSize: Int

  """
  File mime type from https://www.iana.org/assignments/media-types/media-types.xhtml
  """
  mimeType: String
  url(
    """
    Deprecated, use `width` or the predefined field sizes
    """
    input: ImageUrlInput
    width: Int
    format: ImageFormat
  ): String!
  predominantColor: String

  """
  Returns a link of the image 100px wide
  """
  thumbnail: String!

  """
  Returns a link of the image 250px wide
  """
  medium: String!

  """
  Returns a link of the image 500px wide
  """
  large: String!

  """
  Returns a link of the original image
  """
  original: String!
}

input ImageUrlInput {
  size: ImageSize!
}

enum ImageSize {
  THUMBNAIL
  MEDIUM
  LARGE
  ORIGINAL
}

enum ImageFormat {
  webp
  avif
  json
}

type ImageEdge {
  node: Image!
  cursor: String!
}

type ImageConnection {
  edges: [ImageEdge!]!
  pageInfo: PageInfo!
}

type NftMedias {
  images(
    excludeFormats: [NftMediaExcludeFormat!]
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
  ): ImageConnection!
  animations(
    excludeFormats: [NftMediaExcludeFormat!]
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
  ): AnimationConnection!
  audios(
    excludeFormats: [NftMediaExcludeFormat!]
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
  ): AudioConnection!
}

enum NftMediaExcludeFormat {
  SVG
  GIF
  AVIF
  WEBM
  HTML
}

type NftAvatar {
  isCurrentlyHeld: Boolean!
  nft: NftToken!
}

type NftTokenRoyaltyInfo {
  receiver: String!
  amount: String!
}

type NftDenomination {
  network: String!
  address: String!
  symbol: String!
  imageUrl: String
}

type NftValueDenomination {
  valueUsd: Float!
  valueWithDenomination: Float!
  denomination: NftDenomination!
}

type NftToken implements NFT & Node {
  id: ID!
  tokenId: String!
  rarityRank: Int @deprecated
  lastSaleEth: BigDecimal @deprecated(reason: "Use lastSale field instead")
  estimatedValueEth: BigDecimal @deprecated(reason: "Use estimatedValue field instead")
  supply: BigDecimal!
  circulatingSupply: BigDecimal!

  """
  ERC-1155 token can have multiple owners
  """
  holdersCount: BigDecimal!
  socialLinks: [SocialLink!]!
  collection: NftCollection!
  metadata: NftMetadata
  traits: [NftTrait!]!
  royaltyInfo(salePrice: String): NftTokenRoyaltyInfo
  transfers(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    order: NftTransferConnectionOrderInput

    """
    Deprecated use the args
    """
    input: NftTransferConnectionInput
  ): NftTransferConnection
  mediasV2: [NftMediaV2!]!
  mediasV3: NftMedias!
  name: String!
  description: String

  """
  ERC-1155 token can have multiple owners
  """
  holders(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    last: Int

    """
    Cursor of an edge (excluded)
    """
    before: String
    followedBy: Address
    addresses: [Address!]

    """
    Deprecated use the args
    """
    input: NftHolderConnectionInput
  ): NftHolderConnection!

  """
  ERC-1155 token can have multiple owners
  """
  holdersFollowedByAddress(input: HoldersFollowedByAddressInput!): [NftHolder!]!

  """
  Token was hidden by owner
  """
  isHidden(input: ByAddressInput!): Boolean!

  """
  Estimated value of the NFT
  """
  estimatedValue: NftValueDenomination

  """
  Last sale of the NFT
  """
  lastSale: NftValueDenomination

  """
  Token balance for a user
  """
  balance(userAddress: Address!): String
}

type NftTokenErc721 implements NFT & Node {
  id: ID!
  tokenId: String!
  rarityRank: Int @deprecated
  lastSaleEth: BigDecimal @deprecated(reason: "Use lastSale field instead")
  estimatedValueEth: BigDecimal @deprecated(reason: "Use estimatedValue field instead")
  supply: BigDecimal!
  circulatingSupply: BigDecimal!

  """
  ERC-1155 token can have multiple owners
  """
  holdersCount: BigDecimal!
  socialLinks: [SocialLink!]!
  collection: NftCollection!
  metadata: NftMetadata
  traits: [NftTrait!]!
  royaltyInfo(salePrice: String): NftTokenRoyaltyInfo
  transfers(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    order: NftTransferConnectionOrderInput

    """
    Deprecated use the args
    """
    input: NftTransferConnectionInput
  ): NftTransferConnection
  mediasV2: [NftMediaV2!]!
  mediasV3: NftMedias!
  name: String!
  description: String

  """
  ERC-1155 token can have multiple owners
  """
  holders(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    last: Int

    """
    Cursor of an edge (excluded)
    """
    before: String
    followedBy: Address
    addresses: [Address!]

    """
    Deprecated use the args
    """
    input: NftHolderConnectionInput
  ): NftHolderConnection!

  """
  ERC-1155 token can have multiple owners
  """
  holdersFollowedByAddress(input: HoldersFollowedByAddressInput!): [NftHolder!]!

  """
  Token was hidden by owner
  """
  isHidden(input: ByAddressInput!): Boolean!

  """
  Estimated value of the NFT
  """
  estimatedValue: NftValueDenomination

  """
  Last sale of the NFT
  """
  lastSale: NftValueDenomination

  """
  Token balance for a user
  """
  balance(userAddress: Address!): String
}

type NftTokenErc1155 implements NFT & Node {
  id: ID!
  tokenId: String!
  rarityRank: Int @deprecated
  lastSaleEth: BigDecimal @deprecated(reason: "Use lastSale field instead")
  estimatedValueEth: BigDecimal @deprecated(reason: "Use estimatedValue field instead")
  supply: BigDecimal!
  circulatingSupply: BigDecimal!

  """
  ERC-1155 token can have multiple owners
  """
  holdersCount: BigDecimal!
  socialLinks: [SocialLink!]!
  collection: NftCollection!
  metadata: NftMetadata
  traits: [NftTrait!]!
  royaltyInfo(salePrice: String): NftTokenRoyaltyInfo
  transfers(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    order: NftTransferConnectionOrderInput

    """
    Deprecated use the args
    """
    input: NftTransferConnectionInput
  ): NftTransferConnection
  mediasV2: [NftMediaV2!]!
  mediasV3: NftMedias!
  name: String!
  description: String

  """
  ERC-1155 token can have multiple owners
  """
  holders(
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    last: Int

    """
    Cursor of an edge (excluded)
    """
    before: String
    followedBy: Address
    addresses: [Address!]

    """
    Deprecated use the args
    """
    input: NftHolderConnectionInput
  ): NftHolderConnection!

  """
  ERC-1155 token can have multiple owners
  """
  holdersFollowedByAddress(input: HoldersFollowedByAddressInput!): [NftHolder!]!

  """
  Token was hidden by owner
  """
  isHidden(input: ByAddressInput!): Boolean!

  """
  Estimated value of the NFT
  """
  estimatedValue: NftValueDenomination

  """
  Last sale of the NFT
  """
  lastSale: NftValueDenomination

  """
  Token balance for a user
  """
  balance(userAddress: Address!): String
}

type NftTokenEdge {
  node: NftToken!
  cursor: String!
}

type NftTokenConnection {
  edges: [NftTokenEdge!]!
  pageInfo: PageInfo!
}

type EnsMetadata {
  avatar: EnsAvatar
  description: String
  github: String
  twitter: String
  email: String
  website: String
}

union EnsAvatar = NftToken | NftTokenErc721 | NftTokenErc1155 | AvatarUrl

type AvatarUrl {
  url: String!
  mimeType: String
}

type EnsRecord {
  name: Ens!
  metadata: EnsMetadata!
}

type Account implements Node {
  id: ID!
  address: Address!
  displayName: DisplayName!
  avatar(opepenSize: AllowedOpepenSizes! = XS): AccountAvatar!
  avatarUrl: String
  description: Description
  socialLinks: [AccountSocialLink!]!
  ens: String @deprecated(reason: "Use ensRecord instead")
  kind: String!
  contract: Contract
  metadata: [AddressMetadataObject!]!
  isContract: Boolean!
  nftAvatar: NftAvatar @deprecated(reason: "Use avatar instead")
  opepenURI: String!
  blockiesURI: String!
  isFollowedBy(address: Address!): Boolean!
  followStats: FollowerStats
  followers(first: Int, after: String): FollowerConnection!
  following(first: Int, after: String): FollowerConnection!
  ensRecord: EnsRecord
  basename: String
  lensProfile: LensProfile
  farcasterProfile: FarcasterProfile
  label: String
}

enum AllowedOpepenSizes {
  XXS
  XS
  S
  M
  L
  XL
}

type DisplayName {
  value: String!
  source: AccountDisplayNameSource!
}

enum AccountDisplayNameSource {
  ENS
  BASENAME
  LENS
  FARCASTER
  LABEL
  ADDRESS
}

type Description {
  value: String!
  source: AccountDescriptionSource!
}

enum AccountDescriptionSource {
  ENS
  LENS
  FARCASTER
}

type AccountSocialLink {
  url: String!
  name: AccountSocialLinkName!
  source: AccountSocialLinkSource!
}

enum AccountSocialLinkName {
  WEBSITE
  TWITTER
  GITHUB
  EMAIL
  HEY
  WARPCAST
}

enum AccountSocialLinkSource {
  ENS
  LENS
  FARCASTER
}

type FollowerStats {
  followerCount: Int!
  followingCount: Int!
}

type AccountEdge {
  node: Account!
  cursor: String!
}

type FollowerConnection {
  edges: [AccountEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type AccountAvatar {
  value: Avatar!
  source: AccountAvatarSource!
}

union Avatar = NftToken | NftTokenErc721 | NftTokenErc1155 | NftAvatar | AvatarUrl

enum AccountAvatarSource {
  ZAPPER
  ENS
  LENS
  FARCASTER
  OPEPENS
  BLOCKIES
}

type Badge {
  tokenId: Int!
  badgeName: String!
  claimed: Boolean!
  badgeNetwork: Network!
  userAddress: Address!
}

type SocialStats {
  followersCount: Int!
  followedCount: Int!
  addedFollowersCountLast24Hours: Int!
}

"""
Deprecated: Use `Account` instead
"""
type User {
  address: Address!
  ens: String
  avatar: NftToken
  blockiesURI: String!
  blockieUrl: String
  level: Int!
  levelUpXpRequired: Int!
  xp: Int!
  zp: Int!
  pendingZp: Int!
  avatarURI: String
  socialStats: SocialStats!
  badges: [Badge!]!
  followedBy: Boolean!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PaginatedUser {
  edges: [UserEdge!]!
  totalCount: Int!
}

type ActivityFeedApp {
  slug: String!
  name: String!
  url: String
  tags: [String!]!
  imgUrl: String!
  imageUrl: String! @deprecated(reason: "Use imgUrl instead")
  description: String!
  app: App!
}

type NetworkMetadata {
  chainId: Float!
  networkType: NetworkIndexerType!
  name: String!
  url: String!
}

enum NetworkIndexerType {
  EIP_155
  LAYER_ZERO
  WORMHOLE
}

type SocialLink {
  name: String!
  label: String!
  url: String!
  logoUrl: String!
}

type NftCollection implements Node {
  id: ID!
  address: Address!
  subCollectionIdentifier: String!
  name: String!
  displayName: String
  symbol: String!
  description: String!
  network: Network!
  deployer: Address!
  owner: Address!
  creator: Address!
  deployedAt: Timestamp
  ownedAt: Timestamp
  socialLinks: [SocialLink!]!

  """
  Image of the collection as an horizontal rectangle
  """
  bannerImageUrl: String @deprecated(reason: "Use `medias.banner`")

  """
  Image of the collection as a vertical rectangle
  """
  cardImageUrl: String @deprecated(reason: "Use `medias.card`")
  supply: BigDecimal!
  totalSupply: BigDecimal!
  floorPriceEth: BigDecimal @deprecated(reason: "Use floorPrice instead")
  floorPriceSourceMarketPlace: NftDataSourceMarketplace
  topOfferPriceEth: BigDecimal @deprecated(reason: "Use topOfferPrice instead")
  topOfferSourceMarketPlace: NftDataSourceMarketplace
  holdersCount: BigDecimal!
  nftStandard: NftStandard!

  """
  Disabled collection will return `null`
  """
  disabled: Boolean!
  type: NftCollectionType!
  openseaId: String
  spamScore: BigDecimal
  stats: NftCollectionStats!
  isApproved(spenderAddress: Address!, ownerAddress: Address!): Boolean!
  approvalTransaction(spenderAddress: Address!, ownerAddress: Address!): TransactionConfig!
  revokeApprovalTransaction(spenderAddress: Address!, ownerAddress: Address!): TransactionConfig!

  """
  Floor price of the NFT collection
  """
  floorPrice: NftValueDenomination

  """
  Top offer of the NFT collection
  """
  topOfferPrice: NftValueDenomination
  nfts(
    first: Int = 25

    """
    Cursor of an edge (excluded)
    """
    after: String
    tokenIds: [String!]
    owners: [Address!]
    traitIds: [String!]
    order: NftTokenConnectionOrderInput
    traits: [NftTokenTraitInput!]

    """
    Deprecated, use the args
    """
    input: NftConnectionInput
  ): NftTokenConnection!
  events(
    first: Int! = 25

    """
    Cursor of an edge (excluded)
    """
    after: String
    tokenIds: [String!]
    owners: [Address!]
    followedBy: Address
    traits: [NftTokenTraitInput!]
    period: NftPaymentStatsPeriod

    """
    Deprecated: use the args
    """
    input: CollectionEventConnectionInput
  ): CollectionEventConnection!
  traitGroups: [NftCollectionTraitGroupBase!]!
  traitGroupValues(input: NftCollectionTraitValuesArgs!): NftCollectionTraitValueConnection!
  traits: [NftCollectionTraitType!]!
  holders(input: NftHolderConnectionInput, first: Int, after: String, addresses: [String!]): PaginatedNftHolder!
  medias: NftCollectionMedias!
  circulatingSupply: BigDecimal!
  totalCirculatingSupply: BigDecimal!
  nameAfterOverride: String!
  groups: [NftCollectionGroup!]!
  marketCap: BigDecimal
  networkV2: NetworkObject!
}

"""
`Date` type as integer. Type represents date and time as number of milliseconds from start of UNIX epoch.
"""
scalar Timestamp

enum NftDataSourceMarketplace {
  OPENSEA
  X2Y2
  LOOKSRARE
  RESERVOIR
  BLUR
}

enum NftStandard {
  ERC_721
  ERC_1155
}

enum NftCollectionType {
  GENERAL
  BRIDGED
  BADGE
  POAP
  TICKET
  ACCOUNT_BOUND
  WRITING
  GAMING
  ART_BLOCKS
  BRAIN_DROPS
  LENS_PROFILE
  LENS_FOLLOW
  LENS_COLLECT
  ZORA_ERC721
  ZORA_ERC1155
  BLUEPRINT
}

input NftTokenConnectionOrderInput {
  orderBy: NftTokenSort!
  orderDirection: OrderDirectionOption = ASC
}

enum NftTokenSort {
  RARITY_RANK
  LAST_SALE_ETH
  ESTIMATED_VALUE_ETH
}

input NftTokenTraitInput {
  type: String!
  value: String!
}

input NftConnectionInput {
  first: Int = 25

  """
  Cursor of an edge (excluded)
  """
  after: String

  """
  Cursor of an edge (excluded) to move backwards
  """
  before: String
  search: String
  tokenIds: [String!]
  owners: [Address!]
  traitIds: [String!]
  order: NftTokenConnectionOrderInput
  traits: [NftTokenTraitInput!]
}

enum NftPaymentStatsPeriod {
  Week
  Month
  Quarter
}

input CollectionEventConnectionInput {
  first: Int = 25

  """
  Cursor of an edge (excluded)
  """
  after: String

  """
  Cursor of an edge (excluded) to move backwards
  """
  before: String
  search: String
  tokenIds: [String!]
  owners: [Address!]
  followedBy: Address
  traits: [NftTokenTraitInput!]
  period: NftPaymentStatsPeriod
}

input NftCollectionTraitValuesArgs {
  first: Int = 10

  """
  Cursor of an edge (excluded)
  """
  after: String
  traitName: String!
  search: String
}

union NftCollectionTraitType = NftCollectionTraitString | NftCollectionTraitNumeric

type NftCollectionTraitString {
  value: String!
  values: [NftCollectionTraitValue!]
}

type NftCollectionTraitNumeric {
  value: String!
  display: NftTraitDisplayType!
  min: Float
  max: Float
}

type NftCollectionMedias {
  """
  ID of the collection
  """
  id: String!

  """
  Image of the collection as an horizontal rectangle
  """
  banner(excludeFormats: [NftMediaExcludeFormat!]): Image

  """
  Image of the collection as a vertical rectangle
  """
  card(excludeFormats: [NftMediaExcludeFormat!]): Image

  """
  Image of the collection as a square
  """
  logo(excludeFormats: [NftMediaExcludeFormat!]): Image
}

type NftCollectionEdge {
  node: NftCollection!
  cursor: String!
}

type NftCollectionsForOwnersCollectionsConnection {
  edges: [NftCollectionEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type NFTDisplayItem {
  type: String!
  network: Network!
  collectionAddress: Address!
  tokenId: String!
  quantity: Float
  nftToken: NftToken
  isMint: Boolean
  isBurn: Boolean
  nftCollection: NftCollection
}

type AppFungibleToken {
  address: Address!
  network: Network!
  price: BigDecimal
  symbol: String!
  decimals: Float!
  label: String!
  imageUrls: [String!]!
  appImageUrl: String!
  isDebt: Boolean!
}

type TokenDisplayItem {
  type: String!
  network: Network!
  tokenAddress: Address!
  amountRaw: String!
  id: ID!
  token: FunginbleToken
  tokenV2: FungibleToken
}

union FunginbleToken = AppFungibleToken | BaseFungibleToken

type BaseFungibleToken {
  address: Address!
  network: Network!
  price: BigDecimal
  symbol: String!
  decimals: Float!
  imageUrl: String
}

type ActivityInterpretation {
  description: String!
  descriptionDisplayItems: [ActivityFeedDisplayItem!]!
  inboundAttachments: [ActivityFeedDisplayItem!]!
  outboundAttachments: [ActivityFeedDisplayItem!]!
  inboundAttachmentsConnection(
    first: Int
    after: String
    attachmentTypes: [SupportedEventDisplayItem!]
  ): AttachmentConnection!
  outboundAttachmentsConnection(
    first: Int
    after: String
    attachmentTypes: [SupportedEventDisplayItem!]
  ): AttachmentConnection!
  processedDescription: String!
}

union ActivityFeedDisplayItem =
  | ActorDisplayItem
  | AppDisplayItem
  | AppContractNetworkDisplayItem
  | ChatChannelDisplayItem
  | CompositeDisplayItem
  | ImageDisplayItem
  | NetworkDisplayItem
  | NFTCollectionDisplayItem
  | NFTDisplayItem
  | NumberDisplayItem
  | ProposalDisplayItemObject
  | StringDisplayItem
  | TokenContractDisplayItem
  | TokenDisplayItem
  | TransactionDisplayItem

type ActorDisplayItem {
  type: String!
  address: Address!
  actor: Actor! @deprecated(reason: "Use `account` instead")
  actorV2: ActorV2! @deprecated(reason: "Use `account` instead")
  account: Account!
}

union Actor = User | Wallet | Contract

type Wallet {
  address: Address!
  ens: String
}

union ActorV2 = Account | Contract

type AppDisplayItem {
  type: String!
  id: ID!
  appId: String! @deprecated(reason: "Use app.slug instead")
  network: Network!
  app: ActivityFeedApp
}

type AppContractNetworkDisplayItem {
  type: String!
  address: String!
  network: Network!
  app: ActivityFeedApp
}

type ChatChannelDisplayItem {
  type: String!
  channelId: String!
}

type CompositeDisplayItem {
  type: String!
  itemCount: Int!
  items(first: Int = 1000): [ActivityFeedLeafDisplayItem!]!
}

union ActivityFeedLeafDisplayItem =
  | ActorDisplayItem
  | AppDisplayItem
  | AppContractNetworkDisplayItem
  | ChatChannelDisplayItem
  | ImageDisplayItem
  | NetworkDisplayItem
  | NFTCollectionDisplayItem
  | NFTDisplayItem
  | NumberDisplayItem
  | ProposalDisplayItemObject
  | StringDisplayItem
  | TokenContractDisplayItem
  | TokenDisplayItem
  | TransactionDisplayItem

type ImageDisplayItem {
  type: String!
  url: String!
}

type NetworkDisplayItem {
  type: String!
  chainId: Float!
  networkType: NetworkIndexerType!
  networkMetadata: NetworkMetadata
}

type NFTCollectionDisplayItem {
  type: String!
  network: Network!
  collectionAddress: Address!
  quantity: Float
  nftCollection: NftCollection
}

type NumberDisplayItem {
  type: String!
  value: Float! @deprecated(reason: "use numberValue instead")
  numberValue: Float!
}

type ProposalDisplayItemObject {
  type: String!
  id: ID!
  network: Network!
  platform: String!
}

type StringDisplayItem {
  type: String!
  value: String! @deprecated(reason: "use stringValue instead")
  stringValue: String!
}

type TokenContractDisplayItem {
  type: String!
  network: Network!
  address: Address!
  token: FunginbleToken
}

type TransactionDisplayItem {
  type: String!
  event: ActivityEvent!
}

enum SupportedEventDisplayItem {
  Actor
  App
  AppContractNetwork
  ChatChannel
  Composite
  Image
  Network
  Nft
  NftCollection
  Number
  Proposal
  String
  Token
  TokenContract
  Transaction
}

type ActivityFeedDisplayItemEdge {
  node: ActivityFeedDisplayItem!
  cursor: String!
}

type AttachmentConnection {
  edges: [ActivityFeedDisplayItemEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
  nftCount: Int!
}

type ActivityEventInterpreter {
  id: String!
  priority: Int!
  category: ActivityEventTopic!
  app: ActivityFeedApp
  isCodeless: Boolean!
}

enum ActivityEventTopic {
  Defi
  Swaps
  NftMints
  NftSales
  NftFi
  NftBidding
  Social
  Bridge
  Gaming
  Governance
  Fundraising
  Art
  Metaverse
  None
  Nft
  All
  Unknown
}

type OnChainTransactionReceipt {
  contractAddress: Address
  gasUsed: Int!
  status: Int!
}

type DecodedInput {
  signature: String!
  data: [String!]!
}

type DecodedInputDataValue {
  name: String!
  value: String!
}

type DecodedInputV2 {
  signature: String!
  data: [DecodedInputDataValue!]!
}

type OnChainTransactionLog {
  address: String!
  data: String!
  topics: [String!]!
  logIndex: Int!
  transactionIndex: Int!
}

type OnChainTransaction {
  network: Network!
  hash: String!
  nonce: Int!
  blockHash: String!
  blockNumber: Int!
  value: String!
  gasPrice: String!
  gas: Int!
  input: String!
  from: Address!
  fromUser: Account
  to: Address
  timestamp: Timestamp!
  receipt: OnChainTransactionReceipt
  logs: [OnChainTransactionLog!]!
  link: String!
  fromEns: String
  transactionFee: Float!
  transactionPrice: Float!
  toUser: Account
  decodedInput: DecodedInput
  decodedInputV2: DecodedInputV2
}

type ActivityPerspective {
  type: String!
  value: String!
}

type ActivityEvent {
  key: String!
  network: Network!
  source: String!
  eventType: String!
  isAbiAvailable: Boolean!
  isEditable: Boolean!
  interpreterId: String
  interpreter: ActivityEventInterpreter
  timestamp: Timestamp!
  perspective: ActivityPerspective!
  interpretation: ActivityInterpretation!
  transaction: OnChainTransaction
  similarEventCount: Int
  app: ActivityFeedApp
  accountDeltasV2(first: Int = 6, after: String): ActivityAccountDeltaConnection!
  perspectiveDelta: ActivityAccountDelta
  sigHash: String
}

type ActivityEventEdge {
  node: ActivityEvent!
  cursor: String!
}

type ActivityEventConnection {
  edges: [ActivityEventEdge!]!
  pageInfo: PageInfo!
}

type AccountTransactionHistoryEntry {
  subject: String!
  hash: String!
  network: Network!
  blockTimestamp: Timestamp!
  fromAddress: String!
  toAddress: String
  methodSighash: String
}

type AccountTransactionHistoryEdge {
  node: AccountTransactionHistoryEntry!
  cursor: String!
}

type TimelineEventV2 implements Node {
  id: ID!
  hash: String!
  eventHash: String!
  network: Network!
  index: Int!
  fromAddress: Account!
  toAddress: Account
  methodSighash: String!
  timestamp: Timestamp!
  interpreterId: String!
  value: String!
  rawInput: String!
  gas: String!
  networkObject: NetworkObject
  app: App
  transaction: OnChainTransaction!
  interpretation: ActivityInterpretation!
  perspective: String!
  perspectiveDelta: ActivityAccountDelta
  methodSignature: String
  deltas(first: Int = 6, after: String): ActivityAccountDeltaConnection!
}

type ChatMessage implements Node {
  id: ID!
  channelId: ID!
  fromAddress: String!
  createdAt: Timestamp!
  isConsecutive: Boolean!
  content: ChatMessageContent!
}

union ChatMessageContent =
  | ChatMessageTextContent
  | ChatMessageNewMemberContent
  | ChatMessageGifContent
  | ChatMessageReplyContent

type ChatMessageTextContent {
  type: String!
  text: String!
}

type ChatMessageNewMemberContent {
  type: String!
  initialShares: Int!
}

type ChatMessageGifContent {
  type: String!
  giphyId: String!
}

type ChatMessageReplyContent {
  type: String!
  text: String!
}

type ChatMessageEdge {
  node: ChatMessage!
  cursor: String!
}

type FarcasterTokenFeedItem implements Node {
  id: ID!
  type: String!
  chainId: Int!
  tokenAddress: Address!
  token: FungibleToken
  farcasterContext(fid: Int): FarcasterFip2Context!
  buyCount: Int
  buyerCount: Int
  buyerCount24h: Int
}

type FarcasterTokenFeedItemEdge {
  node: FarcasterTokenFeedItem!
  cursor: String!
}

type FarcasterTokenFeedRelevantSwapParticipant implements Node {
  id: ID!
  timeBucket: Timestamp!
  fid: Int!
  isBuy: Boolean!
  amount: Float!
  totalSwaps: Int!
  latestSwapDate: Timestamp!
  latestSwapHash: String!
}

type FarcasterTokenFeedRelevantSwapParticipantEdge {
  node: FarcasterTokenFeedRelevantSwapParticipant!
  cursor: String!
}

type NeynarCastV2 implements Node {
  id: ID!
  cast: JSON!
  farcasterContext: FarcasterFip2Context!
}

"""
The `JSON` scalar type represents JSON values as specified by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).
"""
scalar JSON

type FarcasterTopCast implements Node {
  id: ID!
  hash: String!
  authorFid: Int!
  parentHash: String
  parentUrl: String
  rootParentUrl: String
  parentAuthorFid: Int
  authorPowerBadge: Boolean!
  mentionedFids: [Int!]!
  text: String!
  timestamp: Timestamp!
  author: FarcasterProfile
}

type FarcasterTopCastEdge {
  node: FarcasterTopCast!
  cursor: String!
}

type FarcasterMiniAppFeedItemFrameAuthor {
  object: String!
  fid: Int!
  username: String
  display_name: String
  pfp_url: String
  custody_address: String
}

type FarcasterMiniAppFeedItemFrameManifestAccountAssociation {
  header: String!
  payload: String!
  signature: String!
}

type FarcasterMiniAppFeedItemFrameManifestFrame {
  version: String!
  name: String!
  home_url: String!
  icon_url: String!
  image_url: String
  button_title: String
  splash_image_url: String
  splash_background_color: String
  webhook_url: String
}

type FarcasterMiniAppFeedItemFrameManifest {
  account_association: FarcasterMiniAppFeedItemFrameManifestAccountAssociation!
  frame: FarcasterMiniAppFeedItemFrameManifestFrame
}

type FarcasterMiniAppFeedItemFrame {
  version: String!
  title: String
  image: String
  frames_url: String
  author: FarcasterMiniAppFeedItemFrameAuthor
  manifest: FarcasterMiniAppFeedItemFrameManifest
}

type FarcasterMiniAppFeedItem implements Node {
  id: ID!
  homeUrl: String!
  domain: String!
  type: String!
}

type FarcasterAccountFeedItem implements Node {
  id: ID!
  fid: Int!
}

type FarcasterNftCollectionFeedItem implements Node {
  id: ID!
  type: String!
  collectionAddress: String!
  chainId: Int!
  collection: NftCollection
}

type FarcasterRelevantSwapFeedItem implements Node {
  id: ID!
  type: String!
  swap: ChannelFeedSwap
}

type FarcasterFeedItem implements Node {
  id: ID!
  item: FcTrendItem!
}

union FcTrendItem =
  | FarcasterTokenFeedItem
  | FarcasterMiniAppFeedItem
  | FarcasterMiniAppGroupFeedItem
  | FarcasterCastFeedItem
  | FarcasterNftCollectionFeedItem
  | FarcasterAccountFeedItems
  | FarcasterRelevantSwapFeedItem
  | FarcasterRelevantNftPurchaseFeedItem

type FarcasterMiniAppGroupFeedItem implements Node {
  id: ID!
  type: String!
  miniApps: [FarcasterMiniAppFeedItem!]!
}

type FarcasterCastFeedItem implements Node {
  id: ID!
  hash: String!
  type: String!
}

type FarcasterAccountFeedItems implements Node {
  id: ID!
  items: [FarcasterAccountFeedItem!]!
  type: String!
}

type FarcasterRelevantNftPurchaseFeedItem implements Node {
  id: ID!
  type: String!
}

type FarcasterFeedItemEdge {
  node: FarcasterFeedItem!
  cursor: String!
}

type FarcasterFeedV2Edge {
  node: FcTrendItem!
  cursor: String!
}

type FarcasterTokenFeedV2Edge {
  node: FarcasterTokenFeedItem!
  cursor: String!
}

type FarcasterNftCollectionFeedV2Edge {
  node: FarcasterNftCollectionFeedItem!
  cursor: String!
}

type FarcasterSwapFeedV2Edge {
  node: FarcasterRelevantSwapFeedItem!
  cursor: String!
}

type FarcasterTokenFeedV2Connection {
  edges: [FarcasterTokenFeedV2Edge!]!
  pageInfo: PageInfo!
}

type FarcasterNftFeedV2Connection {
  edges: [FarcasterNftCollectionFeedV2Edge!]!
  pageInfo: PageInfo!
}

type FarcasterSwapFeedV2Connection {
  edges: [FarcasterSwapFeedV2Edge!]!
  pageInfo: PageInfo!
}

type FarcasterTrendingTokenFeedConnection {
  edges: [FarcasterTokenFeedItemEdge!]!
  pageInfo: PageInfo!
}

type FarcasterNftSale implements Node {
  id: ID!
  fid: Int!
  chainId: Int!
  collectionAddress: Address!
  tokenId: String!
  amount: String!
  timestamp: Timestamp!
  transactionHash: String!
  usdVolume: Float!
  isBuy: Boolean!
  paymentTokenAmount: String!
}

type FarcasterNftSaleEdge {
  node: FarcasterNftSale!
  cursor: String!
}

type ChannelFeedSwap implements Node {
  id: ID!
  fid: Int!
  transactionHash: String!
  timestamp: Timestamp!
  chainId: Int!
  volumeUsd: String!
  amount: Float!
  isBuy: Boolean!
  parentUrl: String!
  topHat: FarcasterTopHat
  farcasterContext(fid: Int): FarcasterFip2Context!
  network: NetworkObject!
  token: FungibleToken
  profile: FarcasterProfile
  account: Account!
}

type ChannelFeedItemEdge {
  node: ChannelFeedNodeItem!
  cursor: String!
}

union ChannelFeedNodeItem = ChannelFeedSwap | FarcasterTopCast | FarcasterNftSale

type TokenChannelFeedItemEdge {
  node: TokenChannelFeedNodeItem!
  cursor: String!
}

union TokenChannelFeedNodeItem = ChannelFeedSwap | FarcasterTopCast

type TokenChannelFeedConnection {
  edges: [TokenChannelFeedItemEdge!]!
  pageInfo: PageInfo!
}

type FarcasterFip2Context {
  id: ID!
  uri: String!
  likeCount: Int!
  recastCount: Int!
  commentCount: Int! @deprecated(reason: "Use replyCount")
  replyCount: Int!
  quoteCount: Int!
  isLiked: Boolean!
  isRecast: Boolean!
}

type TokenNetworkAndAddress {
  network: Network!
  address: String!
}

type SupportedTokenHolder implements Node {
  id: ID!
  holderAddress: String!
  value: String!
  percentileShare: Float!
  account: Account!
}

type SupportedTokenHolderEdge {
  node: SupportedTokenHolder!
  cursor: String!
}

type PaginatedSupportedTokenHolders {
  edges: [SupportedTokenHolderEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type SupportedBaseToken implements Node {
  id: ID!
  address: String!
  network: Network!
  label: String
  name: String!
  decimals: Float!
  imgUrl: String!
  symbol: String!
  holders: PaginatedSupportedTokenHolders
  holdersFollowedByAddress: [SupportedTokenHolder!]!
  coingeckoID: String
  canExchange: Boolean
  verified: Boolean!
  hide: Boolean
  totalSupply: String
  price: Float!
  dailyVolume: Float
  createdAt: Timestamp!
  updatedAt: Timestamp!
}

type GroupedSupportedBaseToken {
  uniqKey: String!
  name: String!
  symbol: String!
  coingeckoID: String
  imgUrl: String!
  newtworksAndAddresses: [TokenNetworkAndAddress!]!
  canExchange: Boolean
  hide: Boolean
}

type SupportedBaseTokenHistoricData {
  price1HourAgo: Float!
  price24HoursAgo: Float!
  price7DaysAgo: Float!
  price30DaysAgo: Float!
  volume1HourAgo: Float!
  volume24HoursAgo: Float!
  volume7DaysAgo: Float!
  volume30DaysAgo: Float!
  priceChange1Hour: Float
  priceChange24Hours: Float
  priceChange7Days: Float
  priceChange30Days: Float
  volumeChange1Hour: Float
  volumeChange24Hours: Float
  volumeChange7Days: Float
  volumeChange30Days: Float
}

type TrendingTokenEdge {
  node: SupportedBaseToken!
  cursor: String!
  historicData: SupportedBaseTokenHistoricData!
}

type DisplayItemWrapper {
  label: AbstractDisplayItem!
  value: AbstractDisplayItem!
}

type DisplayItemString implements AbstractDisplayItem {
  type: String!
  valueString: String!
}

type DisplayItemNumber implements AbstractDisplayItem {
  type: String!
  valueNumber: Float!
}

type DisplayItemDollar implements AbstractDisplayItem {
  type: String!
  valueDollar: Float!
}

type DisplayItemPercentage implements AbstractDisplayItem {
  type: String!
  valuePct: Float!
}

type DisplayItemTranslation implements AbstractDisplayItem {
  type: String!
  valueTranslation: String!
}

type StatsItem {
  label: String!
  value: AbstractDisplayItem!
}

type DisplayProps {
  label: String!
  secondaryLabel: AbstractDisplayItem
  tertiaryLabel: AbstractDisplayItem
  images: [String!]!
  statsItems: [StatsItem!]
  balanceDisplayMode: BalanceDisplayMode
}

enum BalanceDisplayMode {
  DEFAULT
  UNDERLYING
}

type TokenWithMetaType {
  metaType: MetaTypeV3
  token: AbstractToken!
}

type ContractPositionBalance implements AbstractPositionBalance {
  type: String!
  key: String
  address: String!
  network: Network!
  appId: String!
  groupId: String!
  groupLabel: String
  displayProps: DisplayProps
  balanceUSD: Float!
  tokens: [TokenWithMetaType!]!
}

type AppTokenPositionBalance implements AbstractToken & AbstractPositionBalance {
  type: String!
  address: String!
  network: Network!
  balance: String!
  balanceUSD: Float!
  price: Float!
  symbol: String!
  decimals: Float!
  key: String
  appId: String!
  groupId: String!
  groupLabel: String
  displayProps: DisplayProps
  supply: Float!
  pricePerShare: [Float!]!
  tokens: [AbstractToken!]!
  hasMissingUnderlyingTokenPrice: Boolean!
}

type BaseTokenPositionBalance implements AbstractToken {
  type: String!
  address: String!
  network: Network!
  balance: String!
  balanceUSD: Float!
  price: Float!
  symbol: String!
  decimals: Float!
  priceSource: Erc20TokenPriceSource
}

enum Erc20TokenPriceSource {
  ORACLE
  COINGECKO
  SPL
  OCP_V1
  OCP_V2
  NONE
}

type NftBalanceCollection {
  id: String!
  name: String!
  floorPrice: Float!
  floorPriceUSD: Float!
  img: String!
  imgBanner: String!
  imgProfile: String!
  imgFeatured: String!
  description: String!
  socials: [NftSocialLink!]!
  owners: Float!
  items: Float!
  volume24h: Float!
  volume24hUSD: Float!
}

type NftSocialLink {
  name: String!
  url: String!
}

type NftAsset {
  balance: Float!
  balanceUSD: Float!
  assetImg: String!
  assetName: String!
  tokenId: String!
}

type NonFungiblePositionBalance implements AbstractToken {
  type: String!
  address: String!
  network: Network!
  balance: String!
  balanceUSD: Float!
  price: Float!
  symbol: String!
  decimals: Float!
  collection: NftBalanceCollection
  assets: [NftAsset!]
}

type StringMetadataItem implements AbstractMetadataItem {
  type: String!
  valueString: String!
}

type NumberMetadataItem implements AbstractMetadataItem {
  type: String!
  valueNumber: Float!
}

type DollarMetadataItem implements AbstractMetadataItem {
  type: String!
  valueDollar: Float!
}

type PercentageMetadataItem implements AbstractMetadataItem {
  type: String!
  valuePct: Float!
}

type MetadataItemWithLabel {
  label: String!
  item: AbstractMetadataItem!
}

type BalanceJobId {
  jobId: String!
}

type BalanceJobStatus {
  jobId: String!
  status: String!
}

type PortfolioTotals {
  total: Float!
  appsTotal: Float!
  totalWithNFT: Float!
  totalByNetwork: [TotalByNetwork!]!
  totalByNetworkWithNFT: [TotalByNetwork!]!
  totalByAddress: [TotalByAddress!]!
  claimables: [ClaimableToken!]!
  debts: [ClaimableToken!]!
  holdings: [PortfolioHolding!]!
}

type PortfolioHolding {
  key: String!
  label: String!
  balanceUSD: Float!
  pct: Float!
}

type ClaimableToken {
  appId: String!
  address: String!
  token: AbstractToken!
}

type TotalByNetwork {
  network: Network!
  total: Float!
}

type TotalByAddress {
  address: String!
  total: Float!
}

type ProductItem {
  label: String!
  assets: [AbstractPositionBalance!]!
  meta: [MetadataItemWithLabel!]!
}

type NftBalance {
  network: Network!
  balanceUSD: Float!
}

type Portfolio {
  proxies: [ProxyAccount!]!
  tokenBalances: [TokenBalance!]! @deprecated(reason: "Use portfolioV2 tokenBalances instead")
  appBalances: [AppBalance!]! @deprecated(reason: "Use portfolioV2 appBalances instead")
  nftBalances: [NftBalance!]! @deprecated(reason: "Use portfolioV2 nftBalances instead")
  totals: PortfolioTotals!
}

type AppBalance {
  key: String!
  address: String!
  appId: String!
  appName: String!
  appImage: String!
  network: Network!
  updatedAt: Timestamp!
  balanceUSD: Float!
  products: [ProductItem!]!
}

type CoinGeckoMarketData implements MarketData {
  type: MarketDataType!
  isExchangeable: Boolean!
  price(currency: Currency = USD): Float
  coinGeckoId: String!
  coinGeckoUrl: String!
  totalSupply: String
  dailyVolume: Float
  marketCap: Float
}

type JupiterMarketData implements MarketData {
  type: MarketDataType!
  isExchangeable: Boolean!
  price(currency: Currency = USD): Float
}

type OnchainMarketData implements MarketData {
  type: MarketDataType!
  isExchangeable: Boolean!
  price(currency: Currency = USD): Float
  historicalPrice(currency: Currency = USD, timestamp: Timestamp!): OnchainHistoricalPrice
  marketCap: Float
  totalLiquidity(currency: Currency = USD): Float
  totalGasTokenLiquidity: Float
  priceChange(since: Timestamp!): Float
  priceChange5m: Float
  priceChange1h: Float
  priceChange24h: Float
  volume24h(currency: Currency = USD): Float
  priceTicks(currency: Currency!, timeFrame: TimeFrame!): [OnchainMarketDataPriceTick!]!
  priceTicksByLength(
    currency: Currency!
    tickLength: TickLength!
    first: Int = 12
    after: String
  ): OnchainMarketDataPriceTickConnection!
  latestSwaps(first: Int = 12, after: String): OnchainMarketDataLatestSwapConnection!
  latestFarcasterSwaps(
    first: Int = 6
    after: String
    filters: OnchainMarketDataLatestFarcasterSwapFilterArgs
  ): OnchainMarketDataLatestFarcasterSwapConnection!
  latestRelevantFarcasterSwaps(
    fid: Int!
    first: Int = 6
    after: String
    filters: OnchainMarketDataLatestFarcasterSwapFilterArgs
  ): OnchainMarketDataLatestFarcasterSwapConnection!
}

enum TimeFrame {
  HOUR
  DAY
  WEEK
  MONTH
  YEAR
}

enum TickLength {
  FIVE_MINUTE
  THIRTY_MINUTE
  ONE_HOUR
  FOUR_HOUR
  ONE_DAY
}

input OnchainMarketDataLatestFarcasterSwapFilterArgs {
  minimumUsdVolume: Int
  ignoreAutomated: Boolean
  isBuy: Boolean
}

type OnchainMarketDataPriceTick implements Node {
  id: ID!
  median: Float!
  open: Float!
  close: Float!
  high: Float!
  low: Float!
  timestamp: Timestamp!
}

type OnchainMarketDataPriceTickEdge {
  node: OnchainMarketDataPriceTick!
  cursor: String!
}

type OnchainMarketDataPriceTickConnection {
  edges: [OnchainMarketDataPriceTickEdge!]!
  pageInfo: PageInfo!
}

type FungibleToken implements Node {
  id: ID!
  address: Address!
  name: String!
  symbol: String!
  decimals: Int!
  totalSupply: String
  networkId: Int!

  """
  Use onchainMarketData for EVM tokens
  """
  marketData: MarketData
  credibility: Float
  rank: Int
  securityRisk: FungibleTokenSecurityRisk
  networkV2: NetworkObject!
  isHoldersSupported: Boolean!
  network: Network! @deprecated(reason: "Use `networkV2` instead")
  imageUrl: String! @deprecated(reason: "Use `imageUrlV2`, which will return null if the image is not found")

  """
  Returns the token image URL or null if not found
  """
  imageUrlV2: String
  priceData: OnchainMarketData
  onchainMarketData: OnchainMarketData @deprecated(reason: "Use priceData instead.")
  isVerified: Boolean!
  holders(first: Float!, after: String, addresses: [String!]): PaginatedSupportedTokenHolders
  deployer: Account
  deployTransaction: OnChainTransaction
  farcasterHolders(first: Int!, after: String): PaginatedSupportedTokenHolders
  followedFarcasterHolders(first: Int! = 20, after: String, fid: Int!): PaginatedSupportedTokenHolders
}

type FungibleTokenSecurityRisk {
  reason: HiddenTokenReason!
  strategy: HiddenTokenMethod!
}

enum HiddenTokenReason {
  Spam
  Rugpull
  Honeypot
  Worthless
  Arbitrary
}

enum HiddenTokenMethod {
  Manual
  GoPlus
  SpamDetection
}

type ChatChannel implements Node {
  id: ID!
  network: Network!
  name: String!
  description: String!
  createdAt: Timestamp!
  imageUrl: String!
  totalShares: Int!
  valuePerShare: String!
  channelFeePerShare: String!
  protocolFeePerShare: String!
}

type ChatChannelEdge {
  node: ChatChannel!
  cursor: String!
}

type ChatChannelMember implements Node {
  id: ID!
  address: String!
  shares: Int!
}

type ChatChannelMemberEdge {
  node: ChatChannelMember!
  cursor: String!
}

type FarcasterXAccount {
  username: String!
  url: String!
}

type FarcasterMetadata {
  id: ID!
  displayName: String
  description: String
  warpcast: String
  farcasterUrl: String
  xAccount: FarcasterXAccount
  imageUrl: String
}

type FarcasterProfile implements Node {
  id: ID!
  username: String!
  custodyAddress: String!
  fid: Int!
  connectedAddresses: [String!]!
  neynarScore: Float!
  metadata: FarcasterMetadata!
  connectedAccounts: [Account!]!
  followStats: FarcasterFollowerStats
  followers(first: Int, after: String): FarcasterFollowerConnection!
  following(first: Int, after: String): FarcasterFollowerConnection!
}

type FarcasterFollowerStats {
  followerCount: Int!
  followingCount: Int!
}

type FarcasterProfileEdge {
  node: FarcasterProfile!
  cursor: String!
}

type FarcasterFollowerConnection {
  edges: [FarcasterProfileEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type FarcasterReaction implements Node {
  id: ID!
  fid: Int!
  target: String!
  targetType: String!
  reactionType: FarcasterReactionType!
  timestamp: Timestamp!
  replyCast: NeynarCastV2
  profile: FarcasterProfile
}

enum FarcasterReactionType {
  Like
  Recast
  Quote
  Reply
}

type FarcasterReactionEdge {
  node: FarcasterReaction!
  cursor: String!
}

type ActivityAccountDelta implements Node {
  id: ID!
  tokenDeltasCount: Int!
  nftDeltasCount: Int!
  account: Account
  tokenDeltasV2(first: Int = 5, after: String): FungibleTokenDeltaConnection!
  nftDeltasV2(first: Int = 5, after: String): NftDeltaConnection!
}

type ActivityAccountDeltaEdge {
  node: ActivityAccountDelta!
  cursor: String!
}

type ActivityAccountDeltaConnection {
  edges: [ActivityAccountDeltaEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type FungibleTokenDelta implements Node {
  id: ID!
  address: String!
  amountRaw: BigDecimal!
  attachment: TokenDisplayItem!
  token: FungibleToken
  appToken: AppFungibleToken
  amount: Float
  historicalPrice(currency: Currency = USD): OnchainHistoricalPrice
}

type FungibleTokenDeltaEdge {
  node: FungibleTokenDelta!
  cursor: String!
}

type FungibleTokenDeltaConnection {
  edges: [FungibleTokenDeltaEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type NftDelta implements Node {
  id: ID!
  collectionAddress: String!
  tokenId: String!
  amount: Float!
  amountRaw: BigDecimal!
  attachment: NFTDisplayItem!
  nft: NftToken
}

type NftDeltaEdge {
  node: NftDelta!
  cursor: String!
}

type NftDeltaConnection {
  edges: [NftDeltaEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type ActivityEventDelta {
  transactionHash: String!
  network: Network!
  subject: String!
  transactionBlockTimestamp: Timestamp!
  nftCount: Int!
  fungibleCount: Int!
}

type ActivityTimelineEventDelta implements Node {
  id: ID!
  transactionHash: String!
  network: Network!
  subject: String!
  transactionBlockTimestamp: Timestamp!
  nftCount: Int!
  fungibleCount: Int!
  perspectiveAccount: Account!
  from: Account!
  to: Account
  fungibleDeltas: [FungibleTokenDelta!]!
  originatedFromTransaction: OnChainTransaction!
  nftDeltas: [NftDelta!]!
  networkObject: NetworkObject
}

type ActivityEventDeltaEdge {
  node: ActivityEventDelta!
  cursor: String!
}

type PositionBreakdownDisplayProps {
  label: String!
  secondaryLabel: AbstractDisplayItem
  tertiaryLabel: AbstractDisplayItem
  images: [String!]!
  balanceDisplayMode: BalanceDisplayMode!
  stats: [DisplayItemWrapper!]!
  info: [DisplayItemWrapper!]!
}

type PositionBreakdown implements AbstractBreakdown {
  appId: String
  metaType: MetaTypeV3
  address: Address!
  network: Network!
  balanceUSD: Float!
  type: BreakdownType!
  breakdown: [AbstractBreakdown!]!
  displayProps: TokenBreakdownDisplayProps!
}

type TokenBreakdownDisplayProps {
  label: String!
  secondaryLabel: AbstractDisplayItem
  tertiaryLabel: AbstractDisplayItem
  balanceDisplayMode: BalanceDisplayMode!
  images: [String!]!
  stats: [DisplayItemWrapper!]!
  info: [DisplayItemWrapper!]!
}

type TokenBreakdownContext {
  balance: Float!
  balanceRaw: String!
  price: Float!
  name: String
  symbol: String!
  decimals: Float!
  verified: Boolean
}

type TokenBreakdown implements AbstractBreakdown {
  appId: String
  metaType: MetaTypeV3
  address: Address!
  network: Network!
  balanceUSD: Float!
  type: BreakdownType!
  breakdown: [AbstractBreakdown!]!
  context: TokenBreakdownContext!
  displayProps: TokenBreakdownDisplayProps!
}

type NonFungibleTokenBreakdownDisplayProps {
  label: String!
  secondaryLabel: AbstractDisplayItem
  tertiaryLabel: AbstractDisplayItem
  balanceDisplayMode: BalanceDisplayMode!
  images: [String!]!
  stats: [DisplayItemWrapper!]!
  info: [DisplayItemWrapper!]!
  profileImage: String!
  profileBanner: String!
  featuredImage: String
}

type NonFungibleTokenBreakdownContext {
  incomplete: Boolean!
  openseaId: String!
  floorPrice: Float!
  holdersCount: Float!
  amountHeld: Float!
}

type NonFungibleTokenBreakdownAsset {
  tokenId: String!
  balance: Float!
  assetImg: String!
  balanceUSD: Float!
  assetName: String!
}

type NonFungibleTokenBreakdown implements AbstractBreakdown {
  appId: String
  metaType: MetaTypeV3
  address: Address!
  network: Network!
  balanceUSD: Float!
  type: BreakdownType!
  breakdown: [AbstractBreakdown!]!
  context: NonFungibleTokenBreakdownContext!
  assets: [NonFungibleTokenBreakdownAsset!]!
  displayProps: NonFungibleTokenBreakdownDisplayProps!
}

type AppContractPosition {
  key: String!
  address: String!
  appId: String!
  appName: String!
  groupId: String!
  type: ContractType!
  label: String!
  liquidity: Float
  groupLabel: String! @deprecated(reason: "prefer using label")
  network: Network!
  displayProps: PositionBreakdownDisplayProps!
  tokens: [AbstractPosition!]!
  baseTokensSymbols: [String!]!
  baseTokens: [BaseTokenPosition!]!
}

type AppTokenPosition implements AbstractPosition {
  appId: String! @deprecated(reason: "use app.slug instead")
  type: ContractType!
  network: Network!
  appName: String! @deprecated(reason: "use app.name instead")
  decimals: Int!
  metaType: String
  groupId: String!
  label: String
  liquidity: Float
  groupLabel: String @deprecated(reason: "prefer using label")
  price: Float!
  pricePerShare: [Float!]!
  supply: String!
  symbol: String!
  address: String!
  name: String
  tokens: [AbstractPosition!]!
  displayProps: PositionBreakdownDisplayProps!
  baseTokensSymbols: [String!]!
  baseTokens: [BaseTokenPosition!]!
}

type AppTokenPositionEdge {
  node: AppTokenPosition!
  cursor: String!
}

type NonFungibleTokenPosition implements AbstractPosition {
  appId: String! @deprecated(reason: "no app for non-fungible tokens")
  type: ContractType!
  network: Network!
  appName: String! @deprecated(reason: "no app for non-fungible tokens")
  address: String!
  symbol: String!
  decimals: Int!
  price: Float!
  assets: [NftAsset!]
  displayProps: NonFungibleTokenBreakdownDisplayProps!
}

type BaseTokenPosition implements AbstractPosition {
  appId: String!
  type: ContractType!
  network: Network!
  metaType: String
  address: String!
  symbol: String!
  price: Float!
  decimals: Int!
  status: String
  hide: Boolean
  canExchange: Boolean
}

type AppPosition {
  appPosition: Position!
}

union Position = AppTokenPosition | AppContractPosition

type AppPositionEdge {
  node: AppPosition!
  cursor: String!
}

type AppPositionConnection {
  edges: [AppPositionEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type AppPositionGroup {
  label: String!
  groupLabel: String! @deprecated(reason: "prefer using label")
  appTokenPositions: [AppTokenPosition!]! @deprecated(reason: "prefer using investments")
  contractPositions: [AppContractPosition!]! @deprecated(reason: "prefer using investments")
  positions: AppPositionConnection!
  baseTokenSymbols: [String!]!
  baseTokens: [BaseTokenPosition!]!
}

type AppListView implements AbstractAppView {
  label: String!
  type: AppViewType!
  positionType: String
  positions: AppPositionGroup!
  totalPositions: Float!
  groupIds: [String!]
}

type AppDropdownView implements AbstractAppView {
  label: String!
  type: AppViewType!
  positionType: String
  options: [AbstractAppView!]!
  groupIds: [String!]
}

type AppSplitView implements AbstractAppView {
  label: String!
  type: AppViewType!
  positionType: String
  views: [AbstractAppView!]!
  groupIds: [String!]
}

type AppTvl {
  """
  Associated network of the app
  """
  network: Network!

  """
  Total value locked of an app for a given network
  """
  tvl: Float!
}

type AppCategoryObject {
  id: ID!
  name: String!
  slug: String!
  description: String!
  trendable: Boolean!
  createdAt: Timestamp!
  updatedAt: Timestamp!
}

type AppLinks {
  """
  Discord channel link
  """
  discord: String

  """
  GitHub organization link
  """
  github: String

  """
  Medium blog link
  """
  medium: String

  """
  Telegram channel link
  """
  telegram: String

  """
  Twitter profile link
  """
  twitter: String
}

type AppGroupDefinition {
  id: String!
  label: String!
  groupLabel: String @deprecated(reason: "should no longer be used")
  isHiddenFromExplore: Boolean
  type: String!
}

type App implements Node {
  id: ID!

  """
  Unique application ID
  """
  databaseId: Int!

  """
  Unique application slug
  """
  slug: String!

  """
  Current status of the application
  """
  status: AppStatus!

  """
  Group in which this application belongs to
  """
  groups: [String!]! @deprecated(reason: "Prefer using groupDefinition")

  """
  Group in which this application belongs to
  """
  groupDefinitions: [AppGroupDefinition!]!

  """
  The typical display name of the application
  """
  displayName: String!

  """
  Application website
  """
  url: String

  """
  Application links
  """
  links: AppLinks
  websiteUrl: String @deprecated(reason: "Renamed to url")

  """
  Description of the application.
  """
  description: String!
  label: String
  imgUrl: String!
  tags: [ApplicationTag!]!
  positions: [AppPositionGroup!]!
  tvl: [AppTvl!]!
  tokenAddress: String
  tokenNetwork: Network
  token: BaseTokenPosition
  categoryId: Int
  category: AppCategoryObject
  twitterUrl: String
  farcasterUrl: String
  farcasterMiniAppDomain: String
  createdAt: Timestamp!
  appPositionsV2(chainId: Int!, groupId: String!, first: Float = 25, after: String): AppPositionConnection!
  appPositions(network: Network!, groupId: String!, first: Float = 25, after: String): AppPositionConnection!
    @deprecated(reason: "Use appPositionsV2 instead.")
}

enum AppStatus {
  ARCHIVED
  ENABLED
  DISABLED
  PENDING
  REJECTED
}

enum ApplicationTag {
  ALGORITHMIC_STABLECOIN
  ASSET_MANAGEMENT
  BONDS
  BRIDGE
  COLLATERALIZED_DEBT_POSITION
  CROSS_CHAIN
  DECENTRALIZED_EXCHANGE
  DERIVATIVES
  ELASTIC_FINANCE
  FARMING
  FUND_MANAGER
  GAMING
  INFRASTRUCTURE
  INSURANCE
  LAUNCHPAD
  LENDING
  LIQUIDITY_POOL
  LIQUID_STAKING
  LOTTERY
  MARGIN_TRADING
  NFT_LENDING
  NFT_MARKETPLACE
  OPTIONS
  PAYMENTS
  PERPETUALS_EXCHANGE
  PREDICTION_MARKET
  PRIVACY
  REAL_ESTATE
  RESERVE_CURRENCY
  STABLECOIN
  STAKING
  SYNTHETICS
  TOKENIZED_RISK
  YIELD_AGGREGATOR
  LIMIT_ORDER
}

type AppEdge {
  node: App!
  cursor: String!
}

type AppConnection {
  edges: [AppEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type FiniliarPortfolioSnapshot {
  totalUsd: Float!
  timestamp: Timestamp!
}

type FiniliarPortfolioChange {
  changePercentage: Float!
  oldestSnapshot: FiniliarPortfolioSnapshot!
  latestSnapshot: FiniliarPortfolioSnapshot!
}

type OnchainMarketDataLatestFarcasterSwap implements Node {
  id: ID!
  transactionHash: String!
  timestamp: Timestamp!
  soldAmount: Float! @deprecated(reason: "Use amount instead")
  soldTokenAddress: Float! @deprecated(reason: "Use token instead")
  boughtAmount: Float! @deprecated(reason: "Use amount instead")
  boughtTokenAddress: Address! @deprecated(reason: "Use token instead")
  tokenAddress: Address!
  volumeUsd: Float!
  amount: Float!
  isBuy: Boolean!
  profile: FarcasterProfile
  token: FungibleToken
  network: NetworkObject!
  channelFeedSwap: ChannelFeedSwap
}

type OnchainMarketDataLatestFarcasterSwapEdge {
  node: OnchainMarketDataLatestFarcasterSwap!
  cursor: String!
}

type OnchainMarketDataLatestFarcasterSwapConnection {
  edges: [OnchainMarketDataLatestFarcasterSwapEdge!]!
  pageInfo: PageInfo!
}

type OnchainMarketDataLatestSwap implements Node {
  id: ID!
  transactionHash: String!
  timestamp: Timestamp!
  soldAmount: Float!
  soldTokenAddress: Address!
  boughtAmount: Float!
  boughtTokenAddress: Address!
  gasTokenVolume: Float!
  volumeUsd: Float!
  from: Account!
  boughtToken: FungibleToken
  soldToken: FungibleToken
  network: NetworkObject!
}

type OnchainMarketDataLatestSwapEdge {
  node: OnchainMarketDataLatestSwap!
  cursor: String!
}

type OnchainMarketDataLatestSwapConnection {
  edges: [OnchainMarketDataLatestSwapEdge!]!
  pageInfo: PageInfo!
}

type OnchainHistoricalPrice {
  timestamp: Timestamp!
  price: Float!
}

type NetworkExchangeConfigurationObject {
  enabled: Boolean!
  suggestedTokenAddresses: [String!]!
  feeBasisPoints: Float!

  """
  Fee percentage eg. value of 0.5 -> 0.5% fee taken from total amount
  """
  feePercentage: Float!
  feeRecipientAddress: String
  exchangeProviderStrategy: String!
  exchangeProviderUrl: String!
}

type NetworkObject {
  id: Int!
  name: String!
  slug: String!
  enumValue: Network! @deprecated(reason: "Use network ID instead")
  enabled: Boolean!
  evmCompatible: Boolean @deprecated(reason: "Use vm instead")
  vm: VirtualMachineType!
  chainId: Int
  hasLiveFeedEtl: Boolean!
  holdingsEnabled: Boolean!
  nftBalancesEnabled: Boolean!
  holdingsComparisonJobEnabled: Boolean!
  thirdPartyBaseTokensEnabled: Boolean!
  onchainPricesEnabled: Boolean!
  activityFeedEnabled: Boolean!
  trendsEnabled: Boolean!
  pushNotificationEnabled: Boolean!
  farcasterZappyBotEnabled: Boolean!
  pnlEnabled: Boolean!
  multicallContractAddress: String
  wrappedGasTokenAddress: String
  blocksPerDayEstimate: Int
  blockScannerType: String
  blockScannerBaseUrl: String
  publicRpcUrl: String
  enabledAt: Timestamp
  exchangeConfiguration: NetworkExchangeConfigurationObject
  lastProcessedBlock(processingFlow: BlockProcessingFlow!): Int
}

enum VirtualMachineType {
  EVM
  SVM
  BITCOIN
}

enum BlockProcessingFlow {
  NFT
  TIMELINE
}

type PortfolioV2AppBalanceByAccountAppGroupBalance {
  """
  ID
  """
  id: ID!

  """
  App ID
  """
  appId: ID!

  """
  Network ID
  """
  networkId: ID!

  """
  Group label
  """
  groupLabel: ID!

  """
  Balance in USD for this grouping
  """
  balanceUSD: Float!
  app: App!
  network: NetworkObject!
  positionBalances(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAccountAppGroupPositionBalanceFiltersInput
  ): PortfolioV2AppBalanceByAccountAppGroupPositionBalanceConnection!
  metadata: [MetadataItemWithLabel!]!
}

input PortfolioV2AppBalanceByAccountAppGroupPositionBalanceFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  search: String
  appSlugs: [String!]
}

type PortfolioV2AppBalanceByAccountAppGroupBalanceEdge {
  node: PortfolioV2AppBalanceByAccountAppGroupBalance!
  cursor: String!
}

type PortfolioV2AppBalanceByAccountAppGroupBalanceConnection {
  edges: [PortfolioV2AppBalanceByAccountAppGroupBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByApp {
  """
  ID
  """
  id: ID!

  """
  App ID
  """
  appId: ID!

  """
  Network ID
  """
  networkId: ID!

  """
  Balance of the app in USD
  """
  balanceUSD: Float!

  """
  Count of positions for this app/network
  """
  positionCount: Int!
  app: App!
  network: NetworkObject!
  accountBalances(first: Int = 5): PortfolioV2AppBalanceByAppAccountBalanceConnection!
  balances(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAppBalanceFiltersInput
  ): PortfolioV2AppBalanceByAppPositionBalanceConnection! @deprecated(reason: "Use positionBalances instead")
  positionBalances(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAppBalanceFiltersInput
  ): PortfolioV2AppBalanceByAppPositionBalanceConnection!
}

input PortfolioV2AppBalanceByAppBalanceFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  symbolLike: String
  search: String
}

type PortfolioV2AppBalanceByAppEdge {
  node: PortfolioV2AppBalanceByApp!
  cursor: String!
}

type PortfolioV2AppBalanceByAppConnection {
  edges: [PortfolioV2AppBalanceByAppEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalancesByAccount {
  id: ID!
  accountAddress: Address!
  account: Account!
  balanceUSD: Float!
  smartAccount: ProxyAccount
  appGroupBalances(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAccountAppGroupBalanceFiltersInput
  ): PortfolioV2AppBalanceByAccountAppGroupBalanceConnection!
}

input PortfolioV2AppBalanceByAccountAppGroupBalanceFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  search: String
  appSlugs: [String!]
}

type PortfolioV2AppBalancesByAccountEdge {
  node: PortfolioV2AppBalancesByAccount!
  cursor: String!
}

type PortfolioV2AppBalancesByAccountConnection {
  edges: [PortfolioV2AppBalancesByAccountEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByAppGroup {
  """
  ID
  """
  id: ID!

  """
  App ID
  """
  appId: ID!

  """
  Network ID
  """
  networkId: ID!

  """
  Group label
  """
  groupLabel: ID!

  """
  Balance of the app in USD
  """
  balanceUSD: Float!

  """
  Count of positions for this app/network
  """
  positionCount: Int!
  app: App!
  network: NetworkObject!
  positionBalances(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAppGroupBalanceFiltersInput
  ): PortfolioV2AppBalanceByAppGroupPositionBalanceConnection!
}

input PortfolioV2AppBalanceByAppGroupBalanceFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  search: String
}

type PortfolioV2AppBalanceByAppGroupEdge {
  node: PortfolioV2AppBalanceByAppGroup!
  cursor: String!
}

type PortfolioV2AppBalanceByAppGroupConnection {
  edges: [PortfolioV2AppBalanceByAppGroupEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByAppAccountBalance {
  id: ID!

  """
  Address of the account
  """
  accountAddress: Address!

  """
  Balance of the account in USD
  """
  balanceUSD: Float!

  """
  Count of positions for this account
  """
  positionCount: Int!
}

type PortfolioV2AppBalanceByAppAccountBalanceEdge {
  node: PortfolioV2AppBalanceByAppAccountBalance!
  cursor: String!
}

type PortfolioV2AppBalanceByAppAccountBalanceConnection {
  edges: [PortfolioV2AppBalanceByAppAccountBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByMetaType {
  id: ID!
  metaType: MetaTypeV3!
  positionCount: Int!
  balanceUSD: Float!
  networkBalances(first: Int = 5): PortfolioV2AppBalanceByMetaTypeNetworkBalanceConnection!
}

type PortfolioV2AppBalanceByMetaTypeEdge {
  node: PortfolioV2AppBalanceByMetaType!
  cursor: String!
}

type PortfolioV2AppBalanceByMetaTypeConnection {
  edges: [PortfolioV2AppBalanceByMetaTypeEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByMetaTypeNetworkBalance {
  id: ID!

  """
  Network ID
  """
  networkId: ID!

  """
  Balance of the network in USD
  """
  balanceUSD: Float!
  network: NetworkObject!
}

type PortfolioV2AppBalanceByMetaTypeNetworkBalanceEdge {
  node: PortfolioV2AppBalanceByMetaTypeNetworkBalance!
  cursor: String!
}

type PortfolioV2AppBalanceByMetaTypeNetworkBalanceConnection {
  edges: [PortfolioV2AppBalanceByMetaTypeNetworkBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByNetwork {
  id: ID!
  networkId: ID!
  network: NetworkObject!
  balanceUSD: Float!
}

type PortfolioV2AppBalanceByNetworkEdge {
  node: PortfolioV2AppBalanceByNetwork!
  cursor: String!
}

type PortfolioV2AppBalanceByNetworkConnection {
  edges: [PortfolioV2AppBalanceByNetworkEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByToken {
  id: ID!
  tokenAddress: String!
  networkId: ID!
  network: NetworkObject!
  balanceUSD: Float!
  token: FungibleToken
  isFavorite: Boolean!
}

type PortfolioV2AppBalanceByTokenEdge {
  node: PortfolioV2AppBalanceByToken!
  cursor: String!
}

type PortfolioV2AppBalanceByTokenConnection {
  edges: [PortfolioV2AppBalanceByTokenEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2NftBalanceByCollection {
  id: ID!
  collectionId: ID!
  balance: String!
  balanceDistinct: String!
  balanceUSD: Float!
  collection: NftCollection!
  tokens(
    first: Int = 25
    after: String
    order: PortfolioV2NftBalanceByTokenInputInput
  ): PortfolioV2NftBalanceByTokenConnection!
}

input PortfolioV2NftBalanceByTokenInputInput {
  by: PortfolioV2NftOrderByOption!
  direction: OrderDirectionOption
}

enum PortfolioV2NftOrderByOption {
  USD_WORTH
  LAST_RECEIVED
}

type PortfolioV2NftBalanceByCollectionEdge {
  node: PortfolioV2NftBalanceByCollection!
  cursor: String!
}

type PortfolioV2NftBalanceByCollectionConnection {
  edges: [PortfolioV2NftBalanceByCollectionEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2NftBalanceByNetwork {
  id: ID!
  networkId: ID!
  balance: String!
  balanceUSD: Float!
  network: NetworkObject!
}

type PortfolioV2NftBalanceByNetworkEdge {
  node: PortfolioV2NftBalanceByNetwork!
  cursor: String!
}

type PortfolioV2NftBalanceByNetworkConnection {
  edges: [PortfolioV2NftBalanceByNetworkEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2NftBalanceByToken {
  id: ID!
  tokenId: ID!
  balance: String!
  balanceUSD: Float!
  valuationStrategy: NftValuationStrategy!
  lastReceived: Timestamp!
  token: NftToken!
}

enum NftValuationStrategy {
  TOP_OFFER
  ESTIMATED_VALUE
  OVERRIDE
}

type PortfolioV2NftBalanceByTokenEdge {
  node: PortfolioV2NftBalanceByToken!
  cursor: String!
}

type PortfolioV2NftBalanceByTokenConnection {
  edges: [PortfolioV2NftBalanceByTokenEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2TokenBalancesByAccountTokenBalance {
  id: ID!
  tokenAddress: Address!
  network: Network!
  name: String!
  symbol: String!
  decimals: Float!
  imgUrl: String!
  verified: Boolean!
  price: Float!
  balance: Float!
  balanceUSD: Float!
  balanceRaw: String!
}

type PortfolioV2TokenBalancesByAccountTokenBalanceEdge {
  node: PortfolioV2TokenBalancesByAccountTokenBalance!
  cursor: String!
}

type PortfolioV2TokenBalancesByAccount {
  id: ID!
  accountAddress: Address!
  account: Account!
  balanceUSD: Float!
  smartAccount: ProxyAccount
  tokenBalances(first: Int = 5): PortfolioV2TokenBalanceByAccountTokenBalanceConnection!
}

type PortfolioV2TokenBalancesByAccountEdge {
  node: PortfolioV2TokenBalancesByAccount!
  cursor: String!
}

type PortfolioV2TokenBalancesByAccountConnection {
  edges: [PortfolioV2TokenBalancesByAccountEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2TokenBalanceByAccountTokenBalance {
  id: ID!
  tokenAddress: String!
  networkId: ID!
  name: String!
  symbol: String!
  decimals: Float!
  verified: Boolean!
  price: Float!
  balance: Float!
  balanceUSD: Float!
  balanceRaw: String!
  network: NetworkObject!
  isFavorite: Boolean!
}

type PortfolioV2TokenBalanceByAccountTokenBalanceEdge {
  node: PortfolioV2TokenBalanceByAccountTokenBalance!
  cursor: String!
}

type PortfolioV2TokenBalanceByAccountTokenBalanceConnection {
  edges: [PortfolioV2TokenBalanceByAccountTokenBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2TokenBalancesByNetwork {
  id: ID!
  networkId: ID!
  networkSlug: Network! @deprecated(reason: "Use network.slug instead")
  balanceUSD: Float!
  network: NetworkObject!
}

type PortfolioV2TokenBalancesByNetworkEdge {
  node: PortfolioV2TokenBalancesByNetwork!
  cursor: String!
}

type PortfolioV2TokenBalancesByNetworkConnection {
  edges: [PortfolioV2TokenBalancesByNetworkEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2TokenBalanceByTokenAccountBalance {
  id: ID!
  accountAddress: Address!
  balance: Float!
  balanceUSD: Float!
  balanceRaw: String!
  account: Account!
  smartAccount: ProxyAccount
}

type PortfolioV2TokenBalanceByTokenAccountBalanceEdge {
  node: PortfolioV2TokenBalanceByTokenAccountBalance!
  cursor: String!
}

type PortfolioV2TokenBalanceByTokenAccountBalanceConnection {
  edges: [PortfolioV2TokenBalanceByTokenAccountBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2TokenBalanceByToken {
  id: ID!
  tokenAddress: String!
  networkId: ID!
  name: String!
  symbol: String!
  decimals: Float!
  verified: Boolean!
  price: Float!
  priceSource: Erc20TokenPriceSource!
  balance: Float!
  balanceUSD: Float!
  balanceRaw: String!
  network: NetworkObject!

  """
  The URL of the token image
  """
  imgUrl: String! @deprecated(reason: "Use imgUrlV2 instead, which will return null if the image is not found")

  """
  The URL of the token image, or null if the image is not found
  """
  imgUrlV2: String
  onchainMarketData: OnchainMarketData
  accountBalances(first: Int = 5): PortfolioV2TokenBalanceByTokenAccountBalanceConnection!
  isFavorite: Boolean!
}

type PortfolioV2TokenBalanceByTokenEdge {
  node: PortfolioV2TokenBalanceByToken!
  cursor: String!
}

type PortfolioV2TokenBalanceByTokenConnection {
  edges: [PortfolioV2TokenBalanceByTokenEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type ProxyAccount {
  ownerAddress: Address!
  address: Address!
  networkId: ID!
  network: Network!
  appId: String @deprecated(reason: "Use `app.slug` field instead")
  app: App
  owner: Account!
  networkV2: NetworkObject!
}

type WalletTokenBalanceToken {
  id: ID!
  address: String!
  network: Network!
  label: String
  imgUrl: String!
  name: String!
  decimals: Float!
  symbol: String!
  verified: Boolean!
  price: Float!
}

type BaseTokenBalance {
  baseToken: WalletTokenBalanceToken!
  balance: Float!
  balanceUSD: Float!
  balanceRaw: String!
}

type TokenBalance {
  key: String!
  address: String!
  network: Network!
  token: BaseTokenBalance!
  proxy: ProxyAccount @deprecated(reason: "Use `proxies` on the `Portfolio` object instead")
  updatedAt: Timestamp!
}

type AddressMetadataObject implements Node {
  id: ID!
  address: Address!
  network: String
  relatedEntityTypes: [OnchainEntityType!]!
  label: String!
  labelSource: String!
  updatedAt: Timestamp!
  createdAt: Timestamp!
}

enum OnchainEntityType {
  TOKEN
  DAO
  NFT_COLLECTION
}

type AddressMetadataEdge {
  node: AddressMetadataObject!
  cursor: String!
}

type ParamType {
  type: String!
  name: String
  indexed: Boolean
  components: [ParamType!]
}

type Contract {
  address: Address!
  network: Network!
  app: App
}

type LensMetadata {
  name: String
  handleNamespace: String
  fullHandle: String
  description: String
  hey: String
  twitter: String
  website: String
  imageUrl: String
  coverImageUrl: String
}

type LensProfile {
  handle: String!
  metadata: LensMetadata!
}

type FarcasterMiniAppJsonAccountAssociation {
  header: String!
  payload: String!
  signature: String!
}

type FarcasterMiniAppJsonFrame {
  version: String!
  name: String!
  iconUrl: String!
  homeUrl: String!
  imageUrl: String
  buttonTitle: String
  splashImageUrl: String
  splashBackgroundColor: String
  webhookUrl: String
  subtitle: String
  description: String
  screenshotUrls: [String!]
  primaryCategory: String
  tags: [String!]
  heroImageUrl: String
  tagline: String
  ogTitle: String
  ogDescription: String
  ogImageUrl: String
  noIndex: Boolean
}

type TimelineV2EntryEdge {
  node: TimelineV2Entry!
  cursor: String!
}

union TimelineV2Entry = TimelineEventV2Entries | ActivityAccountDeltaEntries

type TimelineEventV2Entries implements Node {
  id: ID!
  entries: [TimelineEventV2!]!
}

type ActivityAccountDeltaEntries implements Node {
  id: ID!
  entries: [ActivityTimelineEventDelta!]!
}

type TransactionHistoryV2EntryEdge {
  node: TransactionHistoryV2Entry!
  cursor: String!
}

union TransactionHistoryV2Entry = TimelineEventV2 | ActivityTimelineEventDelta

type TransactionHistoryV2EntryConnection {
  edges: [TransactionHistoryV2EntryEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type FarcasterTopHat implements Node {
  id: ID!
  uri: String!
}

type HistoricalPortfolioTick {
  timestamp: Timestamp!
  value: Float!
}

type NftUserTokenEdge {
  node: NftToken!
  cursor: String!
  balance: Int! @deprecated(reason: "Use `balanceRaw` instead")
  balanceRaw: String!
  balanceUSD: Float!
  valuationStrategy: NftValuationStrategy!
  lastReceived: DateTime
  ownedAt: DateTime
  token: NftToken! @deprecated(reason: "Use `node`")
  balances: [NftUserTokenBalance!]!
}

"""
A date-time string at UTC, such as 2019-12-03T09:54:33Z, compliant with the date-time format.
"""
scalar DateTime

type NftUserTokenConnection {
  edges: [NftUserTokenEdge!]!
  pageInfo: PageInfo!
}

type NftPayment {
  tokenAddress: Address! @deprecated(reason: "Use `token`")
  tokenSymbol: String @deprecated(reason: "Use `token`")
  tokenValue: BigDecimal!
  tokenValueETH: BigDecimal!
  tokenValueUSD: BigDecimal!
}

type NftTransfer implements Node {
  id: ID!
  timestamp: Int!
  txHash: String!
  network: Network!
  payments: [NftPayment!]!
}

type NftTransferEdge {
  node: NftTransfer!
  cursor: String!
  heldForInSeconds: Int
}

type NftTransferConnection {
  edges: [NftTransferEdge!]!
  pageInfo: PageInfo!
}

type CollectionEventSale implements CollectionEvent & Node {
  id: ID!
  timestamp: Int!
  txHash: String!
  intention: String
  event: CollectionEventOld! @deprecated(reason: "Use `CollectionEvent` instead")
  token: NftToken!
  fromAccount: Account!
  toAccount: Account!
  payments: [NftPayment!]!
}

type CollectionEventTransfer implements CollectionEvent & Node {
  id: ID!
  timestamp: Int!
  txHash: String!
  intention: String
  event: CollectionEventOld! @deprecated(reason: "Use `CollectionEvent` instead")
  token: NftToken!
  fromAccount: Account!
  toAccount: Account!
}

type CollectionEventEdge {
  node: CollectionEvent!
  cursor: String!
}

type CollectionEventConnection {
  edges: [CollectionEventEdge!]!
  pageInfo: PageInfo!
}

type NftCollectionStats {
  hourlyVolumeEth: BigDecimal!
  hourlyVolumeEthPercentChange: Float
  dailyVolumeEth: BigDecimal!
  dailyVolumeEthPercentChange: Float
  weeklyVolumeEth: BigDecimal!
  weeklyVolumeEthPercentChange: Float
  monthlyVolumeEth: BigDecimal!
  monthlyVolumeEthPercentChange: Float
  totalVolumeEth: BigDecimal!
  hourlyVolume: NftValueDenomination!
  dailyVolume: NftValueDenomination!
  weeklyVolume: NftValueDenomination!
  monthlyVolume: NftValueDenomination!
  totalVolume: NftValueDenomination!
}

type NftCollectionTraitGroupString implements Node & NftCollectionTraitGroupBase {
  id: ID!
  name: String!
  display: NftTraitDisplayType!
}

type NftCollectionTraitGroupNumericRange implements Node & NftCollectionTraitGroupBase {
  id: ID!
  name: String!
  display: NftTraitDisplayType!
  min: Float!
  max: Float!
}

type NftCollectionTraitValue implements Node {
  id: ID!
  value: String!
  estimatedValueEth: BigDecimal
  supply: BigDecimal!
  supplyPercentage: Float!
}

type NftCollectionTraitValueEdge {
  node: NftCollectionTraitValue!
  cursor: String!
}

type NftCollectionTraitValueConnection {
  edges: [NftCollectionTraitValueEdge!]!
  pageInfo: PageInfo!
}

type TransactionConfig {
  data: String!
  to: Address!
  from: Address!
}

type NftContract {
  address: Address!
  network: Network!
}

type NftCollectionGroup implements Node {
  id: ID!
  key: String!
  name: String!
  description: String!
  socialLinks: [SocialLink!]!

  """
  Image of the collection group as a square
  """
  logoImageUrl: String

  """
  Image of the collection group as an horizontal rectangle
  """
  bannerImageUrl: String

  """
  Image of the collection group as a vertical rectangle
  """
  cardImageUrl: String
  disabled: Boolean!
  isCurated: Boolean!
  relatedContracts: [NftContract!]
  relatedCollectionType: NftCollectionType
}

type NftCollectionHolder implements Node {
  id: ID!

  """
  Number of unique items
  """
  holdCount: BigDecimal!

  """
  Total number of items - for ERC-1155
  """
  holdTotalCount: BigDecimal!
  account: Account!
}

type NftCollectionHolderEdge {
  node: NftCollectionHolder!
  cursor: String!
}

type PaginatedNftHolder {
  edges: [NftCollectionHolderEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type NftEventTokenPayment {
  from: Address!
  to: Address!
  tokenAmountRaw: String!
  historicPriceUsd: Float
  gasAmountRaw: Float
  token: FungibleToken
}

type NftEvent implements Node {
  id: ID!
  network: Network!
  eventType: String!
  from: Address!
  to: Address!
  quantity: String!
  block: Int!
  timestamp: Int!
  txHash: String!
  logIndex: Int!
  key: Int!
  transaction: OnChainTransaction
  lightTransaction: OnChainTransaction
  payment: NftEventTokenPayment
  nft: NftToken!
}

type NftEventEdge {
  node: NftEvent!
  cursor: String!
}

type NftEventConnection {
  edges: [NftEventEdge!]!
  pageInfo: PageInfo!
}

type NftHolder implements Node {
  id: ID!

  """
  Number of unique items, not counting ERC-1155 copies
  """
  holdCount: BigDecimal!

  """
  Total number of items including ERC-1155 copies
  """
  holdTotalCount: BigDecimal!
  account: Account!
}

type NftHolderEdge {
  node: NftHolder!
  cursor: String!
}

type NftHolderConnection {
  edges: [NftHolderEdge!]!
  totalCount: Int!
  pageInfo: PageInfo!
}

type NftTrait implements Node {
  id: ID!
  attributeName: String!
  attributeValue: String!
  estimatedValueEth: BigDecimal @deprecated(reason: "Use estimatedValue instead")
  supply: BigDecimal!
  supplyPercentage: Float!
}

type NftMetadata {
  uri: String
  data: String
}

type NftUserTokenBalance {
  balance: BigDecimal!
  valuationStrategy: NftValuationStrategy!
  user: User! @deprecated(reason: "Use `account` instead to take advantage of the `Account` type")
  account: Account!
}

type AnyPositionBalanceEdge {
  node: AnyPositionBalance!
  cursor: String!
}

union AnyPositionBalance = AppTokenPositionBalance | ContractPositionBalance

type PortfolioV2AppBalanceByAppPositionBalanceConnection {
  edges: [AnyPositionBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByAccountAppGroupPositionBalanceConnection {
  edges: [AnyPositionBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalanceByAppGroupPositionBalanceConnection {
  edges: [AnyPositionBalanceEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PortfolioV2AppBalance {
  byAccount(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAccountFiltersInput
  ): PortfolioV2AppBalancesByAccountConnection!
  byApp(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAppFiltersInput
  ): PortfolioV2AppBalanceByAppConnection!
  byAppGroup(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByAppGroupFiltersInput
  ): PortfolioV2AppBalanceByAppGroupConnection!
  byMetaType(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByMetaTypeFiltersInput
  ): PortfolioV2AppBalanceByMetaTypeConnection!
  byNetwork(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByNetworkFiltersInput
  ): PortfolioV2AppBalanceByNetworkConnection!
  byToken(
    first: Int = 25
    after: String
    filters: PortfolioV2AppBalanceByTokenFiltersInput
  ): PortfolioV2AppBalanceByTokenConnection!
  totalBalanceUSD: Float!
}

input PortfolioV2AppBalanceByAccountFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  search: String
  appSlugs: [String!]
}

input PortfolioV2AppBalanceByAppFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  symbolLike: String
  search: String
  appSlugs: [String!]
  tokens: [PortfolioV2AppBalanceByAppTokenFilterInput!]
}

input PortfolioV2AppBalanceByAppTokenFilterInput {
  address: String!
  network: Network!
}

input PortfolioV2AppBalanceByAppGroupFiltersInput {
  minBalanceUSD: Float
  metaType: MetaTypeV3
  search: String
  appSlugs: [String!]
}

input PortfolioV2AppBalanceByMetaTypeFiltersInput {
  minBalanceUSD: Float
  appSlugs: [String!]
}

input PortfolioV2AppBalanceByNetworkFiltersInput {
  minBalanceUSD: Float
}

input PortfolioV2AppBalanceByTokenFiltersInput {
  minBalanceUSD: Float
}

type PortfolioV2TokenBalanceMetadata {
  addresses: [Address!]!
  networks: [Network!]!
}

type PortfolioV2TokenBalance {
  metadata: PortfolioV2TokenBalanceMetadata!
  byToken(
    """
    The number of items to return. Default is 25, maximum is 100.
    """
    first: Int = 25

    """
    The cursor to start from. Use the `endCursor` value from the previous response.
    """
    after: String

    """
    Filters to apply to the token balances.
    """
    filters: PortfolioV2TokenBalancesByTokenFiltersInput
  ): PortfolioV2TokenBalanceByTokenConnection!
  byAccount(
    """
    The number of items to return. Default is 25, maximum is 100.
    """
    first: Int = 25

    """
    The cursor to start from. Use the `endCursor` value from the previous response.
    """
    after: String

    """
    Filters to apply to the token balances.
    """
    filters: PortfolioV2TokenBalancesByAccountFiltersInput
  ): PortfolioV2TokenBalancesByAccountConnection!
  byNetwork(
    """
    The number of items to return. Default is 25, maximum is 100.
    """
    first: Int = 25

    """
    The cursor to start from. Use the `endCursor` value from the previous response.
    """
    after: String

    """
    Filters to apply to the token balances.
    """
    filters: PortfolioV2TokenBalancesByNetworkFiltersInput
  ): PortfolioV2TokenBalancesByNetworkConnection!
  totalBalanceUSD: Float!
}

input PortfolioV2TokenBalancesByTokenFiltersInput {
  """
  Minimum balance in USD to filter tokens.
  """
  minBalanceUSD: Float

  """
  Include hidden tokens (flagged as spam) only.
  """
  hidden: Boolean

  """
  Token symbol fuzzy search. Can be a substring of the token symbol or name.
  """
  symbolLike: String

  """
  Token address to filter by.
  """
  tokenAddress: String

  """
  List of tokens to exclude from the results.
  """
  excludeTokens: [PortfolioV2TokenBalancesByTokenFiltersExcludeTokenInput!]

  """
  List of tokens to include in the results.
  """
  includeTokens: [PortfolioV2TokenBalancesByTokenFiltersIncludeTokenInput!]

  """
  Include tokens with missing prices.
  """
  includeTokensWithMissingPrices: Boolean
}

input PortfolioV2TokenBalancesByTokenFiltersExcludeTokenInput {
  address: String!
  network: Network!
}

input PortfolioV2TokenBalancesByTokenFiltersIncludeTokenInput {
  address: String!
  network: Network!
}

input PortfolioV2TokenBalancesByAccountFiltersInput {
  """
  Minimum balance in USD to filter tokens.
  """
  minBalanceUSD: Float

  """
  Token symbol fuzzy search. Can be a substring of the token symbol or name.
  """
  symbolLike: String

  """
  Token address to filter by.
  """
  tokenAddress: String

  """
  Include tokens with missing prices.
  """
  includeTokensWithMissingPrices: Boolean
}

input PortfolioV2TokenBalancesByNetworkFiltersInput {
  """
  Minimum balance in USD to filter tokens.
  """
  minBalanceUSD: Float

  """
  Token symbol fuzzy search. Can be a substring of the token symbol or name.
  """
  symbolLike: String

  """
  Token address to filter by.
  """
  tokenAddress: String

  """
  Include tokens with missing prices.
  """
  includeTokensWithMissingPrices: Boolean
}

type PortfolioV2NftBalance {
  byNetwork(
    first: Int = 25
    after: String
    filters: PortfolioV2NftBalanceByNetworkFiltersInput
    order: PortfolioV2NftBalanceByNetworkOrderInput
  ): PortfolioV2NftBalanceByNetworkConnection!
  byCollection(
    first: Int = 25
    after: String
    filters: PortfolioV2NftBalanceByCollectionFiltersInput
    order: PortfolioV2NftBalanceByCollectionOrderInput
  ): PortfolioV2NftBalanceByCollectionConnection!
  byToken(
    first: Int = 25
    after: String
    filters: PortfolioV2NftBalanceByTokenFiltersInput
    order: PortfolioV2NftBalanceByTokenInputInput
  ): PortfolioV2NftBalanceByTokenConnection!
  totalBalanceUSD: Float!
  totalTokensOwned: String!
  distinctTokensOwned: String!
}

input PortfolioV2NftBalanceByNetworkFiltersInput {
  minBalanceUSD: Float

  """
  If no filter, all NFTs are returned. If filter is hidden=true, only hidden NFTs are returned. If filter is hidden=false, only non hidden NFTs are returned.
  """
  hidden: Boolean
  network: Network
  chainId: Int
  chainIds: [Int!]
}

input PortfolioV2NftBalanceByNetworkOrderInput {
  by: PortfolioV2NftOrderByOption!
  direction: OrderDirectionOption
}

input PortfolioV2NftBalanceByCollectionFiltersInput {
  collectionName: String
  collectionKeys: [String!]
  collections: [NftCollectionInputV2!]

  """
  If no filter, all NFTs are returned. If filter is hidden=true, only hidden NFTs are returned. If filter is hidden=false, only non hidden NFTs are returned.
  """
  hidden: Boolean
  network: Network
  chainId: Int
  chainIds: [Int!]
}

input NftCollectionInputV2 {
  address: Address!
  subCollectionIdentifier: String
  chainId: Int!
}

input PortfolioV2NftBalanceByCollectionOrderInput {
  by: PortfolioV2NftOrderByOption!
  direction: OrderDirectionOption
}

input PortfolioV2NftBalanceByTokenFiltersInput {
  """
  If no filter, all NFTs are returned. If filter is hidden=true, only hidden NFTs are returned. If filter is hidden=false, only non hidden NFTs are returned.
  """
  hidden: Boolean
  collectionKeys: [String!]
  collections: [NftCollectionInputV2!]
  network: Network
  chainId: Int
  chainIds: [Int!]
}

type PortfolioV2Metadata {
  addresses: [Address!]!
  networks: [Network!]!
}

type PortfolioV2 {
  metadata: PortfolioV2Metadata!
  tokenBalances(
    """
    Enqueue and wait for snapshot jobs for the token balances
    """
    enqueueSnapshotJobs: Boolean = true

    """
    Enqueue and wait for tracking jobs for the token balances
    """
    enqueueTrackingJobs: Boolean = true
  ): PortfolioV2TokenBalance!
  appBalances(
    """
    Re-enqueue and wait for snapshot jobs for the app balances
    """
    enqueueSnapshotJobs: Boolean = true

    """
    Enqueue and wait for tracking jobs for the app balances
    """
    enqueueTrackingJobs: Boolean = true

    """
    Clear cached app balances before enqueueing jobs
    """
    forceRefreshTracking: Boolean = false
  ): PortfolioV2AppBalance!
  nftBalances(
    withOverrides: Boolean = false
    waitForUpdate: Boolean = true

    """
    Re-enqueue and wait for snapshot jobs for the nft balances
    """
    enqueueSnapshotJobs: Boolean = false
  ): PortfolioV2NftBalance!
}

type NetworkTokenInfo {
  network: Network!
  address: Address!
  marketCap: BigDecimal
  gasLiquidityUsd: BigDecimal
  imageUrl: String!
}

type OnchainSearchResults {
  results: [OnchainSearchResultObject!]!
}

union OnchainSearchResultObject =
  | AppResult
  | Erc20TokenResult
  | GasTokenResult
  | FarcasterProfileResult
  | UnifiedGasTokenResult
  | NftCollectionResult
  | UnifiedErc20TokenResult
  | UserResult
  | TransactionResult

type AppResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  networks: [Network!]!
  appId: String!
  name: String
  app: App
}

enum SearchResultCategory {
  ADDRESS_LABEL
  APP
  APP_TOKEN
  APP_CONTRACT_POSITION
  BASE_TOKEN
  CHANNEL
  FARCASTER_PROFILE
  GAS_TOKEN
  UNIFIED_GAS_TOKEN
  ERC20_TOKEN
  NETWORK_BASE_TOKEN
  DAO
  NFT_COLLECTION
  NFT_COLLECTION_GROUP
  UNIFIED_ERC20_TOKEN
  USER
  TRANSACTION
}

type Erc20TokenResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  address: Address!
  symbol: String!
  name: String
  network: Network!
  gasTokenLiquidityUsd: Float!
  erc20: FungibleToken
}

type GasTokenResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  address: Address!
  symbol: String!
  name: String
  decimals: Float!
  totalSupply: Float!
  network: Network!
  gasTokenLiquidityUsd: Float!
  gasToken: FungibleToken
}

type FarcasterProfileResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  fid: Float!
  username: String!
  displayName: String
}

type UnifiedGasTokenResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  symbol: String!
  name: String
  groupId: String!
  perNetworkInfo: [NetworkTokenInfo!]!
  groupedGasTokens: [FungibleToken!]!
}

type NftCollectionResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  network: Network!
  address: Address!
  monthlyVolume: BigDecimal!
  openseaSlug: String
  collectionGroupNames: [String!]!
  collection: NftCollection
}

type UnifiedErc20TokenResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  symbol: String!
  name: String
  groupId: String!
  perNetworkInfo: [NetworkTokenInfo!]!
  groupedFungibleTokens: [FungibleToken!]!
}

type UserResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  address: Address!
  ens: String
  lens: String
  network: Network!
  farcaster: String
  account: Account!
}

type TransactionResult {
  id: String!
  category: SearchResultCategory!
  title: String!
  imageUrl: String
  score: String
  hash: String!
  network: Network!
}

"""
Address
"""
scalar Address

"""
EVM function/event signature
"""
scalar Signature

"""
Big decimal scalar
"""
scalar BigDecimal

"""
Ethereum Name Service
"""
scalar Ens

"""
Float in percent points without the "%" character, standard range between 0 and 100 (e.g. 62.4 means 62.4%)
"""
scalar Percentage

type Query {
  """
  Get historical portfolio performance in dollars. NOTE: Currently only supported on Worldchain Mainnet
  """
  historicalPortfolio(
    address: Address!
    chainId: Int!
    timeFrame: TimeFrame!
    excludeTokens: [Address!]
    includeTokens: [Address!]
    currency: Currency = USD
  ): [HistoricalPortfolioTick!]!
  portfolio(
    """
    The wallet addresses for which to fetch balances for.
    """
    addresses: [Address!]!

    """
    The networks on which to fetch balances for.
    """
    networks: [Network!]

    """
    The appIds for which to fetch balances for.
    """
    appIds: [String!]

    """
    Whether to include NFT overrides in the balances.
    """
    withOverrides: Boolean = false
  ): Portfolio! @deprecated(reason: "Use portfolioV2 instead to ensure up to date data")
  balanceJobStatus(jobId: String!): BalanceJobStatus!
    @deprecated(reason: "Use portfolioV2 to avoid having to poll job statuses")
  transactionDetails(
    transactionHash: String!
    network: Network!
    realtimeInterpretation: Boolean = false
  ): ActivityEvent @deprecated(reason: "Use transactionDetailsV2 query instead.")
  transactionHistory(
    network: Network
    networks: [Network!]
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    spamFilter: Boolean = true
    realtimeInterpretation: Boolean = false
    startDate: Timestamp
    endDate: Timestamp
    addresses: [Address!]
    tokenAddresses: [Address!]
    isSigner: Boolean
    fromAddresses: [String!]
    toAddresses: [String!]
    sighashes: [String!]
    actionTypeIds: [Int!]
    experimentalSpamLess: Boolean
  ): ActivityEventConnection! @deprecated(reason: "Use transactionHistoryV2 instead")
  accountsTimeline(
    network: Network
    networks: [Network!]
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    spamFilter: Boolean = true
    realtimeInterpretation: Boolean = false
    startDate: Timestamp
    endDate: Timestamp
    addresses: [Address!]
    tokenAddresses: [Address!]
    isSigner: Boolean
    fromAddresses: [String!]
    toAddresses: [String!]
    sighashes: [String!]
    actionTypeIds: [Int!]
    experimentalSpamLess: Boolean
  ): ActivityEventConnection! @deprecated(reason: "Use transactionHistoryV2 query instead.")
  transactionsForAppV2(
    slug: String!
    chainId: Int
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    startDate: Timestamp
    endDate: Timestamp
  ): ActivityEventConnection!
  transactionsForApp(
    network: Network
    networks: [Network!]
    first: Int

    """
    Cursor of an edge (excluded)
    """
    after: String
    spamFilter: Boolean = true
    realtimeInterpretation: Boolean = false
    startDate: Timestamp
    endDate: Timestamp
    slug: String!
  ): ActivityEventConnection! @deprecated(reason: "Use transactionsForAppV2 instead")
  account(address: Address, ens: String, basename: String): Account
  accounts(addresses: [Address!], ens: [String!], basenames: [String!]): [Account!]!
  farcasterProfile(username: String, fid: Int): FarcasterProfile
  tokenTrends(first: Int = 6, after: String, fid: Int): FarcasterTrendingTokenFeedConnection!
    @deprecated(reason: "Use tokenRankings instead.")
  tokenRanking(first: Int = 6, after: String, fid: Int): FarcasterTokenFeedV2Connection!
  nftRanking(first: Int = 6, after: String, fid: Int): FarcasterNftFeedV2Connection!
  generalSwapFeed(first: Int = 6, after: String, fid: Int): FarcasterSwapFeedV2Connection!
  apps(
    first: Int = 100
    after: String
    orderBy: AppOrderByOption = NAME
    orderDirection: OrderDirectionOption = ASC
    filters: AppsFiltersArgs
  ): AppConnection!
  appDetailsById(appId: String!): App!
  nftUsersTokens(
    network: Network
    networks: [Network!]
    minEstimatedValueUsd: Float
    search: String

    """
    Deprecated: use `collectionIds` instead
    """
    collections: [Address!]

    """
    Deprecated: use `collectionIds` instead
    """
    collectionInputs: [NftCollectionInput!]
    collectionIds: [ID!]
    standard: NftStandard
    onlyHidden: Boolean
    bypassHidden: Boolean

    """
    Nullable will be removed in the future so do not send something nullable
    """
    owners: [Address!]
    first: Int = 24

    """
    Cursor of an edge (excluded)
    """
    after: String
    input: NftUsersTokensConnectionInput
    withOverrides: Boolean
  ): NftUserTokenConnection! @deprecated(reason: "Use the byToken field on nftBalances from portfolioV2 instead.")
  nftToken(collectionAddress: String!, network: Network!, tokenId: String!): NFT
    @deprecated(reason: "Use nftTokenV2 instead.")
  nftTokenV2(collectionAddress: Address!, chainId: Int!, tokenId: String!): NFT
  nftCollectionV2(input: NftCollectionInputV2): NftCollection
  nftCollection(input: NftCollectionInput): NftCollection @deprecated(reason: "Use nftCollectionV2 instead.")
  nftCollectionsV2(collections: [NftCollectionInputV2!]!): [NftCollection!]!
  nftCollections(collections: [NftCollectionInput!]!): [NftCollection!]!
    @deprecated(reason: "Use nftCollectionsV2 instead.")
  nftCollectionsForDeployersV2(input: NftCollectionsForDeployersInputV2!): NftCollectionsForOwnersCollectionsConnection!
  nftCollectionsForDeployers(input: NftCollectionsForDeployersInput!): NftCollectionsForOwnersCollectionsConnection!
    @deprecated(reason: "Use nftCollectionsForDeployersV2 instead.")
  nftCollectionsForOwnersV2(input: NftCollectionsForOwnersInputV2!): NftCollectionsForOwnersCollectionsConnection!
  nftCollectionsForOwners(input: NftCollectionsForOwnersInput!): NftCollectionsForOwnersCollectionsConnection!
    @deprecated(reason: "Use nftCollectionsForOwnersV2 instead.")
  nftEventsForAddressesV2(input: NftEventForUsersInputV2!): NftEventConnection!
  nftEventsForAddresses(input: NftEventForUsersInput!): NftEventConnection!
    @deprecated(reason: "Use nftEventsForAddressesV2 instead.")
  nftEventsFromBlockV2(input: NftEventInputV2!): NftEventConnection!
  fungibleToken(address: Address!, network: Network!): FungibleToken @deprecated(reason: "Use fungibleTokenV2 instead.")
  fungibleTokenV2(address: Address!, chainId: Int!): FungibleToken
  fungibleTokenBatch(tokens: [FungibleTokenInput!]!): [FungibleToken]!
    @deprecated(reason: "Use fungibleTokenBatchV2 instead.")
  fungibleTokenBatchV2(tokens: [FungibleTokenInputV2!]!): [FungibleToken]!
  contract(address: String!, network: Network!, allowInferred: Boolean = true): Contract!
    @deprecated(reason: "Use contractV2 instead.")
  contractV2(address: String!, chainId: Int!, allowInferred: Boolean = true): Contract!
  portfolioV2(
    addresses: [Address!]!

    """
    Prefer using chainIds instead.
    """
    networks: [Network!]
    chainIds: [Int!]
    includeProxyAccounts: Boolean = true
  ): PortfolioV2!
  transactionDetailsV2(hash: String!, chainId: Int!, index: Float, subject: Address): [TimelineEventV2!]
  transactionHistoryV2(
    subjects: [Address!]!
    perspective: TransactionHistoryV2Perspective = Signer
    first: Int = 10
    after: String
    filters: TransactionHistoryV2FiltersArgs
  ): TransactionHistoryV2EntryConnection!
  searchV2(input: SearchInputV2!): OnchainSearchResults!
  search(input: SearchPublicInput!): OnchainSearchResults! @deprecated(reason: "Use searchV2 instead.")
  network(chainId: Int!, vm: VirtualMachineType!): NetworkObject
  tokenActivityFeed(
    chainId: Int!
    tokenAddress: String!
    fid: Int!
    first: Int
    after: String
    type: TokenChannelFeedType = DEFAULT
    filters: ChannelFeedFilterArgs
  ): TokenChannelFeedConnection!
}

enum AppOrderByOption {
  NAME
  CREATED_AT
}

input AppsFiltersArgs {
  search: String
  slug: String
  name: String
  categoryId: Int
}

input NftCollectionInput {
  address: Address

  """
  Deprecated : Use `address` instead
  """
  collectionAddress: String
  subCollectionIdentifier: String
  network: Network!
}

input NftUsersTokensConnectionInput {
  owners: [Address!]!
  network: Network
  networks: [Network!]
  minEstimatedValueUsd: Float

  """
  Deprecated: use `collectionIds` instead
  """
  collections: [Address!]

  """
  Deprecated: use `collectionIds` instead
  """
  collectionInputs: [NftCollectionInput!]
  collectionIds: [ID!]
  standard: NftStandard
  search: String
  onlyHidden: Boolean
  bypassHidden: Boolean
  withOverrides: Boolean
  first: Int = 24

  """
  Cursor of an edge (excluded)
  """
  after: String
}

input NftCollectionsForDeployersInputV2 {
  deployers: [Address!]
  first: Int

  """
  Cursor of an edge (excluded)
  """
  after: String
  chainIds: [Int!]!
}

input NftCollectionsForDeployersInput {
  deployers: [Address!]
  first: Int

  """
  Cursor of an edge (excluded)
  """
  after: String
  networks: [Network!]!
}

input NftCollectionsForOwnersInputV2 {
  owners: [Address!]
  first: Int

  """
  Cursor of an edge (excluded)
  """
  after: String
  chainIds: [Int!]!
}

input NftCollectionsForOwnersInput {
  owners: [Address!]
  first: Int

  """
  Cursor of an edge (excluded)
  """
  after: String
  networks: [Network!]!
}

input NftEventForUsersInputV2 {
  chainIds: [Int!]!
  userAddresses: [String!]!
  before: Timestamp
  since: Timestamp
  limit: Int!
  after: String
}

input NftEventForUsersInput {
  networks: [Network!]!
  userAddresses: [String!]!
  before: Timestamp
  since: Timestamp
  limit: Int!
  after: String
}

input NftEventInputV2 {
  chainId: Int!
  limit: Int!
  fromBlock: Int!
  untilBlock: Int
  after: String
}

input FungibleTokenInput {
  address: Address!
  network: Network!
}

input FungibleTokenInputV2 {
  address: Address!
  chainId: Int!
}

"""
The wallet's perspective of a transaction. The wallet can be the initiator of a transaction, or a receiving actor.
"""
enum TransactionHistoryV2Perspective {
  Signer
  Receiver
  All
}

input TransactionHistoryV2FiltersArgs {
  """
  Use chainIds instead.
  """
  network: [Network!]

  """
  Filter by chainIds
  """
  chainIds: [Int!]

  """
  Filter by token transferred
  """
  tokenAddress: [Address!]

  """
  Filter by which address signed the transaction, or which address sent a token
  """
  receivedFrom: [Address!]

  """
  Filter by which address received a token
  """
  sentTo: [Address!]
  categories: [TransactionHistoryV2Category!]

  """
  Filter by which contract was used, typically the "to" field of the transaction
  """
  contractAddress: [Address!]
  startDate: Timestamp
  endDate: Timestamp
  orderByDirection: OrderDirectionOption
}

"""
The category of the events in the transaction history. Can be Swap, Brige, etc
"""
enum TransactionHistoryV2Category {
  Bridge
  Swap
  Nft_Sale
  Nft_Mint
}

input SearchInputV2 {
  search: String!
  maxResultsPerCategory: Float = 3
  categories: [OnchainSearchCategory!]
  chainIds: [Int!]
}

enum OnchainSearchCategory {
  ADDRESS_LABEL
  APP
  FARCASTER_PROFILE
  GAS_TOKEN
  UNIFIED_GAS_TOKEN
  ERC20_TOKEN
  NFT_COLLECTION
  UNIFIED_ERC20_TOKEN
  USER
  TRANSACTION
}

input SearchPublicInput {
  search: String!
  maxResultsPerCategory: Float = 3
  categories: [OnchainSearchCategory!]
  networks: [Network!]
}

enum TokenChannelFeedType {
  DEFAULT
  ALL_CASTS
  FOLLOWED_SWAPS
  ALL_SWAPS
}

input ChannelFeedFilterArgs {
  minimumUsdVolume: Int
  ignoreAutomated: Boolean
  isBuy: Boolean
}

type Mutation {
  computeAppBalances(input: PortfolioInput!): BalanceJobId!
    @deprecated(reason: "Use appBalances from portfolioV2 to avoid having to use this compute mutation")
  computeTokenBalances(input: PortfolioInput!): BalanceJobId!
    @deprecated(reason: "Use tokenBalances from portfolioV2 to avoid having to use this compute mutation")
  refreshNftMetadata(id: ID!): NFT
  markCollectionAsSpam(collectionAddress: Address!, chainId: Int!): Boolean!
  markCollectionAsNotSpam(collectionAddress: Address!, chainId: Int!): Boolean!
}

input PortfolioInput {
  """
  The wallet addresses for which to fetch balances
  """
  addresses: [Address!]!

  """
  The networks for which to fetch balances
  """
  networks: [Network!]

  """
  The app slugs for which to fetch balances
  """
  appIds: [String!]
  flagAsStale: Boolean
}

Access comprehensive onchain activity with rich transaction details, structured asset deltas, and support for both EOA and smart contract wallets.

Try it now
transactionHistoryV2​
Key Features​
1. Dynamic Transaction Descriptions​

One of the most powerful features of the transactionHistoryV2 endpoint is its ability to provide both simple text descriptions and dynamic, interactive elements for each transaction. This is handled through three complementary fields:

processedDescription: A plain text, human-readable summary (e.g. "Swapped 400 USDC for 0.2 ETH")
description: A templated version that includes reference tokens (e.g. "Swapped $1 for $2")
descriptionDisplayItems: Structured data for each referenced element in the description

This enables developers to build rich, interactive transaction displays with automatic descriptions that can be customized for different UIs.

2. Enhanced Filtering Options​

The new endpoint provides more granular filtering options:

filters: {
  chainIds: [Int!]             # Filter by specific chains
  tokenAddress: [Address!]        # Filter by tokens involved
  receivedFrom: [Address!]        # Filter by sender address (works with account abstraction)
  sentTo: [Address!]              # Filter by recipient address
  categories: [String!]           # Filter by category ["Swap", "Bridge", "Nft_Mint", "Nft_Sale"]
  contractAddress: [Address!]     # Filter by contract interacted with
}

Example Filters​
{
  "filters": {
    "chainIds": [8453, 1],
    "tokenAddress": ["0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"],
    "receivedFrom": ["0x52c8ff44260056f896e20d8a43610dd88f05701b"],
    "sentTo": ["0x9b3a20176d2c5d0a22dae382496416a1a8934b30"],
    "categories": ["Swap", "Bridge", "Nft_Mint", "Nft_Sale"],
    "contractAddress": ["0x03059433bcdb6144624cc2443159d9445c32b7a8"]
  },
}

3. Detailed Asset Deltas​

Each transaction includes explicit delta information showing exactly what changed in the user's portfolio:

perspectiveDelta: Returns balance changes for the subject of the transaction (e.g., EOA or contract that signs the transaction)
tokenDeltasV2: Shows token balance changes with positive (received) and negative (sent) amounts
nftDeltasV2: Shows NFT balance changes with collection and token details
deltas: Returns all balances changes for all addresses involved in the transaction
4. Perspective Control​

The new perspective parameter gives you control over which transactions to include:

Signer: Only transactions initiated by the subject addresses (default)
Receiver: Only transactions where subject addresses received assets
All: All transactions involving the subject addresses
Example Use Cases​
1. Human-readable Transactions​

Create rich transaction descriptions with dynamic elements for a user-friendly experience.

Try it now
Example Variables​
{
  "subjects": "0x52c8ff44260056f896e20d8a43610dd88f05701b",
  "perspective": "Signer",
  "first": 20,
  "after": null,
  "filters": {
    "chainIds": [8453]
  }
}

Example Query​
query TransactionHistoryV2(
  $subjects: [Address!]!
  $perspective: TransactionHistoryV2Perspective
  $first: Int
  $filters: TransactionHistoryV2FiltersArgs
) {
  transactionHistoryV2(subjects: $subjects, perspective: $perspective, first: $first, filters: $filters) {
    edges {
      node {
        ... on TimelineEventV2 {
          # Transaction method details
          methodSignature
          methodSighash

          # Transaction metadata
          transaction {
            blockNumber
            hash
            network
            timestamp

            # Sender details with identity
            fromUser {
              address
              displayName {
                value
                source
              }
              farcasterProfile {
                fid
                username
              }
            }

            # Recipient details with identity
            toUser {
              address
              displayName {
                value
                source
              }
            }
          }

          # Human-readable transaction information
          interpretation {
            processedDescription # Text description
            description # Templated description
            # Display items referenced in description
            descriptionDisplayItems {
              # Token information
              ... on TokenDisplayItem {
                type
                tokenAddress
                amountRaw
                network
                tokenV2 {
                  decimals
                  symbol
                  name
                  imageUrlV2
                  priceData {
                    price
                    priceChange24h
                  }
                }
              }

              # Account information
              ... on ActorDisplayItem {
                type
                address
                account {
                  displayName {
                    value
                    source
                  }
                }
              }
            }
          }
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}

Example Response​
{
  "data": {
    "transactionHistoryV2": {
      "edges": [
        {
          "node": {
            "methodSignature": "transfer(address,uint256)",
            "methodSighash": "0xa9059cbb",
            "transaction": {
              "blockNumber": 29598605,
              "hash": "0x69a1f72b4603e72304e2636cc6138402b8f97430622b800275808b5c0d9e15a4",
              "network": "BASE_MAINNET",
              "timestamp": 1745986557000,
              "fromUser": {
                "address": "0x52c8ff44260056f896e20d8a43610dd88f05701b",
                "displayName": {
                  "value": "0xjasper.eth",
                  "source": "ENS"
                },
                "farcasterProfile": {
                  "fid": 177,
                  "username": "jasper"
                }
              },
              "toUser": {
                "address": "0x1bff6cbd036162e3535b7969f63fd8043ccc1433",
                "displayName": {
                  "value": "0x1bff...1433",
                  "source": "ADDRESS"
                }
              }
            },
            "interpretation": {
              "processedDescription": "Sent 1,143.944 BARMSTRONG to 0x32bd...689c",
              "description": "Sent $1 to $2",
              "descriptionDisplayItems": [
                {
                  "type": "token",
                  "tokenAddress": "0x1bff6cbd036162e3535b7969f63fd8043ccc1433",
                  "amountRaw": "1143943988872272227099",
                  "network": "BASE_MAINNET",
                  "tokenV2": {
                    "decimals": 18,
                    "symbol": "BARMSTRONG",
                    "name": "Barmstrong",
                    "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x1bff6cbd036162e3535b7969f63fd8043ccc1433.png",
                    "priceData": {
                      "price": 0.00497470302555712,
                      "priceChange24h": 2.0383762988015475
                    }
                  }
                },
                {
                  "type": "actor",
                  "address": "0x32bd1c7be081e7ac7f03396ee0839523eae6689c",
                  "account": {
                    "displayName": {
                      "value": "0x32bd...689c",
                      "source": "ADDRESS"
                    }
                  }
                }
              ]
            }
          }
        }
      ],
      "pageInfo": {
        "endCursor": "MTc0NTk4NjU1N3x8YmFzZXx8MHg2OWExZjcyYjQ2MDNlNzIzMDRlMjYzNmNjNjEzODQwMmI4Zjk3NDMwNjIyYjgwMDI3NTgwOGI1YzBkOWUxNWE0",
        "hasNextPage": true
      }
    }
  }
}

2. Asset Deltas​

Track detailed token and NFT balance changes across transactions.

Try it now
Example Variables​
{
  "subjects": "0x52c8ff44260056f896e20d8a43610dd88f05701b",
  "perspective": "Signer",
  "first": 20,
  "after": null,
  "filters": {
    "chainIds": [8453]
  }
}

Example Query​
query TransactionHistoryV2(
  $subjects: [Address!]!
  $perspective: TransactionHistoryV2Perspective
  $first: Int
  $filters: TransactionHistoryV2FiltersArgs
  $after: String
) {
  transactionHistoryV2(
    subjects: $subjects
    perspective: $perspective
    first: $first
    filters: $filters
    after: $after
  ) {
    edges {
      node {
        ... on TimelineEventV2 {
          hash
          network
          timestamp
          value

          # Deltas for signed transactions
          deltas {
            totalCount
            edges {
              node {
                account {
                  address
                  isContract
                }
                tokenDeltasCount
                tokenDeltasV2 {
                  edges {
                    node {
                      amount
                      amountRaw
                      token {
                        address
                        credibility
                        decimals
                        symbol
                        imageUrlV2
                        priceData {
                          price
                          priceChange24h
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }

        # Transaction data for perspective: "Receiver"
        ... on ActivityTimelineEventDelta {
          transactionHash
          transactionBlockTimestamp
          network
          networkObject {
            name
            chainId
          }
          subject
          from {
            address
            isContract
          }
          to {
            address
            isContract
          }

          # Deltas for perspective: "Receiver"
          fungibleCount
          fungibleDeltas {
            amount
            amountRaw
            token {
              address
              credibility
              decimals
              symbol
              imageUrlV2
              priceData {
                price
                priceChange24h
              }
            }
          }
        }
      }
      cursor
    }
    totalCount
    pageInfo {
      endCursor
      hasNextPage
      hasPreviousPage
      startCursor
    }
  }
}

Example Response​
{
  "data": {
    "transactionHistoryV2": {
      "edges": [
        {
          "node": {
            "hash": "0x69a1f72b4603e72304e2636cc6138402b8f97430622b800275808b5c0d9e15a4",
            "network": "BASE_MAINNET",
            "timestamp": 1745986557000,
            "value": "0",
            "deltas": {
              "totalCount": 2,
              "edges": [
                {
                  "node": {
                    "account": {
                      "address": "0x52c8ff44260056f896e20d8a43610dd88f05701b",
                      "isContract": false
                    },
                    "tokenDeltasCount": 1,
                    "tokenDeltasV2": {
                      "edges": [
                        {
                          "node": {
                            "amount": -1143.9439888722723,
                            "amountRaw": "-1143943988872272227099",
                            "token": {
                              "address": "0x1bff6cbd036162e3535b7969f63fd8043ccc1433",
                              "credibility": null,
                              "decimals": 18,
                              "symbol": "BARMSTRONG",
                              "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x1bff6cbd036162e3535b7969f63fd8043ccc1433.png",
                              "priceData": {
                                "price": 0.004944035913116251,
                                "priceChange24h": 0.22935723083206128
                              }
                            }
                          }
                        }
                      ]
                    }
                  }
                },
                {
                  "node": {
                    "account": {
                      "address": "0x32bd1c7be081e7ac7f03396ee0839523eae6689c",
                      "isContract": false
                    },
                    "tokenDeltasCount": 1,
                    "tokenDeltasV2": {
                      "edges": [
                        {
                          "node": {
                            "amount": 1143.9439888722723,
                            "amountRaw": "1143943988872272227099",
                            "token": {
                              "address": "0x1bff6cbd036162e3535b7969f63fd8043ccc1433",
                              "credibility": null,
                              "decimals": 18,
                              "symbol": "BARMSTRONG",
                              "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x1bff6cbd036162e3535b7969f63fd8043ccc1433.png",
                              "priceData": {
                                "price": 0.004944035913116251,
                                "priceChange24h": 0.22935723083206128
                              }
                            }
                          }
                        }
                      ]
                    }
                  }
                }
              ]
            }
          },
          "cursor": "MTc0NTk4NjU1N3x8YmFzZXx8MHg2OWExZjcyYjQ2MDNlNzIzMDRlMjYzNmNjNjEzODQwMmI4Zjk3NDMwNjIyYjgwMDI3NTgwOGI1YzBkOWUxNWE0"
        }
      ],
      "totalCount": 0,
      "pageInfo": {
        "endCursor": "MTc0NTk4NjU1N3x8YmFzZXx8MHg2OWExZjcyYjQ2MDNlNzIzMDRlMjYzNmNjNjEzODQwMmI4Zjk3NDMwNjIyYjgwMDI3NTgwOGI1YzBkOWUxNWE0",
        "hasNextPage": true,
        "hasPreviousPage": false,
        "startCursor": "MTc0NTk4NjU1N3x8YmFzZXx8MHg2OWExZjcyYjQ2MDNlNzIzMDRlMjYzNmNjNjEzODQwMmI4Zjk3NDMwNjIyYjgwMDI3NTgwOGI1YzBkOWUxNWE0"
      }
    }
  }
}

Arguments​
Argument	Description	Type
subjects	List of addresses to query (required)	[Address!]!
perspective	Transaction perspective filter	TransactionHistoryV2Perspective = Signer
first	Number of results to return	Int = 10
after	Cursor for pagination	String
filters	Additional filtering options	TransactionHistoryV2FiltersArgs
TransactionHistoryV2Perspective Enum​
Value	Description
Signer	Only include transactions signed by subject addresses (default)
Receiver	Only include transactions where subjects received assets
All	Include all transactions involving subject addresses
Best Practices​
Use Delta Information: deltas provide the most accurate picture of what changed in a wallet, clearly showing assets sent and received
Consider Perspective: Choose the appropriate perspective based on your use case:
Signer for user-initiated transactions (properly attributes account abstraction transactions)
Receiver for incoming transactions
All for complete history
Leverage Account Abstraction Support: Take advantage of the improved signer attribution when working with smart contract wallets and account abstraction frameworks
Optimize Query Size: Only request the fields you need to reduce response size
Utilize Filtering: Use the enhanced filters to narrow down results for specific use cases
NOTE

Transactions are presented from the perspective specified in the perspective parameter. The default is Signer, which shows transactions from the point of view of the initiating address.

TIP

When working with token amounts in deltas, the amount field is already adjusted for decimals, making it ready for display. Positive values indicate tokens received, negative values indicate tokens sent.

Copy page for LLMs

Transaction Details

Presents the details of an onchain transaction in a simple descriptive summary with references to dynamic elements such as tokens, NFTs, accounts, and apps. This endpoint is ideal for building detailed transaction views or surfacing specific transaction information.

Try it now
transactionDetailsV2​

Takes a hash and chainId as input. Returns comprehensive information about a specific transaction including:

Transaction details (hash, nonce, gas info)
Human-readable description
Asset transfers (tokens and NFTs)
Related app information
Account details for actors involved
Example Use Case: Transaction Details Page​

Let's say you want to display details about a specific transaction in a human-readable format with dynamic references to onchain elements. The query returns:

Formatted transaction description (processedDescription)
Raw description with variables (description)
Display items for each referenced element (descriptionDisplayItems)
Network and app information
Complete data about tokens and NFTs involved
Example Variables​
{
  "hash": "0xc8323f3a5a03b8f8bbb0fe0d2d3b297334e9351dffb74efb8ae5ff5dc1fabf57",
  "chainId": 8453
}

Example Query​
query TransactionDetailsV2($hash: String!, $chainId: Int!) {
  transactionDetailsV2(hash: $hash, chainId: $chainId) {
    # Transaction metadata
    transaction {
      hash
      nonce
      gasPrice
      gas
      blockNumber
      timestamp
      # Signing account + identity
      fromUser {
        address
        displayName {
          value
        }
        farcasterProfile {
          fid
          username
          metadata {
            imageUrl
          }
        }
      }
      # Account / contract interacted with
      toUser {
        address
        displayName {
          value
        }
        farcasterProfile {
          fid
          username
          metadata {
            imageUrl
          }
        }
      }
    }
    # Application details (if any)
    app {
      displayName
      imgUrl
    }
    interpretation {
      # Basic text description
      processedDescription
      # Templated description with reference tokens
      description
      # Structured data for referenced elements
      descriptionDisplayItems {
        ... on TokenDisplayItem {
          type
          network
          tokenAddress
          amountRaw
          tokenV2 {
            symbol
            decimals
            name
            imageUrl
            priceData {
              price(currency: USD)
              priceChange24h
              marketCap
            }
          }
        }
        ... on NFTDisplayItem {
          type
          network
          collectionAddress
          tokenId
          quantity
          nftToken {
            collection {
              name
            }
          }
        }
        ... on ActorDisplayItem {
          type
          address
          account {
            displayName {
              value
            }
          }
        }
      }
    }
    deltas {
      edges {
        node {
          account {
            address
          }
          nftDeltasV2 {
            edges {
              node {
                collectionAddress
                nft {
                  name
                }
              }
            }
          }
          tokenDeltasV2 {
            edges {
              node {
                token {
                  address
                  imageUrlV2
                }
              }
            }
          }
        }
      }
    }
  }
}

Example Response​
{
  "data": {
    "transactionDetailsV2": [
      {
        "transaction": {
          "hash": "0xc8323f3a5a03b8f8bbb0fe0d2d3b297334e9351dffb74efb8ae5ff5dc1fabf57",
          "nonce": 1766,
          "gasPrice": "24165433",
          "gas": 381746,
          "blockNumber": 22625088,
          "timestamp": 1732039523000,
          "fromUser": {
            "address": "0x52c8ff44260056f896e20d8a43610dd88f05701b",
            "displayName": {
              "value": "0xjasper.eth"
            },
            "farcasterProfile": {
              "fid": 177,
              "username": "jasper",
              "metadata": {
                "imageUrl": "https://i.seadn.io/gae/GGk8oCF1aOIhymm-IRnJj4GuL7oajAwCXA9uJgxmkVk-aVhfSB2OrOVdnT88OnIg5XQWj1YhHGcPEbTXJeaiTtZdNZPuZd_enYb6qEw?w=500&auto=format"
              }
            }
          },
          "toUser": {
            "address": "0x03059433bcdb6144624cc2443159d9445c32b7a8",
            "displayName": {
              "value": "0x0305...b7a8"
            },
            "farcasterProfile": null
          }
        },
        "app": {
          "displayName": "Coinbase Commerce",
          "imgUrl": "https://storage.googleapis.com/zapper-fi-assets/apps%2Fcoinbase-commerce.png"
        },
        "interpretation": {
          "processedDescription": "Swapped 231.668 DEGEN for 4.95 USDC and sent to 0x9b3a...4b30",
          "description": "Swapped $1 for $2 and sent to $3",
          "descriptionDisplayItems": [
            {
              "type": "token",
              "network": "BASE_MAINNET",
              "tokenAddress": "0x4ed4e862860bed51a9570b96d89af5e1b0efefed",
              "amountRaw": "231668037511194154483",
              "tokenV2": {
                "symbol": "DEGEN",
                "decimals": 18,
                "name": "Degen",
                "imageUrl": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x4ed4e862860bed51a9570b96d89af5e1b0efefed.png",
                "priceData": {
                  "price": 0.003191673866992095,
                  "priceChange24h": 9.296120056701906,
                  "marketCap": 117983211.7532853
                }
              }
            },
            {
              "type": "token",
              "network": "BASE_MAINNET",
              "tokenAddress": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
              "amountRaw": "4950000",
              "tokenV2": {
                "symbol": "USDC",
                "decimals": 6,
                "name": "USD Coin",
                "imageUrl": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.png",
                "priceData": {
                  "price": 1.0000552,
                  "priceChange24h": 0,
                  "marketCap": 157460623.92667243
                }
              }
            },
            {
              "type": "actor",
              "address": "0x9b3a20176d2c5d0a22dae382496416a1a8934b30",
              "account": {
                "displayName": {
                  "value": "0x9b3a...4b30"
                }
              }
            }
          ]
        },
        "deltas": {
          "edges": [
            {
              "node": {
                "account": {
                  "address": "0x52c8ff44260056f896e20d8a43610dd88f05701b"
                },
                "nftDeltasV2": {
                  "edges": []
                },
                "tokenDeltasV2": {
                  "edges": [
                    {
                      "node": {
                        "token": {
                          "address": "0x4ed4e862860bed51a9570b96d89af5e1b0efefed",
                          "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x4ed4e862860bed51a9570b96d89af5e1b0efefed.png"
                        }
                      }
                    }
                  ]
                }
              }
            },
            {
              "node": {
                "account": {
                  "address": "0x0cc3150056ff3fa2e70be77d25fe9ec33d12a437"
                },
                "nftDeltasV2": {
                  "edges": []
                },
                "tokenDeltasV2": {
                  "edges": [
                    {
                      "node": {
                        "token": {
                          "address": "0x4ed4e862860bed51a9570b96d89af5e1b0efefed",
                          "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x4ed4e862860bed51a9570b96d89af5e1b0efefed.png"
                        }
                      }
                    },
                    {
                      "node": {
                        "token": {
                          "address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
                          "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.png"
                        }
                      }
                    }
                  ]
                }
              }
            },
            {
              "node": {
                "account": {
                  "address": "0x6d8675a52438849d90241cb639fba41bdc3329c8"
                },
                "nftDeltasV2": {
                  "edges": []
                },
                "tokenDeltasV2": {
                  "edges": [
                    {
                      "node": {
                        "token": {
                          "address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
                          "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.png"
                        }
                      }
                    }
                  ]
                }
              }
            },
            {
              "node": {
                "account": {
                  "address": "0x9b3a20176d2c5d0a22dae382496416a1a8934b30"
                },
                "nftDeltasV2": {
                  "edges": []
                },
                "tokenDeltasV2": {
                  "edges": [
                    {
                      "node": {
                        "token": {
                          "address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
                          "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.png"
                        }
                      }
                    }
                  ]
                }
              }
            }
          ]
        }
      }
    ]
  }
}

Arguments​
Argument	Description	Type
hash	The transaction hash to retrieve details for	String!
chainId	The chain where the transaction occurred	Int!
Fields​
Main Fields​
Field	Description	Type
key	A unique identifier	String!
network	Network where the transaction occurred	Network!
timestamp	Unix timestamp in milliseconds	Timestamp!
transaction	Contains detailed transaction information	OnChainTransaction!
app	The associated application details	ActivityFeedApp!
interpretation	Contains human-readable descriptions and asset transfers	ActivityInterpretation!
Transaction Fields​
Field	Description	Type
hash	Transaction hash	String!
nonce	Transaction nonce	Int!
gasPrice	Gas price in wei	String!
gas	Gas limit	Int!
fromUser	The initiating address with details	Account!
toUser	The receiving address with details	Account!
blockHash	Hash of the block containing the transaction	String!
blockNumber	Block number containing the transaction	Int!
Interpretation Fields​
Field	Description	Type
description	Human-readable description with variables	String!
processedDescription	Fully processed human-readable description	String!
descriptionDisplayItems	References for variables in the description	[ActivityFeedDisplayItem!]!
inboundAttachments	Assets received in the transaction	[ActivityFeedDisplayItem!]!
outboundAttachments	Assets sent in the transaction	[ActivityFeedDisplayItem!]!
Display Item Fields​

Common fields for all display item types:

Field	Description	Type
type	Type of the display item	String!
network	Network of the item	Network!

Token-specific fields:

Field	Description	Type
tokenAddress	Contract address of the token	Address!
amountRaw	Raw token amount (requires decimal adjustment)	String!
tokenV2	Detailed token information	Token!

NFT-specific fields:

Field	Description	Type
collectionAddress	Contract address of the NFT collection	Address!
tokenId	Unique identifier of the NFT	String!
quantity	Number of NFTs transferred	Float

Actor-specific fields:

Field	Description	Type
address	Address of the actor	Address!
account	Account details including display name	Account!
NOTE

The description field contains variables in the format $1, $2, etc., which reference items in the descriptionDisplayItems array. This allows you to create interactive elements by replacing these variables with links to the corresponding tokens, NFTs, or accounts.

TIP

When displaying token amounts, remember to divide amountRaw by 10^decimals to get the human-readable amount. For example, an amountRaw of "400000000" with 6 decimals represents 400 USDC.

Copy page for LLMsToken Prices & Charts

Get comprehensive onchain prices, current and historical, for any token that has an onchain market across supported networks. Price ticks are also provided for price charts with open, median, and close data.

fungibleTokenV2​

Takes an address and chainId as input. Returns detailed token information including:

Real-time onchain sourced price data
Price history with customizable timeframes
Holders, percentage owned, and value
Liquidity and market cap data
Latest swaps
Support for multiple price currencies (default: USD)
Example Use Case: Token Details with Charts​

Let's say you want to create a token page providing the price, market data, historical graphs in USD as well as metadata including the token's image, name, and symbol.

Try it now
Example Variables​
{
  "address": "0xf3f92a60e6004f3982f0fde0d43602fc0a30a0db",
  "chainId": 480,
  "currency": "USD",
  "timeFrame": "DAY"
}

Example Query​
query TokenPriceData($address: Address!, $chainId: Int!, $currency: Currency!, $timeFrame: TimeFrame!) {
  fungibleTokenV2(address: $address, chainId: $chainId) {
    # Basic token information
    address
    symbol
    name
    decimals
    imageUrlV2

    # Market data and pricing information
    priceData {
      marketCap
      price
      priceChange5m
      priceChange1h
      priceChange24h
      volume24h
      totalGasTokenLiquidity
      totalLiquidity

      # Historical price data for charts
      priceTicks(currency: $currency, timeFrame: $timeFrame) {
        open
        median
        close
        timestamp
      }
    }
  }
}

Example Response​
{
  "data": {
    "fungibleTokenV2": {
      "address": "0xf3f92a60e6004f3982f0fde0d43602fc0a30a0db",
      "symbol": "ORB",
      "name": "Orb",
      "decimals": 18,
      "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/worldchain/0xf3f92a60e6004f3982f0fde0d43602fc0a30a0db.png",
      "priceData": {
        "marketCap": 334470.7897902368,
        "price": 0.00023383417352516877,
        "priceChange5m": -0.0199982305272961,
        "priceChange1h": -0.2097692977861887,
        "priceChange24h": 5.773325856543643,
        "volume24h": 7466.82861328125,
        "totalGasTokenLiquidity": 4.779354739755427,
        "totalLiquidity": 11721.561173042304,
        "priceTicks": [
          {
            "open": 0.0002140876677549433,
            "median": 0.00022124794010452628,
            "close": 0.00022118157877651454,
            "timestamp": 1747677600000
          },
          {
            "open": 0.00022096051014730816,
            "median": 0.00022096051014730816,
            "close": 0.00022100471223336377,
            "timestamp": 1747677900000
          },
          {
            "open": 0.00022096051014730816,
            "median": 0.00022096051014730816,
            "close": 0.00022100471223336377,
            "timestamp": 1747678200000
          },
          {
            "open": 0.00022100471223336377,
            "median": 0.00022100471223336377,
            "close": 0.00022100471223336377,
            "timestamp": 1747678500000
          },
          {
            "open": 0.00023383417352516877,
            "median": 0.00023383417352516877,
            "close": 0.00023383417352516877,
            "timestamp": 1747767600000
          }
        ]
      }
    }
  }
}

Example Use Case: Latest Swaps​

Get a paginated list of the latest swaps for a given token address. Also surfaces identity information such as displayName or farcasterProfile (if any).

NOTE

This field requires heavy computation and costs an additional 8 credits.

Try it now
Example Variables​
{
  "address": "0x0578d8a44db98b23bf096a382e016e29a5ce0ffe",
  "chainId": 8453
}

Example Query​
query fungibleTokenV2($address: Address!, $chainId: Int!) {
  fungibleTokenV2(address: $address, chainId: $chainId) {
    # Latest Swaps
    priceData {
      latestSwaps(first: 3) {
        edges {
          node {
            boughtTokenAddress
            boughtAmount
            soldTokenAddress
            soldAmount
            gasTokenVolume
            volumeUsd
            timestamp
            transactionHash
            from {
              address
              displayName {
                value
                source
              }
              farcasterProfile {
                fid
                username
                metadata {
                  displayName
                  imageUrl
                }
              }
            }
          }
        }
      }
    }
  }
}

Response​
{
  "data": {
    "fungibleTokenV2": {
      "address": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
      "symbol": "27 mgas/s",
      "name": "27 mgas/s",
      "decimals": 18,
      "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd.png",
      "priceData": {
        "latestSwaps": {
          "edges": [
            {
              "node": {
                "timestamp": 1744839371000,
                "transactionHash": "0xdef9ae17c8e9ffdbae9ab726c184aac0f218ce3148f92cfa87c5d09ccb3c47d4",
                "boughtTokenAddress": "0x4200000000000000000000000000000000000006",
                "boughtAmount": 0.000096904283015405,
                "soldTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "soldAmount": 32084.056006244813,
                "volumeUsd": 0.15412087987907147,
                "gasTokenVolume": 0.000096904283015405
              }
            },
            {
              "node": {
                "timestamp": 1744823943000,
                "transactionHash": "0x5da3a1869ef809ab14b7fca7acddf440d6fbffa57fe8bac659cbcecff0c11e70",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 629.0869634078529,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 0.000001938697097137,
                "volumeUsd": 0.0030833900538973754,
                "gasTokenVolume": 0.000001938697097137
              }
            },
            {
              "node": {
                "timestamp": 1744815531000,
                "transactionHash": "0x8dbbc401b87924929afe7ef0731f499d70a5c9c74555c4a3bb0e27390f16fbf0",
                "boughtTokenAddress": "0x4200000000000000000000000000000000000006",
                "boughtAmount": 0.000063636068597575,
                "soldTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "soldAmount": 21068,
                "volumeUsd": 0.10120963263041816,
                "gasTokenVolume": 0.000063636068597575
              }
            },
            {
              "node": {
                "timestamp": 1744767561000,
                "transactionHash": "0xd981578ed22f3d2c629e784f2cd9c3dd7a1f9bc6f396665bf8714f6fb079abcd",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.12290981256175,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            },
            {
              "node": {
                "timestamp": 1744767095000,
                "transactionHash": "0xe409b34e748ca2c2a6c78afe293d813badc96379d7fd3f1093a008833d5858ec",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.12291224817941,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            },
            {
              "node": {
                "timestamp": 1744766441000,
                "transactionHash": "0xd7a9079cf4cbf867c730305c2b61b8b48dd30cba3ce15f5b8feacc89402bd618",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.12291468379734,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            },
            {
              "node": {
                "timestamp": 1744766105000,
                "transactionHash": "0x942f7bda52e857d6044fe86e84169f726481283824134ae192aaf9efaee16bac",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.122917119415554,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            },
            {
              "node": {
                "timestamp": 1744765615000,
                "transactionHash": "0xbe6a25f995905df2c8ce067166c39dd7524e526f129357055987076462b44fa0",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.12291955503404,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            },
            {
              "node": {
                "timestamp": 1744765179000,
                "transactionHash": "0xb2d5c24bd30549dfcfa7b6a6a61127c6b22a17c0a5287ea0ba2bfedf59021d85",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.1229219906528,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            },
            {
              "node": {
                "timestamp": 1744764705000,
                "transactionHash": "0x181d84ecd3cbbecc4add95461a0efaa470c830197b1aca68c2659f1fad5bf22a",
                "boughtTokenAddress": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
                "boughtAmount": 32.12292442627184,
                "soldTokenAddress": "0x4200000000000000000000000000000000000006",
                "soldAmount": 9.9e-8,
                "volumeUsd": 0.00015745400134277343,
                "gasTokenVolume": 9.9e-8
              }
            }
          ]
        }
      }
    }
  }
}

Example Use Case: Token Holders​

Get a paginated list of token holders with their quanity held, percentage of total supply, as well as identity information such as displayName or farcasterProfile (if any).

Try it now
Example Variables​
{
  "address": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
  "chainId": 8453,
  "first": 5
}

Example Query​
query TokenHolders($address: Address!, $chainId: Int!, $first: Float!) {
  fungibleTokenV2(address: $address, chainId: $chainId) {
    # Basic token information
    address
    symbol
    name
    decimals
    imageUrlV2

    # Token holders information
    holders(first: $first) {
      edges {
        node {
          holderAddress
          percentileShare
          value
          account {
            displayName {
              value
              source
            }
            # Social identity data when available
            farcasterProfile {
              username
              fid
              metadata {
                imageUrl
                warpcast
              }
            }
          }
        }
      }
    }
  }
}

Response​
{
  "data": {
    "fungibleTokenV2": {
      "address": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
      "symbol": "27 mgas/s",
      "name": "27 mgas/s",
      "decimals": 18,
      "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd.png",
      "holders": {
        "edges": [
          {
            "node": {
              "holderAddress": "0x3adb6190e0dc8d60e162878704783def2f898d26",
              "percentileShare": 84.73782306624328,
              "value": "847378230662432766735763531",
              "account": {
                "displayName": {
                  "value": "0x3adb...8d26",
                  "source": "ADDRESS"
                },
                "farcasterProfile": null
              }
            }
          },
          {
            "node": {
              "holderAddress": "0x849151d7d0bf1f34b70d5cad5149d28cc2308bf1",
              "percentileShare": 2.5262672668761947,
              "value": "25262672668761945941188720",
              "account": {
                "displayName": {
                  "value": "jesse.xyz",
                  "source": "ENS"
                },
                "farcasterProfile": {
                  "username": "jessepollak",
                  "fid": 99,
                  "metadata": {
                    "imageUrl": "https://imagedelivery.net/BXluQx4ige9GuW0Ia56BHw/1013b0f6-1bf4-4f4e-15fb-34be06fede00/original",
                    "warpcast": "https://warpcast.com/jessepollak"
                  }
                }
              }
            }
          },
          {
            "node": {
              "holderAddress": "0x90360a22946d40196383b4832d366fb3c2fad596",
              "percentileShare": 2.1290545421559686,
              "value": "21290545421559686643069389",
              "account": {
                "displayName": {
                  "value": "0x9036...d596",
                  "source": "ADDRESS"
                },
                "farcasterProfile": null
              }
            }
          },
          {
            "node": {
              "holderAddress": "0x7bf90111ad7c22bec9e9dff8a01a44713cc1b1b6",
              "percentileShare": 1.5262672668761945,
              "value": "15262672668761945941188961",
              "account": {
                "displayName": {
                  "value": "0x7bf9...b1b6",
                  "source": "ADDRESS"
                },
                "farcasterProfile": null
              }
            }
          },
          {
            "node": {
              "holderAddress": "0x4d9ee121638b6fe72907bc1872d5f20eb4e33596",
              "percentileShare": 0.6881155320900804,
              "value": "6881155320900803544851892",
              "account": {
                "displayName": {
                  "value": "0x4d9e...3596",
                  "source": "ADDRESS"
                },
                "farcasterProfile": {
                  "username": "starit",
                  "fid": 10692,
                  "metadata": {
                    "imageUrl": "https://imagedelivery.net/BXluQx4ige9GuW0Ia56BHw/a27eb6ca-68ce-4073-19a5-d4cb370d4d00/original",
                    "warpcast": "https://warpcast.com/starit"
                  }
                }
              }
            }
          }
        ]
      }
    }
  }
}

Example Use Case: Historical Price​

Returns the price of a token at a specific timestamp.

Try it now
Example Variables​
{
  "address": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
  "chainId": 8453,
}

Example Query​
query TokenPriceData($address: Address!, $chainId: Int!) {
  fungibleTokenV2(address: $address, chainId: $chainId) {
    # Basic token information
    address
    symbol
    name
    decimals
    imageUrlV2

    # Historical price by timestamp
    priceData {
      historicalPrice(timestamp: 1742262500000) {
        timestamp
        price
      }
    }
  }
}

Response​
{
  "data": {
    "fungibleTokenV2": {
      "address": "0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd",
      "symbol": "27 mgas/s",
      "name": "27 mgas/s",
      "decimals": 18,
      "imageUrlV2": "https://storage.googleapis.com/zapper-fi-assets/tokens/base/0xbe19c96f5deec29a91ca84e0d038d4bb01d098cd.png",
      "priceData": {
        "historicalPrice": {
          "timestamp": 1742227200000,
          "price": 0.00000626961364413425
        }
      }
    }
  }
}

fungibleTokenBatchV2​

Takes an array of token inputs (address and chainId pairs) and returns detailed information for multiple tokens in a single request. Returns the same data structure as fungibleToken but for multiple tokens at once.

Try it now
Example Variables​
{
  "tokens": [
    {
      "address": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",
      "chainId": 8453
    },
    {
      "address": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
      "chainId": 1
    },
    {
      "address": "0x00ef6220b7e28e890a5a265d82589e072564cc57",
      "chainId": 8453
    }
  ]
}

Example Query​
query FungibleTokenBatchV2($tokens: [FungibleTokenInputV2!]!) {
  fungibleTokenBatchV2(tokens: $tokens) {
    address
    symbol
    name
    decimals
    imageUrlV2
    priceData {
      price
      priceChange5m
      priceChange1h
      priceChange24h
      volume24h
      totalGasTokenLiquidity
      totalLiquidity
    }
  }
}

Arguments​
Argument	Description	Type	Required
address	Token contract address	Address!	Yes
chainId	Chain ID where the token exists	Int!	Yes
currency	Price currency (USD/ETH/BTC)	Currency!	Yes
timeFrame	Time interval for price data	TimeFrame!	Yes
first	Number of holders to fetch	Float!	Yes
Fields​
Field	Description	Type
id	Unique identifier for the token	ID!
address	Contract address	Address!
name	Token name	String!
symbol	Token symbol	String!
decimals	Number of decimals	Int!
totalSupply	Total supply of the token	String
credibility	Token credibility score	Float
rank	Token rank	Int
securityRisk	Security risk assessment	FungibleTokenSecurityRisk
isHoldersSupported	Whether holder data is available	Boolean!
imageUrl	Token logo URL	String!
priceData	Detailed onchain market data	PriceData
isVerified	Token verification status	Boolean!
priceData Fields​
Field	Description	Type
price	Current token price	Float!
marketCap	Market capitalization	Float
totalLiquidity	Total liquidity across all pairs	Float!
totalGasTokenLiquidity	Native token liquidity	Float!
priceChange5m	5-minute price change percentage	Float
priceChange1h	1-hour price change percentage	Float
priceChange24h	24-hour price change percentage	Float
priceTicks	Historical price data points	[PriceTick!]!
historicalPrice	Price at a given timestamp	[HistoricalPrice!]!
Enums​
enum TimeFrame {
  HOUR
  DAY
  WEEK
  MONTH
  YEAR
}

enum Currency {
  USD
  EUR
  GBP
  CAD
  CNY
  KRW
  JPY
  RUB
  AUD
  NZD
  CHF
  SGD
  INR
  BRL
  ETH
  BTC
  HKD
  SEK
  NOK
  MXN
  TRY
}

Copy page for LLMsToken Rankings

Get a ranked list of tokens based on swap activity and velocity of adoption across a user's network - updating in real-time as onchain activity happens. Optionally provide a farcaster FID for rankings tailored to a farcaster user's social graph.

tokenRanking​

Returns a paginated list of tokens. Supports pagination and optional tailoring by providing a farcaster ID.

Token trading metrics (buy count, buyer count)
Real-time price data integration
Farcaster user personalization capabilities
Paginated results with cursor-based navigation
Cross-chain token rankings
Example Use Case: Top Trending Tokens​

Get the most active tokens based on onchain activity, emphasized for a farcaster user.

Try it now
Example Variables​
{
  "first": 10,
  "after": null,
  "fid": 954583
}

Example Query​
query TokenRanking($first: Int, $after: String, $fid: Int) {
  tokenRanking(first: $first, after: $after, fid: $fid) {
    pageInfo {
      hasPreviousPage
      hasNextPage
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        id
        chainId
        tokenAddress
        token {
          address
          name
          symbol
          priceData {
            price
          }
        }
        buyCount
        buyerCount
        buyerCount24h
      }
    }
  }
}

Example Response​
{
  "data": {
    "tokenRanking": {
      "pageInfo": {
        "hasPreviousPage": false,
        "hasNextPage": true,
        "startCursor": null,
        "endCursor": "Tmpoak9EWmlNR1JqT0RJeFpHVTNOekUzTTJWbU56azVmREV3"
      },
      "edges": [
        {
          "cursor": "NjhjODZiMGRjODIxZGU3NzE3M2VmNzk5fDEw",
          "node": {
            "id": "RmFyY2FzdGVyVG9rZW5GZWVkSXRlbS0xOjB4YzUwNjczZWRiM2E3Yjk0ZThjYWQ4YTdkNGUwY2Q2ODg2NGUzM2VkZg==",
            "chainId": 1,
            "tokenAddress": "0xc50673edb3a7b94e8cad8a7d4e0cd68864e33edf",
            "token": {
              "address": "0xc50673edb3a7b94e8cad8a7d4e0cd68864e33edf",
              "name": "PunkStrategy",
              "symbol": "PNKSTR",
              "priceData": {
                "price": 0.01144183403494625
              }
            },
            "buyCount": 428,
            "buyerCount": 270,
            "buyerCount24h": 270
          }
        },
        {
          "cursor": "NjhjODZiMGRjODIxZGU3NzE3M2VmNzk5fDEw",
          "node": {
            "id": "RmFyY2FzdGVyVG9rZW5GZWVkSXRlbS04NDUzOjB4MDlmYzZlNWFkMWExZTA3NGQwMTdlYzlhNmQ2NzdmMzFmOTdlZmIwNw==",
            "chainId": 8453,
            "tokenAddress": "0x09fc6e5ad1a1e074d017ec9a6d677f31f97efb07",
            "token": {
              "address": "0x09fc6e5ad1a1e074d017ec9a6d677f31f97efb07",
              "name": "ROCKY",
              "symbol": "ROCKY",
              "priceData": {
                "price": 0.000002953452986113082
              }
            },
            "buyCount": 139,
            "buyerCount": 75,
            "buyerCount24h": 75
          }
        },
        {
          "cursor": "NjhjODZiMGRjODIxZGU3NzE3M2VmNzk5fDEw",
          "node": {
            "id": "RmFyY2FzdGVyVG9rZW5GZWVkSXRlbS04NDUzOjB4Yzc1NjJkMDUzNmQzYmY1YTkyODY1YWMyMjA2MmEyODkzZTQ1Y2IwNw==",
            "chainId": 8453,
            "tokenAddress": "0xc7562d0536d3bf5a92865ac22062a2893e45cb07",
            "token": {
              "address": "0xc7562d0536d3bf5a92865ac22062a2893e45cb07",
              "name": "Siyana",
              "symbol": "SYYN",
              "priceData": {
                "price": 0.0000016300402490506471
              }
            },
            "buyCount": 53,
            "buyerCount": 39,
            "buyerCount24h": 39
          }
        },
        {
          "cursor": "NjhjODZiMGRjODIxZGU3NzE3M2VmNzk5fDEw",
          "node": {
            "id": "RmFyY2FzdGVyVG9rZW5GZWVkSXRlbS04NDUzOjB4YmVkZTE3YzhiMDUzNTc5MWQxMzFmMGQ2YjYwOTRiOTljZjI3ZWIwNw==",
            "chainId": 8453,
            "tokenAddress": "0xbede17c8b0535791d131f0d6b6094b99cf27eb07",
            "token": {
              "address": "0xbede17c8b0535791d131f0d6b6094b99cf27eb07",
              "name": "likes",
              "symbol": "likes",
              "priceData": {
                "price": 0.000021954556294676207
              }
            },
            "buyCount": 447,
            "buyerCount": 303,
            "buyerCount24h": 303
          }
        }
      ]
    }
  }
}

Arguments​
Argument	Description	Type	Required
first	Number of ranked tokens to fetch (default: 6, max: 20)	Int	No
after	Cursor for pagination	String	No
fid	Customize results by Farcaster ID	Int	No
Fields​
Field	Description	Type
pageInfo	Pagination information	PageInfo!
edges	Array of ranked token results	[FarcasterTokenFeedItemEdge!]!
FarcasterTokenFeedItemEdge Fields​
Field	Description	Type
cursor	Pagination cursor for this item	String!
node	The ranked token data	FarcasterTokenFeedItem!
FarcasterTokenFeedItem Fields​
Field	Description	Type
id	Unique identifier	ID!
chainId	Chain ID where the token exists	Int!
tokenAddress	Token contract address	Address!
token	Detailed token information	FungibleToken
buyCount	Total number of buy transactions	Int
buyerCount	Total number of unique buyers	Int
buyerCount24h	Number of unique buyers in last 24h	Int
PageInfo Fields​
Field	Description	Type
hasPreviousPage	Whether there are previous results	Boolean!
hasNextPage	Whether there are more results	Boolean!
startCursor	Cursor of the first item in results	String
endCursor	Cursor of the last item in results	String
Copy page for LLMs