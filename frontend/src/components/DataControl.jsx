import React, { useState, useEffect } from "react";
import api from "../api";
import "../styles/DataControl.css"

function DataControl({
  dataType,
  setDataType,
  selectedFile,
  setSelectedFile,
}) {
  const [files, setFiles] = useState([]);

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
  }, [dataType, setSelectedFile]);

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

      {dataType === "csv" && (
        <>
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
        </>
      )}
    </div>
  );
}

export default DataControl;
