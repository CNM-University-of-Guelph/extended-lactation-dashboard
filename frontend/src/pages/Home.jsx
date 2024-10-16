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
    const [cowIdFilter, setCowIdFilter] = useState("");
    const [parityFilter, setParityFilter] = useState("");
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
        // For CSV, ensure a file is selected
        if (dataType === "csv" && !selectedFile) {
          return;
        }
  
        setLoading(true);
        setData([]);
        try {
          let fetchedData = [];
  
          if (dataType === "csv") {
            // Fetch CSV data
            const res = await api.get(`/api/data/file/${selectedFile}/`);
            const parsedData = Papa.parse(res.data, { header: true });
            fetchedData = parsedData.data;
          } else if (dataType) {
            // Fetch data from backend models with filters
            const params = {};
            if (cowIdFilter) params.cow_id = cowIdFilter;
            if (parityFilter) params.parity = parityFilter;
  
            const res = await api.get(`/api/${dataType}/`, { params });
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
      } else {
        // Clear data and rowLimitMessage when no dataType is selected
        setData([]);
        setRowLimitMessage("");
      }
    }, [dataType, selectedFile, cowIdFilter, parityFilter]);

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
              cowIdFilter={cowIdFilter}
              setCowIdFilter={setCowIdFilter}
              parityFilter={parityFilter}
              setParityFilter={setParityFilter}
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
