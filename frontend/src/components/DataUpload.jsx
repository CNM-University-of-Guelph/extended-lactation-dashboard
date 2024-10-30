import React, { useState, useEffect, useRef } from "react";
import api from "../api";
import "../styles/DataUpload.css"
import { CSSTransition } from "react-transition-group";

function DataUpload({ fetchFiles, userId }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [message, setMessage] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);
    const [logs, setLogs] = useState([])
    const [isLogVisible, setIsLogVisible] = useState(false);
    const logTerminalRef = useRef(null);

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
        // setMessage("Processing file...");
        setIsLogVisible(true);

        try {
            const res = await api.post("/api/data/upload/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            });

            // Assuming backend sends a success message
            setLogs((prevLogs) => [...prevLogs, "File processed successfully!"]);
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

    const toggleLogVisibility = () => {
        setIsLogVisible((prev) => !prev);
    };

    return (
        <div className={`data-upload-container ${isLogVisible ? 'expanded' : ''}`}>
            {/* Spinner positioned absolutely in the top-right corner */}
            {isProcessing && <div className="spinner-container"><div className="spinner"></div></div>}
            
            {/* Move header closer to the top */}
            <h2>Upload Data</h2>

            {/* File input row */}
            <div className="file-input-container">
                <label className="file-input-label" htmlFor="file-input"></label>
                <input 
                    type="file" 
                    id="file-input" 
                    onChange={handleFileChange} 
                    className="file-input"
                />
            </div>

            {/* Status message */}
            {message && <p className="status-message">{message}</p>}

            {/* Row of buttons */}
            <div className="button-row">
                <button 
                    onClick={handleFileUpload} 
                    disabled={isProcessing} 
                    className="upload-button"
                >
                    {isProcessing ? "Processing..." : "Upload Data"}
                </button>

                <button 
                    onClick={toggleLogVisibility} 
                    className="toggle-log-button"
                >
                    {isLogVisible ? "Collapse Log" : "Expand Log"}
                </button>
            </div>

            {/* Log Terminal with Transition */}
            <CSSTransition
                in={isLogVisible}
                timeout={300}
                classNames="slide-height"
                unmountOnExit
                nodeRef={logTerminalRef}
                onEnter={() => { logTerminalRef.current.style.height = '0px'; }}
                onEntering={() => { logTerminalRef.current.style.height = '100px'; }}
                onEntered={() => { logTerminalRef.current.style.height = '100px'; }}
                onExit={() => { logTerminalRef.current.style.height = '100px'; }}
                onExiting={() => { logTerminalRef.current.style.height = '0px'; }}
            >
                <div 
                    className={`log-terminal ${isLogVisible ? 'visible' : ''}`}
                    ref={logTerminalRef}
                >
                    {logs.map((log, index) => (
                        <p key={index} style={{ margin: 3 }}>{log}</p>
                    ))}
                </div>
            </CSSTransition>
        </div>
    );
}

export default DataUpload;
