import React, { useState, useEffect } from "react";
import api from "../api";
import "../styles/DataUpload.css"

function DataUpload({ fetchFiles, userId }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [message, setMessage] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);
    const [logs, setLogs] = useState([])

    useEffect(() => {
        let socket;
    
        const connectWebSocket = () => {
            socket = new WebSocket(`ws://localhost:8000/ws/data-upload/${userId}/`);
    
            socket.onopen = () => {
                console.log("WebSocket connection opened.");
            };
    
            socket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                const message = data.message;

                // Split the message by line breaks and add each line as a new log entry
                const splitMessages = message.split('\n');
                setLogs((prevLogs) => [...prevLogs, ...splitMessages]);
            };
    
            socket.onclose = () => {
                console.log("WebSocket connection closed. Retrying in 3 seconds...");
                setTimeout(connectWebSocket, 3000); // Retry after 3 seconds
            };
    
            socket.onerror = (error) => {
                console.error("WebSocket error:", error);
            };
        };
    
        connectWebSocket();
    
        return () => {
            if (socket) socket.close();
        };
    }, [userId]);

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

            {/* Log Terminal */}
            <div className="log-terminal">
                {logs.map((log, index) => (
                    // <p key={index}>{log}</p>
                    <p key={index} style={{ margin: 3 }}>{log}</p>
                ))}
            </div>

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
