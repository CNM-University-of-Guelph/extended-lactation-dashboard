import React, { useState } from "react";
import Navbar from "../components/Navbar";
import DataUpload from "../components/DataUpload";
import DisplayCSV from "../components/DisplayCSV";
import TreatmentSidebar from "../components/TreatmentSidebar";

function Home() {
    const [isSidebarHidden, setIsSidebarHidden] = useState(true);

    // Function to toggle sidebar visibility
    const toggleSidebar = () => {
        setIsSidebarHidden(!isSidebarHidden);
    };


    return(
        <div>
            <Navbar />
            <TreatmentSidebar 
                isHidden={isSidebarHidden} 
                toggleSidebar={toggleSidebar} 
            />
            <DataUpload />
            <DisplayCSV />
        </div>
    );
}

export default Home;