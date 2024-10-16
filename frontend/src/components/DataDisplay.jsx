import React from "react";
import "../styles/DataDisplay.css";

function DataDisplay({ data, loading, rowLimitMessage }) {

    return (
      <div className="data-display-container">
        {/* Loading Indicator */}
        {/* {loading && <p>Loading...</p>} */}
        {loading && (
        <div className="spinner"></div>
        )} 

        {/* No Data Message */}
        {!loading && (!data || data.length === 0) && <p>No data to display</p>}
  
        {/* Display row limit message */}
        {rowLimitMessage && (
          <p className="row-limit-message">{rowLimitMessage}</p>
        )}
  
        {/* Table to display data */}
        {data && data.length > 0 && (
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
        )}
      </div>
    );
  }
  
  export default DataDisplay;