import React from 'react';
import "../styles/PredictionCard.css";

const PredictionCard = ({ cowId, parity, predictedValue }) => {
  return (
    <div className="prediction-card">
      <h3>Cow ID: {cowId}</h3>
      <p>Parity: {parity}</p>
      <p>Predicted Value: {predictedValue}</p>
    </div>
  );
};

export default PredictionCard;
