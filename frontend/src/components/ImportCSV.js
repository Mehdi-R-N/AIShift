import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ImportCSV.css';
import Papa from 'papaparse';
import { AuthContext } from '../Context/AuthContext';
import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const MAX_ROWS = 10;

function FileUploader({ onFileUploaded }) { // Removed fileUploaded prop
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      worker: true,
      skipEmptyLines: true,
      complete: function (results) {
        onFileUploaded(file.name, results.data);
      },
    });
  };

  return (
    <div>
      <input
        id="file-upload"
        type="file"
        accept=".csv"
        style={{ display: 'none' }}
        name="file"
        onChange={handleFileUpload}
      />
      <label htmlFor="file-upload" className="browse-btn">
        Browse Your Files
      </label>
    </div>
  );
}

function FileList({ files, onFileSelected, onDeleteFile }) {
  return (
    <div className="file-list">
      {files.filenames.map((filename, i) => (
        <div key={i}>
          <button onClick={() => onFileSelected(filename)}>{filename}</button>
          <button onClick={() => onDeleteFile(filename)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

function CsvTable({ data }) {
  const currentRows = data.slice(0, MAX_ROWS);

  return (
    <div>
      <table>
        <thead>
          <tr>
            {data[0] && Object.keys(data[0]).map((header) => <th key={header}>{header}</th>)}
          </tr>
        </thead>
        <tbody>
          {currentRows.map((row, i) => (
            <tr key={i}>
              {Object.values(row).map((value, j) => <td key={j}>{value}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ImportCSV({ userId }) {
  const { authenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [csvFiles, setCsvFiles] = useState({ filenames: [] });
  const [selectedCsvData, setSelectedCsvData] = useState([]);
  const [uploadMessage, setUploadMessage] = useState("");

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/files/user/${userId}`); // Fetch files for this user
        setCsvFiles(response.data);
      } catch (error) {
        console.error('Error fetching files: ', error);
      }
    };

    fetchFiles();
  }, [userId]);

  const handleFileUploaded = async (fileName, data) => {
    const file = new Blob([Papa.unparse(data)], { type: "text/csv" });
    let formData = new FormData();
    formData.append("file", file, fileName);
    formData.append("userId", userId); // Include userId
    try {
      await axios.post("http://localhost:8000/files/", formData);
      const response = await axios.get(`http://localhost:8000/files/user/${userId}`); // Fetch files for this user
      setCsvFiles(response.data);
      setUploadMessage("Your CSV file successfully uploaded!");
    } catch (error) {
      console.error("Error uploading file: ", error);
      setUploadMessage("Error uploading CSV file.");
    }
  };

  
  const handleDeleteFile = async (fileName) => {
    try {
      await axios.delete(`http://localhost:8000/files/${userId}/${fileName}`); // Include userId
      setCsvFiles((prev) => ({ filenames: prev.filenames.filter(file => file !== fileName) }));
      console.log('File deleted successfully');
    } catch (error) {
      console.error('Error deleting file: ', error);
    }
  };

  const handleFileSelected = async (fileName) => {
    try {
      const response = await axios.get(`http://localhost:8000/files/${userId}/${fileName}`); // Include userId
      setSelectedCsvData(Papa.parse(response.data).data);
    } catch (error) {
      console.error('Error fetching file: ', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <div className="navbar">
        {authenticated ? (
          <button onClick={handleLogout} className="nav-link">
            Logout
          </button>
        ) : (
          <a href="/login" className="nav-link">
            Login
          </a>
        )}
        <a href="/profile" className="nav-link">
          Profile
        </a>
      </div>

      <div className="main-content">
        <FileUploader onFileUploaded={handleFileUploaded} />
        <FileList files={csvFiles} onFileSelected={handleFileSelected} onDeleteFile={handleDeleteFile} />
      </div>
      
      {uploadMessage && <div className="upload-message">{uploadMessage}</div>}
      
      <div className="csv-table-container">
        {selectedCsvData.length > 0 && <CsvTable data={selectedCsvData} />}
      </div>
    </div>
  );
}

export default ImportCSV;
