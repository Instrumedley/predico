export interface BracketTeam {
  teamId: number
  countryCode: string
  countryName: string
  flagEmoji?: string | null
}

export interface BracketSlot {
  label?: string
  team?: BracketTeam
}

export interface BracketMatch {
  matchNumber: number
  home: BracketSlot
  away: BracketSlot
  homeScore?: number | null
  awayScore?: number | null
  winnerTeamId?: number | null
  isFinished: boolean
}

export interface BracketSideData {
  roundOf32: BracketMatch[]
  roundOf16: BracketMatch[]
  quarterFinals: BracketMatch[]
  semiFinal: BracketMatch
}

export interface KnockoutBracketData {
  left: BracketSideData
  right: BracketSideData
  final: BracketMatch
  thirdPlace: BracketMatch
  thirdPlaceCombinationKey?: string | null
}

export interface UpdateKnockoutMatchPayload {
  homeScore: number
  awayScore: number
  winnerTeamId: number
}

export interface KnockoutSavePayload extends UpdateKnockoutMatchPayload {
  matchNumber: number
}
