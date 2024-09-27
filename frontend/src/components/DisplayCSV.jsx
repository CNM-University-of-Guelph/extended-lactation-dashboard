import React, { useState, useEffect } from "react";
import api from "../api";
import Papa from "papaparse";
import "../styles/DisplayCSV.css";

function DisplayCSV() {
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState("");
    const [csvData, setCsvData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [rowLimitMessage, setRowLimitMessage] = useState("");

    const ROW_LIMIT = 1000;

    // Fetch CSV files from backend
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

    // Handle file selection
    const handleFileChange = (e) => {
        setSelectedFile(e.target.value);
        setLoading(true);

        // Fetch the CSV data for selected file
        const fetchCSVData = async (filename) => {
            try {
                const res = await api.get(`/api/data/file/${filename}/`);
                const parsedData = Papa.parse(res.data, { header: true });

                if (parsedData.data.length > ROW_LIMIT) {
                    setCsvData(parsedData.data.slice(0, ROW_LIMIT));
                    setRowLimitMessage(`Showing the first ${ROW_LIMIT} rows out of ${parsedData.data.length} total rows`);
                } else {
                    setCsvData(parsedData.data);
                    setRowLimitMessage("")
                }
            } catch (error) {
                console.error("Error fetching CSV data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchCSVData(e.target.value);
    };

    return (
        <div className="csv-display-container">
            <h2>Select a CSV File</h2>

            {/* Dropdown for selecting files */}
            <select onChange={handleFileChange} value={selectedFile}>
                <option value="" disabled>Select a file</option>
                {files.map((file, index) => (
                    <option key={index} value={file}>{file}</option>
                ))}
            </select>

            {/* Loading Indicator */}
            {loading && <p>Loading...</p>}

            {/* Display row limit message */}
            {rowLimitMessage && <p className="row-limit-message">{rowLimitMessage}</p>}


            <div className="table-wrapper">
                {/* Table to display CSV data */}
                <table>
                    <thead>
                        <tr>
                            {Object.keys(csvData[0] || {}).map((header, index) => (
                                <th key={index}>{header}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {csvData.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {Object.values(row).map((value, colIndex) => (
                                    <td key={colIndex}>{value}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default DisplayCSV;
