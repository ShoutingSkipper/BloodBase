import React, { useState } from 'react';

const IPFSUploader: React.FC = () => {
    const [data, setData] = useState('');
    const [response, setResponse] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            const res = await fetch('http://127.0.0.1:5000/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ data }),
            });

            if (!res.ok) {
                throw new Error(`Error: ${res.status}`);
            }

            const text = await res.text();
            setResponse(text);
        } catch (error) {
            console.error('Failed to submit data:', error);
            setResponse('Failed to submit data.');
        }
    };

    return (
        <div className="p-6 max-w-lg mx-auto">
            <h1 className="text-xl font-bold mb-4">Submit Data to IPFS</h1>
            <form onSubmit={handleSubmit}>
                <textarea
                    value={data}
                    onChange={(e) => setData(e.target.value)}
                    className="w-full p-2 border rounded mb-4"
                    rows={5}
                    placeholder="Enter your data"
                ></textarea>
                <button type="submit" className="bg-success-green text-white px-4 py-2 rounded">
                    Submit
                </button>
            </form>
            {response && <div className="mt-4 bg-off-white p-4 rounded">{response}</div>}
        </div>
    );
};

export default IPFSUploader;