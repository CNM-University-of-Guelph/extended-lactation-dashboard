import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import PredictionCard from "../components/PredictionCard";
import api from '../api';

function Predictions() {
    const [predictions, setPredictions] = useState([]);

    useEffect(() => {
        api.get('api/predictions/')
            .then(response => {
                setPredictions(response.data);
            })
            .catch(error => {
                console.error('Error fetching predictions:', error);
            });
    }, []);

    return (
        <div>
            <Header />
            <h1>Predictions Page</h1>

            <div className="predictions-page">
                {predictions.length > 0 ? (
                    predictions.map(prediction => (
                        <PredictionCard
                            key={`${prediction.cow_id}-${prediction.parity}`}
                            cowId={prediction.cow_id}
                            parity={prediction.parity}
                            predictedValue={prediction.predicted_value}
                        />
                    ))
                ) : (
                    <p>No predictions available at the moment.</p>
                )}
            </div>
        </div>
    );
}

export default Predictions;
