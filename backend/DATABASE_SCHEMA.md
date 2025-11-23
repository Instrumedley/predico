# Database Schema Documentation

## Overview

This document describes the database schema for the World Cup Predictions platform.

## Entity Relationship Diagram

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│   User   │────────│  Prediction  │────────│   Game   │
└────┬─────┘         └──────────────┘         └────┬─────┘
     │                                              │
     │                                              │
     │         ┌──────────────┐                    │
     │────────│ LeagueMember │                    │
     │         └──────┬───────┘                    │
     │                │                            │
     │         ┌───────▼───────┐                    │
     │         │    League     │                    │
     │         └───────┬───────┘                    │
     │                │                            │
     │         ┌───────▼────────┐                  │
     │         │LeagueInvitation│                  │
     │         └────────────────┘                 │
     │                                              │
┌────▼────┐                                    ┌───▼────┐
│  Team  │                                    │ Stadium│
└────┬───┘                                    └────────┘
     │
     │         ┌──────────────┐
     │────────│  GroupTeam   │────────┐
     │         └──────────────┘        │
     │                                 │
┌────▼────┐                    ┌───────▼────┐
│  Group  │                    │    Round   │
└────┬────┘                    └───────┬────┘
     │                                  │
     │                                  │
     └──────────┬───────────────────────┘
                │
           ┌────▼────┐
           │  Game   │
           └─────────┘
