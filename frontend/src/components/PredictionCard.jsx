import React, { useState, useEffect } from 'react';
import "../styles/PredictionCard.css";
import api from '../api';

function PredictionCard({ cowId, parity, predictedValue, isExpandedAll, lactationId, treatmentGroup, onTreatmentGroupChange }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [selectedTreatmentGroup, setSelectedTreatmentGroup] = useState(treatmentGroup);

    // Update local isExpanded when isExpandedAll changes from the parent
    useEffect(() => {
        setIsExpanded(isExpandedAll);
    }, [isExpandedAll]);

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    const handleTreatmentChange = async (event) => {
        const newTreatmentGroup = event.target.value;
        setSelectedTreatmentGroup(newTreatmentGroup);

        // Send update request to backend
        try {
            const response = await api.post(`api/update-treatment-group/${lactationId}/`, {
                treatment_group: newTreatmentGroup
            });

            if (response.status === 200 && response.data.status === 'success') {
                console.log('Treatment group updated successfully:', response.data.message);
                onTreatmentGroupChange();
            } else {
                console.error('Error updating treatment group:', response.data.message);
            }
        } catch (error) {
            console.error('Error updating treatment group:', error);
        }
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

            <div className="treatment-group-dropdown">
                <label htmlFor={`treatment-group-${cowId}`}>Treatment Group: </label>
                <select
                    id={`treatment-group-${cowId}`}
                    value={selectedTreatmentGroup}
                    onChange={handleTreatmentChange}
                >
                    <option value="No group">No Group</option>
                    <option value="Extend 1 cycle">Extend 1 cycle</option>
                    <option value="Extend 2 cycles">Extend 2 cycles</option>
                    <option value="Extend 3 cycles">Extend 3 cycles</option>
                    <option value="Do not extend">Do not extend</option>
                </select>
            </div>

            {/* Expandable content with placeholder image */}
            <div className="expanded-content">
                <img src="/images/sample_bar_graph.jpg" alt="Placeholder Graph" />
            </div>
        </div>
    );
}

export default PredictionCard;
