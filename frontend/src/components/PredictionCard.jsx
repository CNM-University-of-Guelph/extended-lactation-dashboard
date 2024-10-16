import React, { useState, useEffect } from 'react';
import "../styles/PredictionCard.css";
import api from '../api';

function PredictionCard({ 
    cowId, 
    parity, 
    predictedValue, 
    isExpandedAll, 
    lactationId, 
    treatmentGroup, 
    onTreatmentGroupChange, 
    plotPath, 
    extend1Cycle, 
    extend2Cycle, 
    extend3Cycle, 
    daysToTarget 
}) {
    const baseURL = "http://localhost:8000/media/";
    const fullPlotPath = `${baseURL}${plotPath}`;

    const [isExpanded, setIsExpanded] = useState(false);
    const [selectedTreatmentGroup, setSelectedTreatmentGroup] = useState(treatmentGroup);

    // Debug: Log the incoming props
    // console.log("PredictionCard props:", {
    //     cowId,
    //     parity,
    //     predictedValue,
    //     plotPath,
    //     extend1Cycle,
    //     extend2Cycle,
    //     extend3Cycle,
    //     daysToTarget,
    //     fullPlotPath
    // });

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
    
    const formatNumber = (value) => {
        if (typeof value === 'number' && !isNaN(value)) {
          return value.toFixed(2);
        } else {
          return '';
        }
      };

      return (
        <div className={`prediction-card ${isExpanded ? 'expanded' : ''}`}>
          <div className="card-header">
            {/* Left Section: Cow ID and Parity */}
            <div className="left-section">
              <div className="cow-info">
                <h2>Cow ID: {cowId}</h2>
                <h3>Parity: {parity}</h3>
              </div>
            </div>
    
            {/* Center Section: Predicted Value, Days to Target, Treatment Group */}
            <div className="center-section">
              <div className="predicted-value-section">
                <h3 className="label">Predicted d305 Milk Yield</h3>
                <p className="value">{`${formatNumber(predictedValue)} kg/d`}</p>
              </div>
              <div className="days-to-target-section">
                <h3 className="label">Days to 20 kg/d</h3>
                <p className="value">{daysToTarget}</p>
              </div>
              <div className="treatment-group-section">
                <label htmlFor={`treatment-group-${cowId}`}>Treatment Group</label>
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
            </div>
    
            {/* Right Section: Expand/Collapse Button */}
            <div className="right-section">
              <button className="expand-button" onClick={toggleExpand}>
                {isExpanded ? 'Collapse' : 'Expand'}
              </button>
            </div>
          </div>
    
          {/* Expanded content */}
          <div className={`expanded-content ${isExpanded ? 'expanded' : ''}`}>
            <div className="plot-container">
              <img src={fullPlotPath} alt="Prediction Plot" className="prediction-plot" />
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Extend 1 Cycle</th>
                    <th>Extend 2 Cycles</th>
                    <th>Extend 3 Cycles</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{formatNumber(extend1Cycle)}</td>
                    <td>{formatNumber(extend2Cycle)}</td>
                    <td>{formatNumber(extend3Cycle)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      );
    }

export default PredictionCard;
