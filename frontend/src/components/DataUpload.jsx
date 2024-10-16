import React, { useState } from "react";
import api from "../api";
import "../styles/DataUpload.css"

function DataUpload({ fetchFiles }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [message, setMessage] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);

    // Handle file selection
    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
        setMessage("") // Clear any messages
    };

    // Handle file upload
    const handleFileUpload = async () => {
        if (!selectedFile) {
            setMessage("Please select a file to upload.");
            return;
        }

        // Create FormData to send the file
        const formData = new FormData();
        formData.append("file", selectedFile);

        setIsProcessing(true);
        setMessage("Processing file...");

        try {
            const res = await api.post("/api/data/upload/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            });

            // Assuming backend sends a success message
            setMessage("File processed successfully!");
            console.log("Processed file path:", res.data.processed_file); 
            fetchFiles();

        } catch (error) {
            if (error.response && error.response.data) {
                setMessage(`Error: ${JSON.stringify(error.response.data.message)}`);
            } else {
                setMessage("Error processing the file. Please try again.");
            }
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="data-upload-container">
            <h2>Upload Data</h2>

            {/* Upload button */}
            <input type="file" onChange={handleFileChange} />

            {/* Display status or error messages */}
            {message && <p className="status-message">{message}</p>}

            {/* Submit button */}
            <button onClick={handleFileUpload} disabled={isProcessing} className="upload-button">
                {isProcessing ? "Processing..." : "Upload Data"}
            </button>
        </div>
    );
}

export default DataUpload;
