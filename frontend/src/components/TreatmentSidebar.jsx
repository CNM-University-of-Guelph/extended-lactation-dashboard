import React, { useState, useEffect } from 'react';
import '../styles/TreatmentSidebar.css';
import api from '../api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowRight, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

function TreatmentSidebar() {
    const [isHidden, setIsHidden] = useState(true);
    const [treatmentData, setTreatmentData] = useState([]);

    // Fetch treatment data from the backend
    useEffect(() => {
        api.get('/api/treatments/')
            .then(response => {
                setTreatmentData(response.data);
            })
            .catch(error => {
                console.error('Error fetching treatment data:', error);
            });
    }, []);

    const toggleSidebar = () => {
        setIsHidden(!isHidden);
    };

    return (
        <>
            {/* Sidebar */}
            <div className={`treatment-sidebar ${isHidden ? 'hide' : ''}`}>
                <button className="collapse-button" onClick={toggleSidebar}>
                    <FontAwesomeIcon icon={faArrowLeft} />
                </button>

                <div className="treatment-list">
                    <h2>Treatment Groups</h2>
                    {treatmentData.length > 0 ? (
                        treatmentData.map((item, index) => (
                            <div key={index} className="treatment-item">
                                <p><strong>Cow ID:</strong> {item.cow_id}</p>
                                <p><strong>Parity:</strong> {item.parity}</p>
                                <p><strong>Treatment Group:</strong> {item.treatment_group}</p>
                            </div>
                        ))
                    ) : (
                        <p>No treatment data available</p>
                    )}
                </div>
            </div>

            {/* Tab for showing the sidebar */}
            <div className="treatment-tab" onClick={toggleSidebar}>
                <FontAwesomeIcon icon={faArrowRight} size="2x" />
            </div>
        </>
    );
}

export default TreatmentSidebar;
