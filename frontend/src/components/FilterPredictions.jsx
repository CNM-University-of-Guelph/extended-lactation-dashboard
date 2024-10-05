import React, { useState } from 'react';
import "../styles/FilterPredictions.css"
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter } from '@fortawesome/free-solid-svg-icons';

function FilterPredictions({ cowIdFilter, setCowIdFilter, parityFilter, setParityFilter, onToggleFilter }) {
    const [isHidden, setIsHidden] = useState(false);

    const toggleFilter = () => {
        setIsHidden(!isHidden);
        onToggleFilter(!isHidden);  // Notify the parent about filter state change
    };   

    return (
        <>
            <div className={`filter-container ${isHidden ? 'hide' : ''}`}>
                <button className="collapse-button" onClick={toggleFilter}>
                    {isHidden ? 'Show Filter' : 'Hide Filter'}
                </button>

                {!isHidden && (
                    <>
                        <label htmlFor="cowId">Filter by Cow ID:</label>
                        <input
                            type="text"
                            id="cowId"
                            value={cowIdFilter}
                            onChange={(e) => setCowIdFilter(e.target.value)}
                            placeholder="Enter Cow ID"
                        />

                        <label htmlFor="parity">Filter by Parity:</label>
                        <input
                            type="number"
                            id="parity"
                            value={parityFilter}
                            onChange={(e) => setParityFilter(e.target.value)}
                            placeholder="Enter Parity"
                        />
                    </>
                )}
            </div>
            
            <div className={`tab ${isHidden ? '' : 'hide'}`} onClick={toggleFilter}>
                <FontAwesomeIcon icon={faFilter} size="2x" />
            </div>
        </>
    );
}

export default FilterPredictions;
