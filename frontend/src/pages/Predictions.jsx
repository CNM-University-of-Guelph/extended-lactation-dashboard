import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import PredictionCard from "../components/PredictionCard";
import FilterPredictions from '../components/FilterPredictions';
import TreatmentSidebar from "../components/TreatmentSidebar";
import api from '../api';
import '../styles/Predictions.css';

function Predictions() {
    const [predictions, setPredictions] = useState([]);
    const [filteredPredictions, setFilteredPredictions] = useState([]);
    const [cowIdFilter, setCowIdFilter] = useState('');
    const [parityFilter, setParityFilter] = useState('');

    const [isFilterHidden, setIsFilterHidden] = useState(false); 
    const [isTreatmentHidden, setIsTreatmentHidden] = useState(true);  
    const [isExpandedAll, setIsExpandedAll] = useState(false);

    // Toggle filter sidebar
    const handleToggleFilter = () => {
        setIsFilterHidden(!isFilterHidden);
        setIsTreatmentHidden(true);  // Hide treatment sidebar when filter is open
    };

    // Toggle treatment sidebar
    const handleToggleTreatment = () => {
        setIsTreatmentHidden(!isTreatmentHidden);
        setIsFilterHidden(true);  // Hide filter sidebar when treatment is open
    };

    const toggleExpandAllCards = (expandAll) => {
        setIsExpandedAll(expandAll);
    };

    // Fetch all predictions from backend
    useEffect(() => {
        api.get('api/predictions/')
            .then(response => {
                console.log('Fetched predictions:', response.data);
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

            <TreatmentSidebar 
                isHidden={isTreatmentHidden} 
                toggleSidebar={handleToggleTreatment}
            />

            <h1>Predictions Page</h1>
            
            <FilterPredictions
                cowIdFilter={cowIdFilter}
                setCowIdFilter={setCowIdFilter}
                parityFilter={parityFilter}
                setParityFilter={setParityFilter}
                isHidden={isFilterHidden}
                onToggleFilter={handleToggleFilter}
                toggleExpandAllCards={toggleExpandAllCards}
            />
            {/* Adjust cards-container based on both sidebars' visibility */}
            <div className={`cards-container 
                ${isFilterHidden ? 'expand-filter' : ''} 
                ${isTreatmentHidden ? 'expand-treatment' : ''}`}>
                {filteredPredictions.length > 0 ? (
                    filteredPredictions.map(prediction => (
                        <PredictionCard
                            key={`${prediction.cow_id}-${prediction.parity}`}
                            cowId={prediction.cow_id}
                            parity={prediction.parity}
                            predictedValue={prediction.predicted_value}
                            isExpandedAll={isExpandedAll}
                            lactationId={prediction.lactation_id}
                            treatmentGroup={prediction.treatment_group}
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
