import React from 'react'
import { useNavigate } from 'react-router-dom'
import { NavBar, MiniMenu, type MenuOption } from '@/components/layout'

const scoringExamples = [
  {
    actual: '2–1',
    prediction: '2–1',
    points: 100,
    breakdown: 'Exact score',
  },
  {
    actual: '2–1',
    prediction: '2–0',
    points: 65,
    breakdown: 'Correct result (50) + home goals (15)',
  },
  {
    actual: '2–1',
    prediction: '3–0',
    points: 50,
    breakdown: 'Correct result only (home win)',
  },
  {
    actual: '2–1',
    prediction: '1–1',
    points: 15,
    breakdown: 'Away goals only (15)',
  },
  {
    actual: '1–1',
    prediction: '0–0',
    points: 50,
    breakdown: 'Correct result only (draw)',
  },
  {
    actual: '2–1',
    prediction: '1–2',
    points: 0,
    breakdown: 'Wrong result and wrong goals',
  },
]

export const FaqPage: React.FC = () => {
  const navigate = useNavigate()

  const handleMenuOptionChange = (option: MenuOption) => {
    if (option === 'dashboard') {
      navigate('/dashboard')
    } else if (option === 'scorecard') {
      navigate('/scorecard')
    }
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <MiniMenu activeOption="faq" onOptionChange={handleMenuOptionChange} />

        <div className="mt-6 space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-neutral-DEFAULT">FAQ — Scoring</h1>
            <p className="mt-2 text-sm text-neutral-DEFAULT/70">
              How points are calculated for each match prediction on Predico.
            </p>
          </div>

          <section className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">Overview</h2>
            <p className="mt-3 text-sm text-neutral-DEFAULT/80 leading-relaxed">
              Before each match kicks off, you enter a predicted score (home goals and away goals). After the
              final whistle, your prediction is compared to the actual result. You earn points from up to three
              categories below. Categories <strong>add together</strong>, except when you get the exact score — then
              you receive a flat <strong>100 points</strong> and no other bonuses for that match.
            </p>
          </section>

          <section className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">Point categories</h2>
            <ul className="mt-4 space-y-4">
              <li className="flex gap-3">
                <span className="flex-shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary-medium/15 text-primary-dark font-bold text-sm">
                  100
                </span>
                <div>
                  <p className="font-medium text-neutral-DEFAULT">Exact score</p>
                  <p className="mt-1 text-sm text-neutral-DEFAULT/70">
                    Both the home and away goals match the real result exactly (e.g. you predicted 2–1 and the
                    match finished 2–1). This replaces all other bonuses for that game.
                  </p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary-medium/15 text-primary-dark font-bold text-sm">
                  50
                </span>
                <div>
                  <p className="font-medium text-neutral-DEFAULT">Correct result</p>
                  <p className="mt-1 text-sm text-neutral-DEFAULT/70">
                    You picked the right outcome: home win, away win, or draw — even if the exact score was wrong.
                    Example: actual 2–1 (home win), you predicted 3–0 (also home win).
                  </p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary-medium/15 text-primary-dark font-bold text-sm">
                  15
                </span>
                <div>
                  <p className="font-medium text-neutral-DEFAULT">Correct home team goals</p>
                  <p className="mt-1 text-sm text-neutral-DEFAULT/70">
                    The number of goals you predicted for the home team matches the actual number, regardless of
                    the away score.
                  </p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary-medium/15 text-primary-dark font-bold text-sm">
                  15
                </span>
                <div>
                  <p className="font-medium text-neutral-DEFAULT">Correct away team goals</p>
                  <p className="mt-1 text-sm text-neutral-DEFAULT/70">
                    The number of goals you predicted for the away team matches the actual number, regardless of
                    the home score.
                  </p>
                </div>
              </li>
            </ul>
          </section>

          <section className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6 overflow-hidden">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">Examples</h2>
            <p className="mt-2 text-sm text-neutral-DEFAULT/70 mb-4">
              Actual result used in every row below: varies per row (see &quot;Actual&quot; column).
            </p>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-DEFAULT/10 text-sm">
                <thead>
                  <tr>
                    <th className="px-3 py-2 text-left font-semibold text-neutral-DEFAULT/70">Actual</th>
                    <th className="px-3 py-2 text-left font-semibold text-neutral-DEFAULT/70">Your prediction</th>
                    <th className="px-3 py-2 text-right font-semibold text-neutral-DEFAULT/70">Points</th>
                    <th className="px-3 py-2 text-left font-semibold text-neutral-DEFAULT/70">Why</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-DEFAULT/10">
                  {scoringExamples.map((row) => (
                    <tr key={`${row.actual}-${row.prediction}`}>
                      <td className="px-3 py-3 text-neutral-DEFAULT whitespace-nowrap">{row.actual}</td>
                      <td className="px-3 py-3 text-neutral-DEFAULT whitespace-nowrap">{row.prediction}</td>
                      <td className="px-3 py-3 text-right font-semibold text-neutral-DEFAULT">{row.points}</td>
                      <td className="px-3 py-3 text-neutral-DEFAULT/70">{row.breakdown}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">Leagues &amp; rankings</h2>
            <div className="mt-3 space-y-3 text-sm text-neutral-DEFAULT/80 leading-relaxed">
              <p>
                Your <strong>total score</strong> is the sum of points from all scored matches across the
                tournament. League rankings use this total — every member in a league sees the same standings
                based on overall prediction performance.
              </p>
              <p>
                If two players have the same total score, the higher rank goes to whoever has more{' '}
                <strong>perfect predictions</strong> (exact scores worth 100 points). This tie-break applies
                at every position in the table.
              </p>
              <p>
                Points are calculated automatically after a match is marked finished and the official score is
                entered. Until then, that game contributes 0 points to your total.
              </p>
              <p>
                You can submit or update predictions on the <strong>Scorecard</strong> tab until{' '}
                <strong>one hour before kickoff</strong>. After that deadline, the fixture is locked.
              </p>
            </div>
          </section>

          <section className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">Knockout stage</h2>
            <div className="mt-3 space-y-3 text-sm text-neutral-DEFAULT/80 leading-relaxed">
              <p>
                Knockout matches use the same scoring rules as the group stage, but there is one important
                difference in what counts as the &quot;actual&quot; result.
              </p>
              <p>
                Your prediction is always for the score at the end of{' '}
                <strong>regular time (90 minutes plus stoppage time)</strong> — the standard full-time whistle,
                not extra time or a penalty shootout.
              </p>
              <p>
                When we score your prediction, we compare it to that 90-minute score only. If a knockout match
                goes to extra time or penalties, those goals do <strong>not</strong> change your points. Example:
                if the match is 1–1 after 90 minutes and Team A wins on penalties, the result used for scoring
                is <strong>1–1</strong>, not the shootout outcome.
              </p>
              <p>
                In admin, the knockout winner (who advances) can still be recorded separately when a match is
                decided after extra time or on penalties — that is for the bracket only and does not affect how
                your prediction is scored.
              </p>
            </div>
          </section>

          <section className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">Quick reference</h2>
            <dl className="mt-4 grid gap-3 text-sm">
              <div className="flex justify-between gap-4 border-b border-neutral-DEFAULT/10 pb-2">
                <dt className="text-neutral-DEFAULT/70">Exact score</dt>
                <dd className="font-semibold text-neutral-DEFAULT">100 pts</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-neutral-DEFAULT/10 pb-2">
                <dt className="text-neutral-DEFAULT/70">Correct win / draw / loss</dt>
                <dd className="font-semibold text-neutral-DEFAULT">50 pts</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-neutral-DEFAULT/10 pb-2">
                <dt className="text-neutral-DEFAULT/70">Correct home goals</dt>
                <dd className="font-semibold text-neutral-DEFAULT">15 pts</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-neutral-DEFAULT/70">Correct away goals</dt>
                <dd className="font-semibold text-neutral-DEFAULT">15 pts</dd>
              </div>
            </dl>
          </section>
        </div>
      </div>
    </div>
  )
}
