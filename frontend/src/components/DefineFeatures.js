// import React, { useState, useEffect, useContext } from 'react';
// import { Link } from 'react-router-dom';
// import { AuthContext } from '../Context/AuthContext';
// import './DefineFeatures.css';

// const DefineFeatures = () => {
//   const { userId } = useContext(AuthContext);

//   const [tableData, setTableData] = useState(JSON.parse(localStorage.getItem(`tableData_${userId}`)) || [
//     { 'column1': 'Example Data 1', 'column2': 'Example Data 2' },
//   ]);

//   const [columns, setColumns] = useState(JSON.parse(localStorage.getItem(`columns_${userId}`)) || ['column1', 'column2']);

//   useEffect(() => {
//     localStorage.setItem(`tableData_${userId}`, JSON.stringify(tableData));
//     localStorage.setItem(`columns_${userId}`, JSON.stringify(columns));
//   }, [tableData, columns, userId]);

//   const handleAddRow = () => {
//     let newRow = {};
//     columns.forEach(column => {
//       newRow[column] = '';
//     });
//     setTableData([...tableData, newRow]);
//   };

//   const handleAddColumn = () => {
//     const newColumn = prompt('Enter the column name');
//     if (newColumn) {
//       setColumns([...columns, newColumn]);
//       setTableData(tableData.map(row => ({ ...row, [newColumn]: '' })));
//     }
//   };

//   const handleDeleteRow = (index) => {
//     const newTableData = [...tableData];
//     newTableData.splice(index, 1);
//     setTableData(newTableData);
//   };

//   const handleDeleteColumn = (column) => {
//     const newColumns = columns.filter(col => col !== column);
//     const newTableData = tableData.map(row => {
//       const newRow = { ...row };
//       delete newRow[column];
//       return newRow;
//     });
//     setColumns(newColumns);
//     setTableData(newTableData);
//   };

//   const handleChange = (index, column, event) => {
//     const newTableData = [...tableData];
//     newTableData[index][column] = event.target.value;
//     setTableData(newTableData);
//   };

//   const handleEditColumn = (column, newColumnName) => {
//     const newColumns = columns.map(col => (col === column ? newColumnName : col));
//     const newTableData = tableData.map(row => {
//       const newRow = { ...row };
//       newRow[newColumnName] = newRow[column];
//       delete newRow[column];
//       return newRow;
//     });
//     setColumns(newColumns);
//     setTableData(newTableData);
//   };

//   return (
//     <div className="define-features">
//       <nav>
//         <div className="nav-item">
//           <Link to="/login" className="nav-link">Login/Logout</Link>
//         </div>
//         <div className="nav-item">
//           <Link to="/profile" className="nav-link">Profile</Link>
//         </div>
//       </nav>
//       <div className="main-content">
//         <h1>Define Features</h1>
//         <button onClick={handleAddRow}>Add Row</button>
//         <button onClick={handleAddColumn}>Add Column</button>
//         <table>
//           <thead>
//             <tr>
//               {columns.map((column, index) => (
//                 <th key={index}>
//                   <input
//                     type="text"
//                     value={column}
//                     onChange={(event) => handleEditColumn(column, event.target.value)}
//                   />
//                   <button onClick={() => handleDeleteColumn(column)}>Delete</button>
//                 </th>
//               ))}
//               <th>Actions</th>
//             </tr>
//           </thead>
//           <tbody>
//             {tableData.map((row, index) => (
//               <tr key={index}>
//                 {columns.map((column, colIndex) => (
//                   <td key={colIndex}>
//                     <input
//                       type="text"
//                       value={row[column]}
//                       onChange={(event) => handleChange(index, column, event)}
//                     />
//                   </td>
//                 ))}
//                 <td>
//                   <button onClick={() => handleDeleteRow(index)}>Delete</button>
//                 </td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//         <div style={{
//           display: 'flex',
//           justifyContent: 'flex-end',
//           marginTop: '20px'
//         }}>
//           <button 
//             style={{
//               backgroundColor: 'lightgreen',
//               padding: '10px 20px',
//               border: 'none',
//               borderRadius: '5px'
//             }} 
//             onClick={() => alert('Data has been saved!')}>
//             Save
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default DefineFeatures;