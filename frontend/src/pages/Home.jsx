import React, { useState, useEffect, useContext } from "react";
import Navbar from "../components/Navbar";
import DataUpload from "../components/DataUpload";
import TreatmentSidebar from "../components/TreatmentSidebar";
import DataControl from "../components/DataControl";
import DataDisplay from "../components/DataDisplay";
import api from "../api";
import Papa from "papaparse";
import { UserContext } from "../UserContext.jsx";
import "../styles/Home.css"

function Home() {
    const [isSidebarHidden, setIsSidebarHidden] = useState(true);

    const [dataType, setDataType] = useState("");
    const [selectedFile, setSelectedFile] = useState("");
    const [cowIdFilter, setCowIdFilter] = useState("");
    const [parityFilter, setParityFilter] = useState("");
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState([]);
  
    const { user } = useContext(UserContext);

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
  
          setData(fetchedData);      

        } catch (error) {
          console.error("Error fetching data:", error);
        } finally {
          setLoading(false);
        }
      };
  
      if (dataType) {
        fetchData();
      } else {
        setData([]);
      }
    }, [dataType, selectedFile, cowIdFilter, parityFilter]);

    const fetchFiles = async () => {
      try {
        const res = await api.get("/api/data/files");
        setFiles(res.data.files);
      } catch (error) {
        console.error("Error fetching files:", error);
      }
    };

    return (
        <div className="home-container">
          <Navbar />
          <TreatmentSidebar
            isHidden={isSidebarHidden}
            toggleSidebar={toggleSidebar}
          />
          <DataUpload fetchFiles={fetchFiles} userId={user?.id}/>
          <DataControl
            dataType={dataType}
            setDataType={setDataType}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            cowIdFilter={cowIdFilter}
            setCowIdFilter={setCowIdFilter}
            parityFilter={parityFilter}
            setParityFilter={setParityFilter}
            files={files}
          />
          <DataDisplay
            data={data}
            loading={loading}
          />
        </div>
      );
}

export default Home;
