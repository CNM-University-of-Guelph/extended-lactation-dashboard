import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import PredictionCard from "../components/PredictionCard";
import FilterPredictions from '../components/FilterPredictions';
import api from '../api';

function Predictions() {
    const [predictions, setPredictions] = useState([]);
    const [filteredPredictions, setFilteredPredictions] = useState([]);
    const [cowIdFilter, setCowIdFilter] = useState('');
    const [parityFilter, setParityFilter] = useState('');

    // Fetch all predictions from backend
    useEffect(() => {
        api.get('api/predictions/')
            .then(response => {
                setPredictions(response.data);
                setFilteredPredictions(response.data);
            })
            .catch(error => {
                console.error('Error fetching predictions:', error);
            });
    }, []);

    // Filtering logic
    useEffect(() => {
        const filtered = predictions.filter(prediction => {
            const matchesCowId = cowIdFilter === '' || prediction.cow_id.includes(cowIdFilter);
            const matchesParity = parityFilter === '' || prediction.parity === parseInt(parityFilter);
            return matchesCowId && matchesParity;
        });
        setFilteredPredictions(filtered);
    }, [cowIdFilter, parityFilter, predictions]);

    return (
        <div>
            <Navbar />
            <h1>Predictions Page</h1>
            <FilterPredictions
                cowIdFilter={cowIdFilter}
                setCowIdFilter={setCowIdFilter}
                parityFilter={parityFilter}
                setParityFilter={setParityFilter}
            />
            <div className="predictions-list">
                {filteredPredictions.length > 0 ? (
                        filteredPredictions.map(prediction => (
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
