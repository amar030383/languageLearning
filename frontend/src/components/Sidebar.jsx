import React from 'react'

const Sidebar = ({ activeFeature, onFeatureChange }) => {
  const features = [
    { id: 'vocabulary', name: '🇩🇪 Vocabulary Player', description: 'Learn German words with audio' }
  ]

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>German Learning</h2>
        <p>Choose a feature</p>
      </div>

      <div className="sidebar-menu">
        {features.map((feature) => (
          <button
            key={feature.id}
            className={`sidebar-item ${activeFeature === feature.id ? 'active' : ''}`}
            onClick={() => onFeatureChange(feature.id)}
          >
            <div className="feature-icon">{feature.name.split(' ')[0]}</div>
            <div className="feature-info">
              <h3>{feature.name.split(' ').slice(1).join(' ')}</h3>
              <p>{feature.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default Sidebar