```

## Models

### User
**Table:** `users`

Stores user account information for authentication and profiles.

**Fields:**
- `id` (PK): Integer, auto-increment
- `email`: String, unique, indexed
- `username`: String, unique, indexed
- `hashed_password`: String (bcrypt hash)
- `is_active`: Boolean, default True
- `is_superuser`: Boolean, default False
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- One-to-many with `Prediction`
- One-to-many with `League` (as creator)
- Many-to-many with `League` (via `LeagueMember`)
- One-to-many with `LeagueInvitation` (as inviter and invitee)

---

### Team
**Table:** `teams`

Stores national team information.

**Fields:**
- `id` (PK): Integer, auto-increment
- `name`: String, unique, indexed (e.g., "Brazil", "Argentina")
- `country_code`: String(3), unique, indexed (ISO 3166-1 alpha-3, e.g., "BRA", "ARG")
- `flag_emoji`: String(10), optional (flag emoji for display)
- `fifa_ranking`: Integer, optional (current FIFA ranking)

**Relationships:**
- One-to-many with `Game` (as home_team and away_team)
- Many-to-many with `Group` (via `GroupTeam`)

---

### Stadium
**Table:** `stadiums`

Stores stadium/venue information for matches.

**Fields:**
- `id` (PK): Integer, auto-increment
- `name`: String, indexed
- `city`: String
- `capacity`: Integer, optional

**Relationships:**
- One-to-many with `Game`

---

### Round
**Table:** `rounds`

Stores tournament round/phase information.

**Fields:**
- `id` (PK): Integer, auto-increment
- `name`: String, unique, indexed (e.g., "Group A", "Round of 16", "Final")
- `round_type`: Enum (RoundType), indexed
  - `GROUP_STAGE`
  - `ROUND_OF_16`
  - `QUARTER_FINALS`
  - `SEMI_FINALS`
  - `THIRD_PLACE`
  - `FINAL`
- `order`: Integer, indexed (tournament order: 1=Group Stage, 2=Round of 16, etc.)

**Relationships:**
- One-to-many with `Game`

---

### Group
**Table:** `groups`

Stores group stage group information.

**Fields:**
- `id` (PK): Integer, auto-increment
- `name`: String, unique, indexed (e.g., "Group A", "Group B")

**Relationships:**
- Many-to-many with `Team` (via `GroupTeam`)
- One-to-many with `Game` (only for group stage games)

---

### GroupTeam
**Table:** `group_teams`

Association table linking teams to groups (many-to-many).

**Fields:**
- `id` (PK): Integer, auto-increment
- `group_id` (FK): Integer → `groups.id`, indexed
- `team_id` (FK): Integer → `teams.id`, indexed

**Relationships:**
- Many-to-one with `Group`
- Many-to-one with `Team`

**Important Notes:**
- These records are **historical and permanent** - they are NOT deleted when the group stage ends
- They represent which teams were assigned to which groups during the group stage
- Useful for historical queries, statistics, and displaying group stage results
- When knockout rounds begin, teams advance based on group stage results, but GroupTeam records remain as a permanent record

---

### Game
**Table:** `games`

Stores match/game information.

**Fields:**
- `id` (PK): Integer, auto-increment
- `home_team_id` (FK): Integer → `teams.id`, indexed (one of two teams in the game)
- `away_team_id` (FK): Integer → `teams.id`, indexed (one of two teams in the game)
- `scheduled_at`: DateTime, indexed
- `status`: Enum (GameStatus), indexed
  - `SCHEDULED`
  - `LIVE`
  - `FINISHED`
  - `CANCELLED`
  - `POSTPONED`
- `home_score`: Integer, nullable (set when game finishes)
- `away_score`: Integer, nullable
- `home_penalty_score`: Integer, nullable (for penalty shootouts)
- `away_penalty_score`: Integer, nullable
- `stadium_id` (FK): Integer → `stadiums.id`, nullable, indexed
- `round_id` (FK): Integer → `rounds.id`, indexed
- `group_id` (FK): Integer → `groups.id`, nullable, indexed (only for group stage)
- `is_knockout`: Boolean, default False, indexed
- `match_number`: Integer, optional
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- **Many-to-one with `Team`** (via `home_team_id` and `away_team_id`) - Each game has exactly 2 teams
  - `home_team`: The team playing at home
  - `away_team`: The team playing away
- Many-to-one with `Stadium`
- Many-to-one with `Round`
- Many-to-one with `Group` (optional, for group stage only)
- One-to-many with `Prediction`

**Team-Game Relationship:**
- A `Game` always has exactly 2 teams (home and away)
- A `Team` can participate in multiple games (as home_team or away_team)
- Use `team.home_games` to get games where team is home
- Use `team.away_games` to get games where team is away
- Use `team.all_games` property (or query both) to get all games for a team

**Notes:**
- Group stage games have `group_id` set and `is_knockout=False`
- Knockout games have `group_id=null` and `is_knockout=True`
- Knockout games are created dynamically as the tournament progresses

---

### Prediction
**Table:** `predictions`

Stores user predictions for games.

**Fields:**
- `id` (PK): Integer, auto-increment
- `user_id` (FK): Integer → `users.id`, indexed
- `game_id` (FK): Integer → `games.id`, indexed
- `predicted_home_score`: Integer
- `predicted_away_score`: Integer
- `points`: Integer, default 0, indexed (total points earned)
- `exact_score_points`: Integer, default 0 (points for exact score match)
- `correct_result_points`: Integer, default 0 (points for correct winner/draw)
- `correct_goal_difference_points`: Integer, default 0 (points for correct goal difference)
- `is_calculated`: Boolean, default False, indexed
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- Many-to-one with `User`
- Many-to-one with `Game`

**Constraints:**
- Unique constraint on (`user_id`, `game_id`) - one prediction per user per game

**Scoring Logic:**
Points are calculated after a game finishes:
- Exact score match: Highest points (e.g., 10 points)
- Correct result (winner/draw): Medium points (e.g., 5 points)
- Correct goal difference: Lower points (e.g., 2 points)
- Points breakdown stored for transparency

---

### League
**Table:** `leagues`

Stores private prediction leagues.

**Fields:**
- `id` (PK): Integer, auto-increment
- `name`: String, indexed
- `description`: String, nullable
- `created_by` (FK): Integer → `users.id`, indexed
- `is_private`: Boolean, default True, indexed
- `invite_code`: String, unique, nullable, indexed (for joining via code)
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- Many-to-one with `User` (as creator)
- One-to-many with `LeagueMember`
- One-to-many with `LeagueInvitation`

---

### LeagueMember
**Table:** `league_members`

Association table linking users to leagues with additional metadata (many-to-many).

**Fields:**
- `id` (PK): Integer, auto-increment
- `league_id` (FK): Integer → `leagues.id`, indexed
- `user_id` (FK): Integer → `users.id`, indexed
- `total_points`: Integer, default 0, indexed (league-specific score)
- `joined_at`: DateTime

**Relationships:**
- Many-to-one with `League`
- Many-to-one with `User`

**Constraints:**
- Unique constraint on (`league_id`, `user_id`) - one membership per user per league

**Notes:**
- `total_points` is the sum of all prediction points for games in this league
- Updated when predictions are scored

---

### LeagueInvitation
**Table:** `league_invitations`

Stores league invitation information.

**Fields:**
- `id` (PK): Integer, auto-increment
- `league_id` (FK): Integer → `leagues.id`, indexed
- `inviter_id` (FK): Integer → `users.id`, indexed
- `invitee_id` (FK): Integer → `users.id`, indexed
- `status`: String, default "pending", indexed
  - `pending`: Invitation sent, awaiting response
  - `accepted`: Invitation accepted
  - `rejected`: Invitation rejected
  - `expired`: Invitation expired
- `created_at`: DateTime
- `expires_at`: DateTime, nullable (optional expiration)
- `responded_at`: DateTime, nullable

**Relationships:**
- Many-to-one with `League`
- Many-to-one with `User` (as inviter)
- Many-to-one with `User` (as invitee)

---

## Indexes

### Performance Indexes

The following indexes are created for optimal query performance:

1. **User:**
   - `email` (unique)
   - `username` (unique)

2. **Game:**
   - `scheduled_at` (for querying upcoming games)
   - `status` (for filtering by game status)
   - `round_id` (for querying games by round)
   - `group_id` (for querying group stage games)
   - `is_knockout` (for filtering knockout games)

3. **Prediction:**
   - `user_id` (for user's predictions)
   - `game_id` (for game predictions)
   - `points` (for leaderboard queries)
   - `is_calculated` (for batch processing)
   - Unique: (`user_id`, `game_id`)

4. **LeagueMember:**
   - `league_id` (for league members)
   - `user_id` (for user's leagues)
   - `total_points` (for league leaderboards)
   - Unique: (`league_id`, `user_id`)

5. **LeagueInvitation:**
   - `status` (for filtering pending invitations)
   - `invitee_id` (for user's received invitations)

---

## Key Design Decisions

1. **Separate Round and Group Models:**
   - `Round` handles tournament phases (Group Stage, Round of 16, etc.)
   - `Group` handles specific groups within the group stage (Group A, B, etc.)
   - This allows flexibility for knockout rounds which don't have groups

2. **Prediction Points Breakdown:**
   - Stores detailed point breakdown (exact score, correct result, goal difference)
   - Enables transparency and allows for scoring rule changes without recalculating

3. **League-Specific Scoring:**
   - `LeagueMember.total_points` stores league-specific scores
   - Allows different leagues to have different scoring rules in the future
   - Enables efficient leaderboard queries per league

4. **Game Status Enum:**
   - Tracks game lifecycle (scheduled → live → finished)
   - Enables filtering and prevents predictions after game starts

5. **Invite Code System:**
   - `League.invite_code` allows easy joining via code
   - Alternative to invitation system for public/private leagues

---

## Future Enhancements

Potential additions for future versions:

1. **UserScore Table:**
   - Cache global user scores for performance
   - Updated via triggers or background jobs

2. **PredictionHistory:**
   - Track prediction changes (if users can edit predictions)

3. **Notification System:**
   - Track game start notifications
   - League invitation notifications

4. **Tournament Model:**
   - Support multiple tournaments (not just World Cup)
   - Link games, teams, and rounds to tournaments

