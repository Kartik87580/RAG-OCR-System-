
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../services/supabase';
import UploadPanel from '../components/UploadPanel';
import ChatPanel from '../components/ChatPanel';

import { API_BASE_URL } from '../api/config';

export default function Dashboard() {
    const { user, signOut, loading } = useAuth();
    const navigate = useNavigate();
    const [documents, setDocuments] = useState([]);
    const [currentDocumentId, setCurrentDocumentId] = useState(null);
    const [showUpload, setShowUpload] = useState(false);
    const [activeMenuDocId, setActiveMenuDocId] = useState(null);

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (!e.target.closest('.doc-options-btn') && !e.target.closest('.doc-menu')) {
                setActiveMenuDocId(null);
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    const handleDeleteDocument = async (docId, e) => {
        e.stopPropagation();
        if (!window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) return;

        setActiveMenuDocId(null);

        try {
            // Call backend to delete from DB, Storage, and Vector DB
            const response = await fetch(`${API_BASE_URL}/api/documents/${docId}`, {
                method: 'DELETE',
            });


            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to delete');
            }

            // Check if we deleted the current document
            const deletedDoc = documents.find(d => d.id === docId);
            if (deletedDoc && deletedDoc.job_id === currentDocumentId) {
                setCurrentDocumentId(null);
            }

            // Update list
            setDocuments(prev => prev.filter(d => d.id !== docId));
        } catch (error) {
            console.error('Error deleting document:', error);
            alert(`Failed to delete document: ${error.message}`);
        }
    };

    useEffect(() => {
        if (!loading && !user) {
            navigate('/login');
        }
    }, [user, loading, navigate]);

    useEffect(() => {
        if (user) {
            fetchDocuments();
        }
    }, [user]);

    const fetchDocuments = async () => {
        const { data, error } = await supabase
            .from('documents')
            .select('*')
            .eq('user_id', user.id) // RLS also enforces this, but good to be explicit
            .order('upload_time', { ascending: false });

        if (error) console.error('Error fetching docs:', error);
        else setDocuments(data || []);
    };

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

    const handleUploadSuccess = (docId) => {
        fetchDocuments();
        setCurrentDocumentId(docId);
        setShowUpload(false);
    };

    if (loading) return <div>Loading...</div>;
    if (!user) return null;

    return (

        <div className="dashboard-layout">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-brand">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M14 2V8H20" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M16 13H8" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M16 17H8" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M10 9H9H8" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <span>DocuChat AI</span>
                </div>
                <div className="header-user">
                    <span className="user-email">{user.email}</span>
                    <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
                        Sign Out
                    </button>
                </div>
            </header>

            <div className="dashboard-content">
                {/* Sidebar */}
                <aside className="sidebar">
                    <div className="sidebar-header">
                        <button
                            onClick={() => setShowUpload(true)}
                            className="btn btn-primary"
                            style={{ width: '100%' }}
                        >
                            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            New Document
                        </button>
                    </div>

                    <div className="sidebar-list custom-scrollbar">
                        {documents.length === 0 ? (
                            <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                No documents yet.
                            </div>
                        ) : (
                            documents.map(doc => (
                                <div
                                    key={doc.id}
                                    onClick={() => setCurrentDocumentId(doc.job_id)}
                                    className={`doc-item ${currentDocumentId === doc.job_id ? 'active' : ''}`}
                                >
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div className="doc-title" title={doc.filename}>{doc.filename}</div>
                                        <div className="doc-date">{new Date(doc.upload_time).toLocaleDateString()}</div>
                                    </div>

                                    <button
                                        className={`doc-options-btn ${activeMenuDocId === doc.id ? 'active' : ''}`}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setActiveMenuDocId(activeMenuDocId === doc.id ? null : doc.id);
                                        }}
                                        title="Options"
                                    >
                                        <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                                        </svg>
                                    </button>

                                    {activeMenuDocId === doc.id && (
                                        <div className="doc-menu">
                                            <button
                                                onClick={(e) => handleDeleteDocument(doc.id, e)}
                                                className="doc-menu-item text-danger"
                                            >
                                                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                                Delete Chat
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </aside>

                {/* Main Content */}
                <main className="main-area">
                    {/* Upload Modal */}
                    {showUpload && (
                        <div className="upload-modal-overlay" onClick={(e) => {
                            if (e.target.className === 'upload-modal-overlay') setShowUpload(false);
                        }}>
                            <div className="card" style={{ width: '100%', maxWidth: '500px', margin: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                    <h3>Upload Document</h3>
                                    <button onClick={() => setShowUpload(false)} className="btn btn-ghost" style={{ padding: '0.2rem' }}>✕</button>
                                </div>
                                <UploadPanel onUploadSuccess={handleUploadSuccess} userId={user.id} />
                            </div>
                        </div>
                    )}

                    {currentDocumentId ? (
                        <ChatPanel currentDocumentId={currentDocumentId} userId={user.id} />
                    ) : (
                        <div className="empty-state">
                            <div style={{ marginBottom: '1.5rem', opacity: 0.5 }}>
                                <svg width="64" height="64" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3>Select a document to start chatting</h3>
                            <p>Or upload a new PDF from the sidebar.</p>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}
