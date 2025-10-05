import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import Sidebar from './components/Sidebar'
import WordTranslator from './components/WordTranslator'
import './App.css'

function App() {
  const [activeFeature, setActiveFeature] = useState('vocabulary')

  return (
    <div className="app">
      <Sidebar activeFeature={activeFeature} onFeatureChange={setActiveFeature} />

      <div className="main-content">
        {activeFeature === 'vocabulary' && (
          <VocabularyPlayer />
        )}

        {activeFeature === 'translator' && (
          <WordTranslator />
        )}
      </div>
    </div>
  )
}

function VocabularyPlayer() {
  const [vocabulary, setVocabulary] = useState([])
  const [currentIndex, setCurrentIndex] = useState(2)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isAutoPlay, setIsAutoPlay] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentAudioType, setCurrentAudioType] = useState(null)
  const [germanSpeed, setGermanSpeed] = useState(0.75)
  const audioRef = useRef(null)
  const autoPlayRef = useRef(false)

  // Fetch vocabulary data on component mount
  useEffect(() => {
    fetchVocabulary()
  }, [])

  const fetchVocabulary = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/vocabulary')
      setVocabulary(response.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to load vocabulary data')
      setLoading(false)
      console.error('Error fetching vocabulary:', err)
    }
  }

  const playAudio = async (index, audioType, playbackSpeed = 1.0) => {
    try {
      setCurrentAudioType(audioType)
      const audioUrl = `http://localhost:8000/api/audio/${index}/${audioType}`

      // Check if audio file exists first
      const response = await fetch(audioUrl, { method: 'HEAD' })
      if (!response.ok) {
        console.log(`Audio file not found: ${audioType} for index ${index}`)
        setCurrentAudioType(null)
        return
      }

      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }

      const audio = new Audio(audioUrl)
      audio.playbackRate = playbackSpeed
      audioRef.current = audio

      return new Promise((resolve, reject) => {
        audio.onended = () => {
          setCurrentAudioType(null)
          resolve()
        }
        audio.onerror = (err) => {
          console.error(`Error playing ${audioType}:`, err)
          setCurrentAudioType(null)
          resolve() // Continue even if audio fails
        }
        audio.play().catch(err => {
          console.error(`Error playing ${audioType}:`, err)
          setCurrentAudioType(null)
          resolve()
        })
      })
    } catch (err) {
      console.error('Error in playAudio:', err)
      setCurrentAudioType(null)
    }
  }

  const playSequence = async () => {
    if (currentIndex >= vocabulary.length) {
      setIsAutoPlay(false)
      autoPlayRef.current = false
      return
    }

    setIsPlaying(true)
    const item = vocabulary[currentIndex]

    try {
      // Play in sequence: German word → English word → German sentence (slow) → English sentence
      await playAudio(item.index, 'german_word')
      await new Promise(resolve => setTimeout(resolve, 500))

      await playAudio(item.index, 'english_word')
      await new Promise(resolve => setTimeout(resolve, 500))

      await playAudio(item.index, 'german_sentence', germanSpeed)
      await new Promise(resolve => setTimeout(resolve, 500))

      await playAudio(item.index, 'english_sentence')
      await new Promise(resolve => setTimeout(resolve, 1000))

    } catch (err) {
      console.error('Error playing sequence:', err)
    } finally {
      setIsPlaying(false)
      setCurrentAudioType(null)

      // If autoplay is enabled, move to next word
      if (autoPlayRef.current && currentIndex < vocabulary.length - 1) {
        setCurrentIndex(currentIndex + 1)
      } else if (autoPlayRef.current && currentIndex >= vocabulary.length - 1) {
        setIsAutoPlay(false)
        autoPlayRef.current = false
      }
    }
  }

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setIsPlaying(false)
    setIsAutoPlay(false)
    autoPlayRef.current = false
    setCurrentAudioType(null)
  }

  const toggleAutoPlay = () => {
    const newAutoPlayState = !isAutoPlay
    setIsAutoPlay(newAutoPlayState)
    autoPlayRef.current = newAutoPlayState

    if (newAutoPlayState && !isPlaying) {
      playSequence()
    }
  }

  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      stopAudio()
      setCurrentIndex(currentIndex + 1)
    }
  }

  const handlePrevious = () => {
    if (currentIndex > 0) {
      stopAudio()
      setCurrentIndex(currentIndex - 1)
    }
  }

  // Effect to trigger playback when index changes during autoplay
  useEffect(() => {
    if (autoPlayRef.current && !isPlaying && currentIndex < vocabulary.length) {
      playSequence()
    }
  }, [currentIndex])

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading vocabulary...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">{error}</div>
      </div>
    )
  }

  if (vocabulary.length === 0) {
    return (
      <div className="container">
        <div className="error">No vocabulary data found</div>
      </div>
    )
  }

  const currentItem = vocabulary[currentIndex]

  return (
    <div className="container">
      <header className="header">
        <h1>🇩🇪 German Vocabulary Player</h1>
        <p className="subtitle">Learn German words and sentences with audio</p>
      </header>

      <div className="vocab-card">
        <div className="progress-info">
          <span className="index-badge">
            {currentIndex + 1} / {vocabulary.length}
          </span>
        </div>

        <div className="vocab-content">
          <div className="word-section">
            <div className="word-item german">
              <span className="label">German</span>
              <h2 className={currentAudioType === 'german_word' ? 'playing' : ''}>
                {currentItem.german_word}
              </h2>
            </div>
            <div className="word-item english">
              <span className="label">English</span>
              <h2 className={currentAudioType === 'english_word' ? 'playing' : ''}>
                {currentItem.english_word}
              </h2>
            </div>
          </div>

          <div className="sentence-section">
            <div className="sentence-item">
              <span className="label">German Sentence {germanSpeed < 1 && `(${germanSpeed}x speed)`}</span>
              <p className={currentAudioType === 'german_sentence' ? 'playing' : ''}>
                {currentItem.german_sentence}
              </p>
            </div>
            <div className="sentence-item">
              <span className="label">English Sentence</span>
              <p className={currentAudioType === 'english_sentence' ? 'playing' : ''}>
                {currentItem.english_sentence}
              </p>
            </div>
          </div>
        </div>

        <div className="controls">
          <button
            className="btn btn-secondary"
            onClick={handlePrevious}
            disabled={currentIndex === 0 || isPlaying}
          >
            ← Previous
          </button>

          <button
            className={`btn btn-primary ${isPlaying ? 'playing' : ''}`}
            onClick={isPlaying ? stopAudio : playSequence}
            disabled={!currentItem}
          >
            {isPlaying ? '⏸ Stop' : '▶ Play'}
          </button>

          <button
            className="btn btn-secondary"
            onClick={handleNext}
            disabled={currentIndex === vocabulary.length - 1 || isPlaying}
          >
            Next →
          </button>
        </div>

        <div className="autoplay-controls">
          <button
            className={`btn btn-autoplay ${isAutoPlay ? 'active' : ''}`}
            onClick={toggleAutoPlay}
          >
            {isAutoPlay ? '⏹ Stop AutoPlay' : '🔄 Start AutoPlay'}
          </button>
        </div>

        <div className="speed-controls">
          <label htmlFor="german-speed">German Sentence Speed: {germanSpeed}x</label>
          <input
            id="german-speed"
            type="range"
            min="0.5"
            max="1.0"
            step="0.05"
            value={germanSpeed}
            onChange={(e) => setGermanSpeed(parseFloat(e.target.value))}
            disabled={isPlaying}
          />
          <div className="speed-labels">
            <span>0.5x (Slower)</span>
            <span>1.0x (Normal)</span>
          </div>
        </div>
      </div>

      <footer className="footer">
        <p>Order: German word → English word → German sentence (slow) → English sentence</p>
        {isAutoPlay && <p className="autoplay-status">🔄 AutoPlay is ON - Playing continuously...</p>}
      </footer>
    </div>
  )
}

export default App
