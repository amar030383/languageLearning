import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios';
import Sidebar from './components/Sidebar'
import VocabularyPlayer from './components/VocabularyPlayer'
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
      </div>
    </div>
  )
}



export default App
