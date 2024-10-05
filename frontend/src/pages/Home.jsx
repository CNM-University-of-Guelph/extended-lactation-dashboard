import Navbar from "../components/Navbar";
import DataUpload from "../components/DataUpload";
import DisplayCSV from "../components/DisplayCSV";
import TreatmentSidebar from "../components/TreatmentSidebar";

function Home() {
    return(
        <div>
            <Navbar />
            <TreatmentSidebar /> 
            <DataUpload />
            <DisplayCSV />
        </div>
    );
}

export default Home;