import Header from "../components/Header";
import DataUpload from "../components/DataUpload";
import DisplayCSV from "../components/DisplayCSV";

function Home() {
    return(
        <div>
            <Header />
            <h1>Welcome to the Home page!</h1>
            <DataUpload />
            <DisplayCSV />
        </div>
    );
}

export default Home;