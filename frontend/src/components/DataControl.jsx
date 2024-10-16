import React, { useState, useEffect, useRef } from "react";
import api from "../api";
import "../styles/DataControl.css"
import { CSSTransition, SwitchTransition } from "react-transition-group";

function DataControl({
  dataType,
  setDataType,
  selectedFile,
  setSelectedFile,
  cowIdFilter,
  setCowIdFilter,
  parityFilter,
  setParityFilter,
}) {
  const [files, setFiles] = useState([]);

  const csvRef = useRef(null);
  const filtersRef = useRef(null);
  const emptyRef = useRef(null);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await api.get("/api/data/files");
        setFiles(res.data.files);
      } catch (error) {
        console.error("Error fetching files:", error);
      }
    };
    fetchFiles();
  }, []);

  // Reset selected file when data type changes
  useEffect(() => {
    if (dataType !== "csv") {
      setSelectedFile("");
    }
    setCowIdFilter("");
    setParityFilter("");
  }, [dataType, setSelectedFile]);

  const getNodeRef = () => {
    if (dataType === "csv") {
      return csvRef;
    } else if (dataType) {
      return filtersRef;
    } else {
      return emptyRef;
    }
  };

  return (
    <div className="data-control-container">
      <h2>Select Data Type</h2>
      <select
        onChange={(e) => setDataType(e.target.value)}
        value={dataType}
        className="data-type-select"
      >
        <option value="" disabled>
          Select data type
        </option>
        <option value="csv">Uploaded CSV Files</option>
        <option value="lactation-data">Lactation Data</option>
        <option value="multiparous-features">Multiparous Features</option>
        <option value="primiparous-features">Primiparous Features</option>
      </select>

      <SwitchTransition mode="out-in">
        <CSSTransition
          key={dataType || "empty"}
          timeout={300}
          classNames="fade"
          unmountOnExit
          nodeRef={getNodeRef()}
        >
          {/* Render content based on dataType */}
          {dataType === "csv" ? (
            <div className="csv-content" ref={csvRef}>
              <h2>Select a CSV File</h2>
              <select
                onChange={(e) => setSelectedFile(e.target.value)}
                value={selectedFile}
                className="file-select"
              >
                <option value="" disabled>
                  Select a file
                </option>
                {files.map((file, index) => (
                  <option key={index} value={file}>
                    {file}
                  </option>
                ))}
              </select>
            </div>
          ) : dataType ? (
            <div className="filters-container" ref={filtersRef}>
              <h2>Filters</h2>
              <input
                type="text"
                placeholder="Cow ID"
                value={cowIdFilter}
                onChange={(e) => setCowIdFilter(e.target.value)}
                className="filter-input"
              />
              <input
                type="number"
                placeholder="Parity"
                value={parityFilter}
                onChange={(e) => setParityFilter(e.target.value)}
                className="filter-input"
              />
            </div>
          ) : (
            <div ref={emptyRef}></div>
          )}
        </CSSTransition>
      </SwitchTransition>

    </div>
  );
}

export default DataControl;
