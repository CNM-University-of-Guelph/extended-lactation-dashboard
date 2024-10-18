import React, { useState, useEffect, useRef } from "react";
import "../styles/DataDisplay.css";
import { CSSTransition } from "react-transition-group";

function DataDisplay({ data, loading, rowLimitMessage }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const expandedRef = useRef(null);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  // Add or remove class on body to prevent background scrolling
  useEffect(() => {
    if (isExpanded) {
      document.body.classList.add('no-scroll');
    } else {
      document.body.classList.remove('no-scroll');
    }

    // Cleanup on unmount
    return () => {
      document.body.classList.remove('no-scroll');
    };
  }, [isExpanded]);

  const TableContent = () => (
    <>
      {/* Table to display data */}
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {Object.keys(data[0]).map((header, index) => (
                <th key={index}>{header.replace(/_/g, " ")}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {Object.keys(data[0]).map((header, colIndex) => (
                  <td key={colIndex}>{row[header]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );

  return (
    <>
      <div className={`data-display-container ${isExpanded ? 'expanded' : ''}`}>
        {/* Loading Indicator */}
        {loading && <div className="spinner"></div>}

        {/* No Data Message */}
        {!loading && (!data || data.length === 0) && (
          <p>No data to display</p>
        )}

        {/* Row Limit Message */}
        {!loading && rowLimitMessage && (
          <p className="row-limit-message">{rowLimitMessage}</p>
        )}

        {/* Render Table Content in normal view */}
        {!loading && data && data.length > 0 && !isExpanded && (
          <div className="parent-container">
            <button className="expand-button" onClick={toggleExpanded}>
              Expand Table
            </button>
            <div className="table-wrapper">
              <TableContent />
            </div>
          </div>
        )}

      </div>

      {/* Expanded View */}
      <CSSTransition
      in={isExpanded}
      timeout={300}
      classNames="expand"
      unmountOnExit
      nodeRef={expandedRef}
    >
      <div className="expanded-table-container" ref={expandedRef}>
        <div className="overlay" onClick={toggleExpanded}></div>
        <div className="expanded-table-content">
          <button className="collapse-button" onClick={toggleExpanded}>
            Collapse Table
          </button>
          <div className="table-wrapper">
            <TableContent isExpandedView={true} />
          </div>
        </div>
      </div>
      </CSSTransition>

    </>
  );
}

export default DataDisplay;
