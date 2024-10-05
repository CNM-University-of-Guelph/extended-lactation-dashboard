import React, { useEffect, useState } from 'react';
import "../styles/FilterPredictions.css"

function FilterPredictions({ cowIdFilter, setCowIdFilter, parityFilter, setParityFilter }) {
    const [isCollapsed, setIsCollapsed] = useState(false);

    const toggleFilter = () => {
        setIsCollapsed(!isCollapsed);
    };   

    return (
        <div className="filter-container" style={{ maxHeight: isCollapsed ? '50px' : '1000px' }}>
            <button className="collapse-button" onClick={toggleFilter}>
                {isCollapsed ? 'Show Filter' : 'Hide Filter'}
            </button>

            {!isCollapsed && (
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
    );
}

export default FilterPredictions;
