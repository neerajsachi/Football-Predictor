import { useState, useEffect } from 'react'
import { Button, Card, CardBody, Input, Badge, StatCard, StatRow } from './components'
import { useApi } from './hooks/useApi'
import { showToast } from './utils/toast'
import axios from 'axios'

function App() {
  const [activeTab, setActiveTab] = useState('match')
  const [clubs, setClubs] = useState([])
  
  // Match predictor state
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [matchLoading, setMatchLoading] = useState(false)
  
  // Transfer predictor state
  const [clubName, setClubName] = useState('')
  const [transferPrediction, setTransferPrediction] = useState(null)
  const [transferLoading, setTransferLoading] = useState(false)

  useEffect(() => {
    axios.get('http://localhost:8000/clubs')
      .then(res => setClubs(res.data.clubs))
      .catch(err => console.error('Failed to load clubs', err))
  }, [])

  const handleMatchPredict = async (e) => {
    e.preventDefault()
    if (!homeTeam.trim() || !awayTeam.trim()) {
      showToast('Please select both teams', 'warning')
      return
    }

    if (homeTeam.trim().toLowerCase() === awayTeam.trim().toLowerCase()) {
      showToast('Home and away teams must be different', 'error')
      return
    }

    setMatchLoading(true)
    setPrediction(null)

    try {
      const response = await axios.post('http://localhost:8000/predict-match', {
        home_team: homeTeam,
        away_team: awayTeam
      })
      
      if (response.data.error) {
        showToast(response.data.error, 'error')
      } else {
        setPrediction(response.data.prediction)
      }
    } catch (err) {
      showToast('Failed to fetch prediction', 'error')
    } finally {
      setMatchLoading(false)
    }
  }

  const handleTransferPredict = async (e) => {
    e.preventDefault()
    if (!clubName.trim()) {
      showToast('Please select a club', 'warning')
      return
    }

    setTransferLoading(true)
    setTransferPrediction(null)

    try {
      const response = await axios.post('http://localhost:8000/predict-transfers', {
        club_name: clubName
      })
      setTransferPrediction(response.data)
    } catch (err) {
      showToast('Failed to fetch transfer predictions', 'error')
    } finally {
      setTransferLoading(false)
    }
  }

  const filteredHomeClubs = clubs.filter(club => 
    club.toLowerCase().includes(homeTeam.toLowerCase())
  ).slice(0, 10)

  const filteredAwayClubs = clubs.filter(club => 
    club.toLowerCase().includes(awayTeam.toLowerCase())
  ).slice(0, 10)

  const filteredClubs = clubs.filter(club => 
    club.toLowerCase().includes(clubName.toLowerCase())
  ).slice(0, 10)

  return (
    <div 
      className="min-h-screen py-8 px-4 sm:py-12"
      style={{
        backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('/DvPkMESS.jpg')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-fadeIn">
          <div className="inline-block mb-4">
            <div className="text-8xl mb-4 animate-bounce">⚽</div>
          </div>
          <h1 className="text-5xl sm:text-7xl font-black text-white mb-4 drop-shadow-2xl tracking-tight">
            Football Predictor
          </h1>
          <p className="text-xl sm:text-2xl text-white/90 font-medium">
            AI-Powered Match & Transfer Predictions
          </p>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-3 mb-8 justify-center animate-scaleIn">
          {[
            { id: 'match', label: 'Match Predictor', icon: '⚽' },
            { id: 'transfer', label: 'Transfers', icon: '🔄' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-white text-blue-600 shadow-2xl scale-110'
                  : 'glass text-white hover:bg-white/20 hover:scale-105'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Match Predictor */}
        {activeTab === 'match' && (
          <div className="animate-fadeIn">
            <Card className="glass-strong p-8 mb-8">
              <form onSubmit={handleMatchPredict} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <Input
                    label="Home Team"
                    value={homeTeam}
                    onChange={setHomeTeam}
                    suggestions={filteredHomeClubs}
                    onSelect={setHomeTeam}
                    icon="🏠"
                    placeholder="Search team..."
                  />
                  <Input
                    label="Away Team"
                    value={awayTeam}
                    onChange={setAwayTeam}
                    suggestions={filteredAwayClubs}
                    onSelect={setAwayTeam}
                    icon="✈️"
                    placeholder="Search team..."
                  />
                </div>
                <Button type="submit" variant="primary" size="lg" loading={matchLoading} className="w-full">
                  {matchLoading ? 'Analyzing...' : '🔮 Predict Match'}
                </Button>
              </form>
            </Card>

            {prediction && (
              <div className="space-y-6 animate-scaleIn">
                {/* Score Prediction */}
                <Card className="glass-strong overflow-hidden">
                  <div className="bg-gradient-to-r from-green-500 via-blue-500 to-purple-500 p-8 text-center text-white">
                    <h2 className="text-3xl font-bold mb-4">Match Prediction</h2>
                    <div className="text-7xl font-black mb-4">{prediction.score}</div>
                    {prediction.importance && (
                      <Badge variant="gradient" size="lg" className="bg-white/20">
                        {prediction.importance}
                      </Badge>
                    )}
                  </div>
                </Card>

                {/* Probabilities */}
                <div className="grid md:grid-cols-3 gap-4">
                  <StatCard label={`${homeTeam} Win`} value={prediction.probabilities.home_win} icon="🏠" color="blue" />
                  <StatCard label="Draw" value={prediction.probabilities.draw} icon="🤝" color="yellow" />
                  <StatCard label={`${awayTeam} Win`} value={prediction.probabilities.away_win} icon="✈️" color="red" />
                </div>

                {/* Team Stats */}
                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="glass-strong" gradient hover>
                    <CardBody>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-2xl font-bold text-gray-800">🏠 {homeTeam}</h3>
                        {prediction.stats.home_league_position && (
                          <Badge variant="primary" size="lg">#{prediction.stats.home_league_position}</Badge>
                        )}
                      </div>
                      {prediction.stats.home_manager && (
                        <p className="text-sm text-gray-600 mb-4">👔 {prediction.stats.home_manager}</p>
                      )}
                      {prediction.stats.home_stadium && prediction.stats.home_stadium !== 'Unknown' && (
                        <p className="text-sm text-gray-600 mb-4">🏟️ {prediction.stats.home_stadium}</p>
                      )}
                      <div className="space-y-2">
                        <StatRow label="Predicted Goals" value={prediction.stats.home_goals} highlight />
                        <StatRow label="xG (Expected)" value={prediction.stats.home_xg} />
                        <StatRow label="Avg Goals/Game" value={prediction.stats.home_avg_goals} />
                        <StatRow label="Win Rate" value={`${prediction.stats.home_win_rate}%`} />
                        {prediction.stats.home_form && prediction.stats.home_form.length > 0 && (
                          <div className="flex justify-between items-center py-3">
                            <span className="text-gray-700">Form</span>
                            <span className="text-2xl">
                              {prediction.stats.home_form.map((r, i) => (
                                <span key={i}>{r === 'W' ? '🟢' : r === 'L' ? '🔴' : '🟡'}</span>
                              ))}
                            </span>
                          </div>
                        )}
                      </div>
                    </CardBody>
                  </Card>

                  <Card className="glass-strong" gradient hover>
                    <CardBody>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-2xl font-bold text-gray-800">✈️ {awayTeam}</h3>
                        {prediction.stats.away_league_position && (
                          <Badge variant="danger" size="lg">#{prediction.stats.away_league_position}</Badge>
                        )}
                      </div>
                      {prediction.stats.away_manager && (
                        <p className="text-sm text-gray-600 mb-4">👔 {prediction.stats.away_manager}</p>
                      )}
                      {prediction.stats.away_stadium && prediction.stats.away_stadium !== 'Unknown' && (
                        <p className="text-sm text-gray-600 mb-4">🏟️ {prediction.stats.away_stadium}</p>
                      )}
                      <div className="space-y-2">
                        <StatRow label="Predicted Goals" value={prediction.stats.away_goals} highlight />
                        <StatRow label="xG (Expected)" value={prediction.stats.away_xg} />
                        <StatRow label="Avg Goals/Game" value={prediction.stats.away_avg_goals} />
                        <StatRow label="Win Rate" value={`${prediction.stats.away_win_rate}%`} />
                        {prediction.stats.away_form && prediction.stats.away_form.length > 0 && (
                          <div className="flex justify-between items-center py-3">
                            <span className="text-gray-700">Form</span>
                            <span className="text-2xl">
                              {prediction.stats.away_form.map((r, i) => (
                                <span key={i}>{r === 'W' ? '🟢' : r === 'L' ? '🔴' : '🟡'}</span>
                              ))}
                            </span>
                          </div>
                        )}
                      </div>
                    </CardBody>
                  </Card>
                </div>

                {/* H2H */}
                {prediction.stats.h2h_results && prediction.stats.h2h_results.length > 0 && (
                  <Card className="glass-strong" gradient>
                    <CardBody>
                      <h3 className="text-2xl font-bold text-gray-800 mb-4">🏆 Head-to-Head</h3>
                      <div className="space-y-3">
                        {prediction.stats.h2h_results.map((match, idx) => (
                          <div key={idx} className="bg-white rounded-xl p-4 flex items-center justify-between shadow-md hover:shadow-lg transition-shadow">
                            <span className="font-semibold text-gray-800">{match.result}</span>
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-gray-500">{match.date}</span>
                              <Badge variant={match.winner === 'home' ? 'success' : match.winner === 'away' ? 'danger' : 'default'}>
                                {match.winner === 'home' ? 'W' : match.winner === 'away' ? 'L' : 'D'}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardBody>
                  </Card>
                )}
              </div>
            )}
          </div>
        )}

        {/* Transfer Predictor */}
        {activeTab === 'transfer' && (
          <div className="animate-fadeIn">
            <Card className="glass-strong p-8 mb-8">
              <form onSubmit={handleTransferPredict} className="space-y-6">
                <Input
                  label="Select Club"
                  value={clubName}
                  onChange={setClubName}
                  suggestions={filteredClubs}
                  onSelect={setClubName}
                  icon="⚽"
                  placeholder="Search club..."
                />
                <Button type="submit" variant="secondary" size="lg" loading={transferLoading} className="w-full">
                  {transferLoading ? 'Analyzing...' : '🔄 Predict Transfers'}
                </Button>
              </form>
            </Card>

            {transferPrediction && (
              <div className="space-y-6 animate-scaleIn">
                <Card className="glass-strong overflow-hidden">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-center text-white">
                    <h2 className="text-3xl font-bold">{transferPrediction.club_name}</h2>
                    <p className="text-sm mt-2 opacity-90">Transfer Window Predictions</p>
                  </div>
                </Card>

                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="glass-strong" gradient>
                    <CardBody>
                      <h3 className="text-2xl font-bold text-red-600 mb-4">📤 Transfers Out</h3>
                      {transferPrediction.transfers_out.length > 0 ? (
                        <div className="space-y-3">
                          {transferPrediction.transfers_out.map((transfer, idx) => (
                            <div key={idx} className="bg-white rounded-xl p-4 shadow-md hover:shadow-lg transition-shadow">
                              <div className="font-bold text-gray-800">{transfer.player}</div>
                              <div className="text-sm text-gray-600 mt-2 space-y-1">
                                <div>Position: {transfer.position}</div>
                                <div>Age: {transfer.age} | Value: {transfer.market_value}</div>
                                <div className="text-red-600 font-semibold">→ {transfer.to_club}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-center py-8">No predicted outgoing transfers</p>
                      )}
                    </CardBody>
                  </Card>

                  <Card className="glass-strong" gradient>
                    <CardBody>
                      <h3 className="text-2xl font-bold text-green-600 mb-4">📥 Transfers In</h3>
                      {transferPrediction.transfers_in.length > 0 ? (
                        <div className="space-y-3">
                          {transferPrediction.transfers_in.map((transfer, idx) => (
                            <div key={idx} className="bg-white rounded-xl p-4 shadow-md hover:shadow-lg transition-shadow">
                              <div className="font-bold text-gray-800">{transfer.player}</div>
                              <div className="text-sm text-gray-600 mt-2 space-y-1">
                                <div>Position: {transfer.position}</div>
                                <div>Age: {transfer.age} | Value: {transfer.market_value}</div>
                                <div className="text-green-600 font-semibold">← {transfer.from_club}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-center py-8">No predicted incoming transfers</p>
                      )}
                    </CardBody>
                  </Card>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
