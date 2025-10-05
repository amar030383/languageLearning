import React, { useState, useRef } from 'react'
import axios from 'axios'

const TalkToMe = () => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [translation, setTranslation] = useState(null)
  const [isTranslating, setIsTranslating] = useState(false)
  const [error, setError] = useState(null)

  const recognitionRef = useRef(null)
  const translationTimeoutRef = useRef(null)

  // Initialize speech recognition
  const initSpeechRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition is not supported in this browser. Please use Chrome, Firefox, or Edge.')
      return null
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()

    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      console.log('Speech recognition started')
      setIsListening(true)
      setError(null)
      setTranscript('')
      setTranslation(null)
    }

    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPart
        } else {
          interimTranscript += transcriptPart
        }
      }

      const fullTranscript = finalTranscript || interimTranscript
      if (fullTranscript) {
        setTranscript(fullTranscript)
      }
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setError(`Speech recognition error: ${event.error}`)
      setIsListening(false)
    }

    recognition.onend = () => {
      console.log('Speech recognition ended')
      setIsListening(false)

      // Wait 1 second after speech ends, then translate if we have transcript
      if (transcript.trim()) {
        setTimeout(() => {
          if (transcript.trim() && !isTranslating) {
            translateText(transcript.trim())
          }
        }, 1000) // 1 second pause
      }
    }

    return recognition
  }

  const translateText = async (text) => {
    if (!text || isTranslating) return

    setIsTranslating(true)
    setError(null)

    try {
      console.log('🔄 Attempting to translate:', text)
      console.log('🌐 API URL:', 'http://localhost:8000/api/translate')

      const response = await axios.post('http://localhost:8000/api/translate', {
        english_word: text
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      })

      console.log('✅ Translation response:', response.data)
      setTranslation(response.data)
    } catch (err) {
      console.error('❌ Translation error:', err)
      console.error('❌ Error details:', {
        message: err.message,
        code: err.code,
        status: err.response?.status,
        data: err.response?.data
      })

      if (err.code === 'NETWORK_ERROR' || err.message.includes('Network Error')) {
        setError('🌐 Network error: Cannot connect to translation server. Make sure the backend is running on port 8000.')
      } else if (err.response?.status === 404) {
        setError('🔗 API endpoint not found. Check if backend server is running.')
      } else if (err.response?.status === 500) {
        setError('⚙️ Server error: Backend translation service is not working properly.')
      } else {
        setError(`❌ Translation failed: ${err.message}`)
      }
    } finally {
      setIsTranslating(false)
    }
  }

  const startListening = () => {
    if (isListening) {
      stopListening()
      return
    }

    if (!recognitionRef.current) {
      recognitionRef.current = initSpeechRecognition()
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.start()
      } catch (err) {
        console.error('Failed to start recognition:', err)
        setError('Failed to start speech recognition. Please try again.')
      }
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }

  const clearResults = () => {
    setTranscript('')
    setTranslation(null)
    setError(null)
  }

  return (
    <div className="talk-to-me-container">
      <div className="talk-to-me-header">
        <h2>🎤 Talk to Me</h2>
        <p>Speak in English and get instant German translation</p>
      </div>

      <div className="speech-interface">
        <div className="microphone-section">
          <button
            className={`microphone-btn ${isListening ? 'listening' : ''}`}
            onClick={startListening}
          >
            {isListening ? '🎤 Stop Listening' : '🎤 Start Listening'}
          </button>

          {isListening && (
            <div className="listening-indicator">
              <div className="pulse-animation"></div>
              <p>🎧 Listening... Speak now!</p>
            </div>
          )}

          {isTranslating && (
            <div className="translating-indicator">
              <div className="spinner"></div>
              <p>🌐 Translating...</p>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {transcript && (
          <div className="transcript-section">
            <div className="transcript-box">
              <h3>🗣️ You said:</h3>
              <p className="transcript-text">"{transcript}"</p>
            </div>
          </div>
        )}

        {translation && (
          <div className="translation-section">
            <div className="translation-card">
              <div className="word-translation">
                <div className="word-item english">
                  <span className="label">🇺🇸 English</span>
                  <h3>{transcript}</h3>
                </div>
                <div className="word-item german">
                  <span className="label">🇩🇪 German</span>
                  <h3>{translation.german_word}</h3>
                </div>
              </div>

              <div className="sentence-section">
                <div className="sentence-item">
                  <span className="label">English Example</span>
                  <p>{translation.english_sentence}</p>
                </div>
                <div className="sentence-item">
                  <span className="label">German Example</span>
                  <p>{translation.german_sentence}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {(transcript || translation || error) && (
          <div className="controls-section">
            <button className="btn btn-secondary" onClick={clearResults}>
              🗑️ Clear Results
            </button>
          </div>
        )}
      </div>

      <div className="instructions">
        <h3>💡 How to use:</h3>
        <div className="instruction-steps">
          <div className="step">
            <span className="step-number">1</span>
            <p>Click "🎤 Start Listening"</p>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <p>Speak clearly in English</p>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <p>See instant German translation!</p>
          </div>
        </div>
        <p className="tip">🔥 Pro tip: Allow microphone permissions when prompted by your browser</p>
      </div>
    </div>
  )
}

export default TalkToMe
