
import React from 'react';
import { Link } from 'react-router-dom';

export default function Landing() {
    return (
        <div className="container-center" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', gap: '2rem' }}>
            <div className="animate-fade-in">
                <h1 style={{ fontSize: '3.5rem', marginBottom: '1rem', fontWeight: 800 }}>
                    Chat with Your <span className="text-gradient">Documents</span>
                </h1>
                <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
                    Upload your PDFs and instantly get answers using AI. Unlock the knowledge trapped in your files.
                </p>

                <div style={{ marginTop: '3rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <Link to="/login">
                        <button className="btn btn-primary" style={{ padding: '0.75rem 2rem', fontSize: '1.1rem' }}>Get Started</button>
                    </Link>
                    <Link to="/signup">
                        <button className="btn btn-secondary" style={{ padding: '0.75rem 2rem', fontSize: '1.1rem' }}>Create Account</button>
                    </Link>
                </div>
            </div>

            <div style={{ marginTop: '4rem', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', textAlign: 'left', maxWidth: '1000px' }}>
                <div className="card">
                    <h3 style={{ color: 'var(--primary-light)' }}>📄 Upload</h3>
                    <p style={{ color: 'var(--text-muted)' }}>Drag & drop your PDF documents securely. We process them instantly.</p>
                </div>
                <div className="card">
                    <h3 style={{ color: 'var(--accent)' }}>🧠 Analyze</h3>
                    <p style={{ color: 'var(--text-muted)' }}>Our AI reads and understands your content, creating a searchable knowledge base.</p>
                </div>
                <div className="card">
                    <h3 style={{ color: 'var(--success)' }}>💬 Chat</h3>
                    <p style={{ color: 'var(--text-muted)' }}>Ask questions in natural language and get citation-backed answers.</p>
                </div>
            </div>
        </div>
    );
}
