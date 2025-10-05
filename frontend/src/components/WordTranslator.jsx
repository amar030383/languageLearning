import React, { useState } from 'react'
import axios from 'axios'

const WordTranslator = () => {
  const [englishWord, setEnglishWord] = useState('')
  const [translation, setTranslation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleTranslate = async () => {
    if (!englishWord.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('http://localhost:8000/api/translate', {
        english_word: englishWord.trim()
      })
      setTranslation(response.data)
    } catch (err) {
      setError('Failed to translate word')
      console.error('Translation error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleTranslate()
    }
  }

  return (
    <div className="translator-container">
      <div className="translator-header">
        <h2>🔄 Word Translator</h2>
        <p>Enter an English word to translate to German</p>
      </div>

      <div className="translator-input-section">
        <div className="input-group">
          <label htmlFor="english-word">English Word:</label>
          <input
            id="english-word"
            type="text"
            value={englishWord}
            onChange={(e) => setEnglishWord(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter a word (e.g., house, book, table)"
            className="word-input"
          />
        </div>

        <button
          className="btn btn-primary translate-btn"
          onClick={handleTranslate}
          disabled={!englishWord.trim() || loading}
        >
          {loading ? '🔄 Translating...' : '🌐 Translate'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {translation && (
        <div className="translation-result">
          <div className="translation-card">
            <div className="word-translation">
              <div className="word-item english">
                <span className="label">English</span>
                <h3>{englishWord}</h3>
              </div>
              <div className="word-item german">
                <span className="label">German</span>
                <h3>{translation.german_word}</h3>
              </div>
            </div>

            <div className="sentence-section">
              <div className="sentence-item">
                <span className="label">English Sentence</span>
                <p>{translation.english_sentence}</p>
              </div>
              <div className="sentence-item">
                <span className="label">German Sentence</span>
                <p>{translation.german_sentence}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WordTranslator
