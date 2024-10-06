import React, { useState } from 'react';
import "../styles/FilterPredictions.css"
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter } from '@fortawesome/free-solid-svg-icons';

function FilterPredictions({ cowIdFilter, setCowIdFilter, parityFilter, setParityFilter, onToggleFilter, toggleExpandAllCards }) {
    const [isHidden, setIsHidden] = useState(false);
    const [expandAll, setExpandAll] = useState(false);

    const toggleFilter = () => {
        setIsHidden(!isHidden);
        onToggleFilter(!isHidden);  // Notify the parent about filter state change
    };   

    const handleExpandAll = () => {
        setExpandAll(!expandAll);
        toggleExpandAllCards(!expandAll); // Notify the parent to expand/collapse all cards
    };

    return (
        <>
            <div className={`filter-container ${isHidden ? 'hide' : ''}`}>
                <button className="collapse-button" onClick={toggleFilter}>
                    {isHidden ? 'Show Filter' : 'Hide Filter'}
                </button>

                <button className="expand-all-button" onClick={handleExpandAll}>
                    {expandAll ? 'Collapse All' : 'Expand All'}
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

            {/* Tab for showing the filter */}
            <div className={`filter-tab ${isHidden ? '' : 'hide'}`} onClick={toggleFilter}>
                <FontAwesomeIcon icon={faFilter} size="2x" />
            </div>
        </>
    );
}

export default FilterPredictions;
