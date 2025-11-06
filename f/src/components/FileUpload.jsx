import React, { useState } from "react";
import { uploadPDFs } from "../api";

const FileUpload = ({ onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!files.length) return alert("Please select PDFs first.");
    setLoading(true);
    try {
      const res = await uploadPDFs(files);
      console.log(res.data.message);
      onUploadComplete(); // Start polling for backend readiness
      setFiles([]);
    } catch (err) {
      console.error(err);
      alert("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={(e) => setFiles(Array.from(e.target.files))}
        className="border border-gray-300 rounded p-2 cursor-pointer"
        disabled={loading}
      />
      <button
        onClick={handleUpload}
        disabled={loading || !files.length}
        className={`px-4 py-2 rounded text-white font-semibold  ${
          loading || !files.length
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700 cursor-pointer"
        }`}
      >
        {loading ? "Uploading..." : "Upload PDFs"}
      </button>

      {loading && (
        <p className="text-gray-600 mt-2 animate-pulse">
          Processing PDFs and building embeddings...
        </p>
      )}
    </div>
  );
};

export default FileUpload;
