import React, { useState, useEffect } from 'react';
import '../styles/TreatmentSidebar.css';
import api from '../api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowRight, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

function TreatmentSidebar({ isHidden, toggleSidebar, refreshTrigger }) {
    const [treatmentData, setTreatmentData] = useState([]);
    const treatmentGroups = [
        "No group",
        "Extend 1 cycle",
        "Extend 2 cycles",
        "Extend 3 cycles",
        "Extend 4 cycles",
        "Extend 5 cycles",
        "Extend 6 cycles",
        "Extend 7 cycles",
        "Extend 8 cycles",
        "Extend 9 cycles",
        "Extend 10 cycles",
        "Do not extend"
    ];

    // Fetch treatment data from the backend
    useEffect(() => {
        api.get('/api/treatments/')
            .then(response => {
                setTreatmentData(response.data);
            })
            .catch(error => {
                console.error('Error fetching treatment data:', error);
            });
    }, [refreshTrigger]);

    const groupedData = treatmentGroups.reduce((acc, group) => {
        acc[group] = treatmentData.filter(item => item.treatment_group === group);
        return acc;
    }, {});

    return (
        <>
            {/* Sidebar */}
            <div className={`treatment-sidebar ${isHidden ? 'hide' : ''}`}>

                {/* Header Section */}
                <div className="sidebar-header">
                    <button className="collapse-button" onClick={toggleSidebar}>
                        <FontAwesomeIcon icon={faArrowLeft} />
                    </button>
                    <h2>Treatment Groups</h2>
                </div>

                <div className="treatment-list">
                    {treatmentGroups.map(group => (
                        <div key={group} className="treatment-group">
                            <h3>{group}</h3>
                            {groupedData[group].length > 0 ? (
                                groupedData[group].map((item, index) => (
                                    <div key={index} className="treatment-item">
                                        <p><strong>Cow ID:</strong> {item.cow_id}</p>
                                        <p><strong>Parity:</strong> {item.parity}</p>
                                    </div>
                                ))
                            ) : (
                                <p className="no-cows-message">No cows in {group}</p>
                            )}
                        </div>
                    ))}
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
