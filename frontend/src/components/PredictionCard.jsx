import React, { useState } from 'react';
import "../styles/PredictionCard.css";

function PredictionCard({ cowId, parity, predictedValue }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
      setIsExpanded(!isExpanded);
  };

  return (
    <div className={`prediction-card ${isExpanded ? 'expanded' : ''}`}>
        <div className="card-header">
            <div className="cow-info">
                <h3>Cow ID: {cowId}</h3>
                <p>Parity: {parity}</p>
            </div>
            <button className="expand-button" onClick={toggleExpand}>
                {isExpanded ? 'Collapse' : 'Expand'}
            </button>
        </div>
        <p className="predicted-value">Predicted Value: {predictedValue}</p>

        {isExpanded && (
            <div className="expanded-content">
                <img src="/images/sample_bar_graph.jpg" alt="Placeholder Graph" />
            </div>
        )}
    </div>
  );
}

export default PredictionCard;
