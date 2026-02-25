import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [activeTab, setActiveTab] = useState('match')
  
  // Match predictor state
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [displayHomeTeam, setDisplayHomeTeam] = useState('')
  const [displayAwayTeam, setDisplayAwayTeam] = useState('')
  const [clubs, setClubs] = useState([])
  const [homeFilteredClubs, setHomeFilteredClubs] = useState([])
  const [awayFilteredClubs, setAwayFilteredClubs] = useState([])
  const [showHomeDropdown, setShowHomeDropdown] = useState(false)
  const [showAwayDropdown, setShowAwayDropdown] = useState(false)

  // Transfer predictor state
  const [clubName, setClubName] = useState('')
  const [transferPrediction, setTransferPrediction] = useState(null)
  const [transferLoading, setTransferLoading] = useState(false)
  const [transferError, setTransferError] = useState('')
  const [clubFilteredClubs, setClubFilteredClubs] = useState([])
  const [showClubDropdown, setShowClubDropdown] = useState(false)

  useEffect(() => {
    axios.get('http://localhost:8000/clubs')
      .then(res => setClubs(res.data.clubs))
      .catch(err => console.error('Failed to load clubs', err))
  }, [])

  const handleHomeTeamChange = (value) => {
    setHomeTeam(value)
    if (value.length > 0) {
      const filtered = clubs.filter(club => 
        club.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 10)
      setHomeFilteredClubs(filtered)
      setShowHomeDropdown(true)
    } else {
      setShowHomeDropdown(false)
    }
  }

  const handleAwayTeamChange = (value) => {
    setAwayTeam(value)
    if (value.length > 0) {
      const filtered = clubs.filter(club => 
        club.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 10)
      setAwayFilteredClubs(filtered)
      setShowAwayDropdown(true)
    } else {
      setShowAwayDropdown(false)
    }
  }

  const handleClubNameChange = (value) => {
    setClubName(value)
    if (value.length > 0) {
      const filtered = clubs.filter(club => 
        club.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 10)
      setClubFilteredClubs(filtered)
      setShowClubDropdown(true)
    } else {
      setShowClubDropdown(false)
    }
  }

  const selectHomeTeam = (club) => {
    setHomeTeam(club)
    setShowHomeDropdown(false)
  }

  const selectAwayTeam = (club) => {
    setAwayTeam(club)
    setShowAwayDropdown(false)
  }

  const selectClub = (club) => {
    setClubName(club)
    setShowClubDropdown(false)
  }

  const handlePredict = async (e) => {
    e.preventDefault()
    if (!homeTeam.trim() || !awayTeam.trim()) return

    // Validate teams are different
    if (homeTeam.trim().toLowerCase() === awayTeam.trim().toLowerCase()) {
      // Show toast notification
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 animate-fadeIn'
      toast.textContent = '⚠️ Home and away teams must be different'
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.style.opacity = '0'
        toast.style.transition = 'opacity 0.3s'
        setTimeout(() => toast.remove(), 300)
      }, 3000)
      return
    }

    setLoading(true)
    setError('')
    setPrediction(null)

    try {
      const response = await axios.post('http://localhost:8000/predict-match', {
        home_team: homeTeam,
        away_team: awayTeam
      })
      if (response.data.error) {
        // Show toast notification for errors
        const toast = document.createElement('div')
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 animate-fadeIn'
        toast.textContent = `⚠️ ${response.data.error}`
        document.body.appendChild(toast)
        setTimeout(() => {
          toast.style.opacity = '0'
          toast.style.transition = 'opacity 0.3s'
          setTimeout(() => toast.remove(), 300)
        }, 3000)
      } else {
        setPrediction(response.data.prediction)
        setDisplayHomeTeam(homeTeam)
        setDisplayAwayTeam(awayTeam)
      }
    } catch (err) {
      setError('Failed to fetch prediction. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleTransferPredict = async (e) => {
    e.preventDefault()
    if (!clubName.trim()) return

    setTransferLoading(true)
    setTransferError('')
    setTransferPrediction(null)

    try {
      const response = await axios.post('http://localhost:8000/predict-transfers', {
        club_name: clubName
      })
      setTransferPrediction(response.data)
    } catch (err) {
      setTransferError('Failed to fetch transfer predictions.')
    } finally {
      setTransferLoading(false)
    }
  }

  const getWinnerDisplay = (winner) => {
    if (winner === 'home') return displayHomeTeam
    if (winner === 'away') return displayAwayTeam
    return 'Draw'
  }

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg">
            ⚽ Football Predictor
          </h1>
          <p className="text-xl text-white/90">
            AI-powered predictions for matches and transfers
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('match')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition ${
              activeTab === 'match'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            Match Predictor
          </button>
          <button
            onClick={() => setActiveTab('transfer')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition ${
              activeTab === 'transfer'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            Transfer Predictor
          </button>
        </div>

        {/* Match Predictor Tab */}
        {activeTab === 'match' && (
          <div className="bg-white/95 backdrop-blur rounded-3xl shadow-2xl p-8 mb-8">
            <form onSubmit={handlePredict} className="mb-8">
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="relative">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Home Team</label>
                  <input
                    type="text"
                    value={homeTeam}
                    onChange={(e) => handleHomeTeamChange(e.target.value)}
                    onFocus={() => homeTeam && setShowHomeDropdown(true)}
                    placeholder=""
                    className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition"
                  />
                  {showHomeDropdown && homeFilteredClubs.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                      {homeFilteredClubs.map((club, idx) => (
                        <div
                          key={idx}
                          onClick={() => selectHomeTeam(club)}
                          className="px-4 py-3 hover:bg-primary hover:text-white cursor-pointer transition"
                        >
                          {club}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="relative">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Away Team</label>
                  <input
                    type="text"
                    value={awayTeam}
                    onChange={(e) => handleAwayTeamChange(e.target.value)}
                    onFocus={() => awayTeam && setShowAwayDropdown(true)}
                    placeholder=""
                    className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition"
                  />
                  {showAwayDropdown && awayFilteredClubs.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                      {awayFilteredClubs.map((club, idx) => (
                        <div
                          key={idx}
                          onClick={() => selectAwayTeam(club)}
                          className="px-4 py-3 hover:bg-primary hover:text-white cursor-pointer transition"
                        >
                          {club}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-xl hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 disabled:hover:scale-100"
              >
                {loading ? 'Predicting...' : 'Predict Match'}
              </button>
            </form>

            {error && (
              <div className="bg-red-100 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-lg mb-6 animate-fadeIn">
                <p className="font-semibold">Error</p>
                <p>{error}</p>
              </div>
            )}

            {prediction && (
              <div className="space-y-6 animate-fadeIn">
                <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-2xl p-8 text-center">
                  <h2 className="text-3xl font-bold mb-4">Match Prediction</h2>
                  <div className="text-6xl font-bold mb-4">{prediction.score}</div>
                  {prediction.importance && (
                    <div className="mt-4">
                      <span className="px-4 py-2 rounded-lg font-semibold bg-purple-600">
                        {prediction.importance}
                      </span>
                    </div>
                  )}
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 rounded-xl p-6 text-center">
                    <div className="text-4xl font-bold text-blue-600 mb-2">{prediction.probabilities.home_win}</div>
                    <div className="text-gray-700 font-semibold">{displayHomeTeam} Win</div>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-6 text-center">
                    <div className="text-4xl font-bold text-gray-600 mb-2">{prediction.probabilities.draw}</div>
                    <div className="text-gray-700 font-semibold">Draw</div>
                  </div>
                  <div className="bg-red-50 rounded-xl p-6 text-center">
                    <div className="text-4xl font-bold text-red-600 mb-2">{prediction.probabilities.away_win}</div>
                    <div className="text-gray-700 font-semibold">{displayAwayTeam} Win</div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-2">
                      ⚽ {displayHomeTeam}
                      {prediction.stats.home_league_position && (
                        <span className="ml-2 text-sm bg-blue-600 text-white px-2 py-1 rounded">#{prediction.stats.home_league_position}</span>
                      )}
                    </h3>
                    {prediction.stats.home_manager && (
                      <p className="text-sm text-gray-600 mb-2">👔 Manager: {prediction.stats.home_manager}</p>
                    )}
                    {prediction.stats.home_stadium && prediction.stats.home_stadium !== 'Unknown' && (
                      <p className="text-sm text-gray-600 mb-4">🏟️ Stadium: {prediction.stats.home_stadium}</p>
                    )}
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-700">Predicted Goals:</span>
                        <span className="font-bold text-blue-600">{prediction.stats.home_goals}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">xG (Expected):</span>
                        <span className="font-bold text-blue-500">{prediction.stats.home_xg}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Goals/Game:</span>
                        <span className="font-bold">{prediction.stats.home_avg_goals}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Conceded:</span>
                        <span className="font-bold text-red-500">{prediction.stats.home_conceded_avg}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Shots:</span>
                        <span className="font-bold">{prediction.stats.home_shots}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Shots on Target:</span>
                        <span className="font-bold">{prediction.stats.home_shots_on_target}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Corners:</span>
                        <span className="font-bold">{prediction.stats.home_corners}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Win Rate:</span>
                        <span className="font-bold text-green-600">{prediction.stats.home_win_rate}%</span>
                      </div>
                      {prediction.stats.home_form && prediction.stats.home_form.length > 0 && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-700">Form:</span>
                          <span className="text-2xl">
                            {prediction.stats.home_form.map((result, i) => (
                              <span key={i}>
                                {result === 'W' ? '🟢' : result === 'L' ? '🔴' : '🟡'}
                              </span>
                            ))}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Likely Scorers:</p>
                      <ul className="space-y-1">
                        {prediction.likely_scorers.home.map((player, i) => (
                          <li key={i} className="text-gray-600 flex items-center gap-2">
                            <span className="text-blue-500">⚽</span> {player}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-2">
                      ⚽ {displayAwayTeam}
                      {prediction.stats.away_league_position && (
                        <span className="ml-2 text-sm bg-red-600 text-white px-2 py-1 rounded">#{prediction.stats.away_league_position}</span>
                      )}
                    </h3>
                    {prediction.stats.away_manager && (
                      <p className="text-sm text-gray-600 mb-2">👔 Manager: {prediction.stats.away_manager}</p>
                    )}
                    {prediction.stats.away_stadium && prediction.stats.away_stadium !== 'Unknown' && (
                      <p className="text-sm text-gray-600 mb-4">🏟️ Stadium: {prediction.stats.away_stadium}</p>
                    )}
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-700">Predicted Goals:</span>
                        <span className="font-bold text-red-600">{prediction.stats.away_goals}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">xG (Expected):</span>
                        <span className="font-bold text-red-500">{prediction.stats.away_xg}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Goals/Game:</span>
                        <span className="font-bold">{prediction.stats.away_avg_goals}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Conceded:</span>
                        <span className="font-bold text-red-500">{prediction.stats.away_conceded_avg}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Shots:</span>
                        <span className="font-bold">{prediction.stats.away_shots}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Shots on Target:</span>
                        <span className="font-bold">{prediction.stats.away_shots_on_target}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Corners:</span>
                        <span className="font-bold">{prediction.stats.away_corners}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Win Rate:</span>
                        <span className="font-bold text-green-600">{prediction.stats.away_win_rate}%</span>
                      </div>
                      {prediction.stats.away_form && prediction.stats.away_form.length > 0 && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-700">Form:</span>
                          <span className="text-2xl">
                            {prediction.stats.away_form.map((result, i) => (
                              <span key={i}>
                                {result === 'W' ? '🟢' : result === 'L' ? '🔴' : '🟡'}
                              </span>
                            ))}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Likely Scorers:</p>
                      <ul className="space-y-1">
                        {prediction.likely_scorers.away.map((player, i) => (
                          <li key={i} className="text-gray-600 flex items-center gap-2">
                            <span className="text-red-500">⚽</span> {player}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Head-to-Head Results */}
                {prediction.stats.h2h_results && prediction.stats.h2h_results.length > 0 && (
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-4">🏆 Last 3 Head-to-Head</h3>
                    <div className="space-y-3">
                      {prediction.stats.h2h_results.map((match, idx) => (
                        <div key={idx} className="bg-white rounded-lg p-3 flex items-center justify-between">
                          <span className="text-gray-700 font-medium">{match.result}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">{match.date}</span>
                            {match.winner === 'home' && <span className="text-blue-600 font-bold">W</span>}
                            {match.winner === 'away' && <span className="text-red-600 font-bold">L</span>}
                            {match.winner === 'draw' && <span className="text-gray-600 font-bold">D</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Transfer Predictor Tab */}
        {activeTab === 'transfer' && (
          <div className="bg-white/95 backdrop-blur rounded-3xl shadow-2xl p-8 mb-8">
            <form onSubmit={handleTransferPredict} className="mb-8">
              <div className="relative mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Club Name</label>
                <input
                  type="text"
                  value={clubName}
                  onChange={(e) => handleClubNameChange(e.target.value)}
                  onFocus={() => clubName && setShowClubDropdown(true)}
                  placeholder=""
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition"
                />
                {showClubDropdown && clubFilteredClubs.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                    {clubFilteredClubs.map((club, idx) => (
                      <div
                        key={idx}
                        onClick={() => selectClub(club)}
                        className="px-4 py-3 hover:bg-primary hover:text-white cursor-pointer transition"
                      >
                        {club}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <button
                type="submit"
                disabled={transferLoading}
                className="w-full px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 disabled:hover:scale-100"
              >
                {transferLoading ? 'Predicting...' : 'Predict Transfers'}
              </button>
            </form>

            {transferError && (
              <div className="bg-red-100 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-lg mb-6 animate-fadeIn">
                <p className="font-semibold">Error</p>
                <p>{transferError}</p>
              </div>
            )}

            {transferPrediction && (
              <div className="space-y-6 animate-fadeIn">
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl p-6 text-center">
                  <h2 className="text-3xl font-bold">Transfer Predictions</h2>
                  <p className="text-xl mt-2">{transferPrediction.club_name}</p>
                  <p className="text-sm mt-1 opacity-90">Next 5 Years (2025-2030)</p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Transfers Out */}
                  <div className="bg-red-50 rounded-xl p-6">
                    <h3 className="text-2xl font-bold text-red-600 mb-4">📤 Transfers Out</h3>
                    {transferPrediction.transfers_out.length > 0 ? (
                      <div className="space-y-3">
                        {transferPrediction.transfers_out.map((transfer, idx) => (
                          <div key={idx} className="bg-white rounded-lg p-4 shadow">
                            <div className="font-bold text-gray-800">{transfer.player}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              <div>Position: {transfer.position}</div>
                              <div>Age: {transfer.age} | Value: {transfer.market_value}</div>
                              <div className="text-red-600 font-semibold">→ {transfer.to_club}</div>
                              <div className="text-xs text-gray-500 mt-1">Probability: {transfer.probability}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No predicted outgoing transfers</p>
                    )}
                  </div>

                  {/* Transfers In */}
                  <div className="bg-green-50 rounded-xl p-6">
                    <h3 className="text-2xl font-bold text-green-600 mb-4">📥 Transfers In</h3>
                    {transferPrediction.transfers_in.length > 0 ? (
                      <div className="space-y-3">
                        {transferPrediction.transfers_in.map((transfer, idx) => (
                          <div key={idx} className="bg-white rounded-lg p-4 shadow">
                            <div className="font-bold text-gray-800">{transfer.player}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              <div>Position: {transfer.position}</div>
                              <div>Age: {transfer.age} | Value: {transfer.market_value}</div>
                              <div className="text-green-600 font-semibold">← {transfer.from_club}</div>
                              <div className="text-xs text-gray-500 mt-1">Probability: {transfer.probability}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No predicted incoming transfers</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="text-center text-white/80 text-sm">
          <p>⚡ Powered by AI & Machine Learning</p>
        </div>
      </div>
    </div>
  )
}

export default App
