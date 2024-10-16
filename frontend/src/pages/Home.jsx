import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import DataUpload from "../components/DataUpload";
import TreatmentSidebar from "../components/TreatmentSidebar";
import DataControl from "../components/DataControl";
import DataDisplay from "../components/DataDisplay";
import api from "../api";
import Papa from "papaparse";

function Home() {
    const [isSidebarHidden, setIsSidebarHidden] = useState(true);

    const [dataType, setDataType] = useState("");
    const [selectedFile, setSelectedFile] = useState("");
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [rowLimitMessage, setRowLimitMessage] = useState("");
  
    const ROW_LIMIT = 1000;

    // Function to toggle sidebar visibility
    const toggleSidebar = () => {
        setIsSidebarHidden(!isSidebarHidden);
    };

    useEffect(() => {
        const fetchData = async () => {
          setLoading(true);
          try {
            let fetchedData = [];

            if (dataType === "csv" && !selectedFile) {
                // No file selected, do not fetch data
                return;
                
            } else if (dataType === "csv" && selectedFile) {
                // Fetch CSV data
                const res = await api.get(`/api/data/file/${selectedFile}/`);
                const parsedData = Papa.parse(res.data, { header: true });
                fetchedData = parsedData.data;
              
            } else if (dataType) {
              // Fetch data from backend models
              const res = await api.get(`/api/${dataType}/`);
              fetchedData = res.data;
            }
    
            // Handle row limit
            if (fetchedData.length > ROW_LIMIT) {
              setData(fetchedData.slice(0, ROW_LIMIT));
              setRowLimitMessage(
                `Showing the first ${ROW_LIMIT} rows out of ${fetchedData.length} total rows`
              );
            } else {
              setData(fetchedData);
              setRowLimitMessage("");
            }
          } catch (error) {
            console.error("Error fetching data:", error);
          } finally {
            setLoading(false);
          }
        };
    
        if (dataType) {
          fetchData();
        }
      }, [dataType, selectedFile]);

    return (
        <div>
          <Navbar />
          <TreatmentSidebar
            isHidden={isSidebarHidden}
            toggleSidebar={toggleSidebar}
          />
          <div className="left-container">
            <DataUpload />
            <DataControl
              dataType={dataType}
              setDataType={setDataType}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
            />
          </div>
          <DataDisplay
            data={data}
            loading={loading}
            rowLimitMessage={rowLimitMessage}
          />
        </div>
      );
}

export default Home;
