import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [state, setState] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [viewMode, setViewMode] = useState('desktop'); // 'desktop' or 'mobile'
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeTab, setActiveTab] = useState('billing'); // 'billing', 'email', 'sms', 'push'
  const [loading, setLoading] = useState(true);
  const [pollError, setPollError] = useState(false);

  // Poll state.json from Streamlit public folder
  useEffect(() => {
    const fetchState = () => {
      fetch('/state.json')
        .then((res) => {
          if (!res.ok) throw new Error('State not initialized');
          return res.json();
        })
        .then((data) => {
          setState(data);
          setLoading(false);
          setPollError(false);
          
          // Keep current logged-in user updated with latest data
          if (currentUser) {
            const updatedUser = data.customers.find((c) => c.id === currentUser.id);
            if (updatedUser) {
              setCurrentUser(updatedUser);
            }
          }
        })
        .catch((err) => {
          console.warn('Waiting for simulation to start...', err);
          setPollError(true);
          setLoading(false);
        });
    };

    fetchState();
    const interval = setInterval(fetchState, 2000); // Poll every 2s
    return () => clearInterval(interval);
  }, [currentUser]);

  // Handle local response actions for In-App checkins
  const [showInAppModal, setShowInAppModal] = useState(true);
  const [inAppSubmitted, setInAppSubmitted] = useState(false);

  // Fallback initial customers if state.json is not ready
  const defaultCustomers = [
    { id: "C001", name: "Student Sam", persona: "Price-sensitive student", product_id: "P001", status: "Active", engagement_score: 85, test_group: "Group A (AI-driven CLM)", clv: 29.0 },
    { id: "C002", name: "Corporate Clara", persona: "Busy technical manager", product_id: "P002", status: "Active", engagement_score: 40, test_group: "Group A (AI-driven CLM)", clv: 99.0 },
    { id: "C003", name: "Ghosting Greg", persona: "Inactive developer", product_id: "P003", status: "Active", engagement_score: 25, test_group: "Group A (AI-driven CLM)", clv: 15.0 },
    { id: "C004", name: "Scale-up Sarah", persona: "SaaS founder hitting limits", product_id: "P001", status: "Active", engagement_score: 90, test_group: "Group B (Standard Rules)", clv: 29.0 },
    { id: "C005", name: "Bargain Betty", persona: "Deal hunting buyer", product_id: "P001", status: "Active", engagement_score: 30, test_group: "Group B (Standard Rules)", clv: 29.0 }
  ];

  const customersList = state ? state.customers : defaultCustomers;

  const productCatalog = {
    "P001": { name: "Pro Subscription", base_price: 29.0, desc: "Unlimited projects, standard API access" },
    "P002": { name: "Enterprise Plan", base_price: 99.0, desc: "SSO, 24/7 dedicated support, SLA compliance" },
    "P003": { name: "API Add-on", base_price: 15.0, desc: "High-throughput API usage keys" },
    "P004": { name: "Pro + API Bundle", base_price: 39.0, desc: "Combined Pro plan and high-throughput API Add-on for power users" }
  };

  const handleLogin = (user) => {
    setCurrentUser(user);
    // Reset view specific states
    setSelectedEmail(null);
    setShowInAppModal(true);
    setInAppSubmitted(false);
    setActiveTab('billing');
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  // Filter messages for logged in user
  const userMessages = currentUser && currentUser.messages ? currentUser.messages : [];
  const emails = userMessages.filter(m => m.channel === 'Email');
  const sms = userMessages.filter(m => m.channel === 'SMS');
  const push = userMessages.filter(m => m.channel === 'Push');
  
  // Check if there is an active in-app notification sent today (where day matches current simulation day)
  const latestInApp = userMessages
    .filter(m => m.channel === 'In-App')
    .slice(-1)[0];

  // Price calculations
  const productKey = currentUser ? currentUser.product_id : 'P001';
  const currentProduct = productCatalog[productKey];
  const basePrice = state ? state.price_history[currentProduct.name].slice(-1)[0] : currentProduct.base_price;
  
  // Calculate if last action was a successful discount
  const hasActiveDiscount = currentUser && 
    (currentUser.last_action === 'SEND_SMS_DISCOUNT' || currentUser.last_action === 'SEND_EMAIL_DISCOUNT') && 
    currentUser.messages.slice(-1)[0]?.reaction.includes('Accepted');
  
  const discountRate = hasActiveDiscount ? 0.3 : 0.0;
  const finalPrice = (basePrice * (1 - discountRate)).toFixed(2);

  if (loading) {
    return (
      <div className="center-wrapper">
        <div className="spinner"></div>
        <p>Loading Customer workspace...</p>
      </div>
    );
  }

  // LOGIN SCREEN
  if (!currentUser) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <span className="login-logo">⚡ RetentionX Client Portal</span>
            <h1>Access Your Subscription Workspace</h1>
            <p>Select a simulated customer persona to log in, view private communications (SMS, emails, push notices), check current invoice details, and interact with the background retention loop.</p>
          </div>

          {pollError && (
            <div className="warning-banner">
              ⚠️ <strong>Backend Offline:</strong> Run Streamlit (`streamlit run app.py`) and simulate Day 1 to initialize the live OODA feed. Showing offline mockup.
            </div>
          )}

          <div className="user-grid">
            {customersList.map((user) => {
              const prod = productCatalog[user.product_id];
              const isChurned = user.status === 'Churned';
              return (
                <div 
                  key={user.id} 
                  className={`user-login-card ${isChurned ? 'card-churned' : ''}`}
                  onClick={() => !isChurned && handleLogin(user)}
                >
                  <div className="user-avatar">
                    {user.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <h3>{user.name}</h3>
                  <span className="user-meta">{user.persona}</span>
                  <div className="user-plan-badge">{prod.name}</div>
                  <div style={{ fontSize: '0.7rem', color: '#c084fc', fontWeight: 600, marginBottom: '0.6rem' }}>
                    {user.test_group || 'Group A (AI-driven CLM)'}
                  </div>
                  
                  <div className="health-row">
                    <span className="health-label">Engagement Score</span>
                    <span className="health-value">{user.engagement_score}/100</span>
                  </div>
                  <div className="health-row" style={{ marginTop: '0.2rem', marginBottom: '0.4rem' }}>
                    <span className="health-label">Simulated CLV</span>
                    <span className="health-value" style={{ color: '#34d399', fontWeight: '700' }}>${(user.clv || 0).toFixed(2)}</span>
                  </div>
                  <div className="health-bar-container">
                    <div 
                      className={`health-bar ${user.engagement_score < 30 ? 'low' : user.engagement_score < 70 ? 'med' : 'high'}`}
                      style={{ width: `${user.engagement_score}%` }}
                    ></div>
                  </div>

                  {isChurned ? (
                    <div className="churned-banner">💀 CHURNED (Unsubscribed)</div>
                  ) : (
                    <button className="login-btn">Log In</button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // MAIN CLIENT WORKSPACE
  return (
    <div className="workspace-container">
      {/* Top Navbar */}
      <header className="workspace-header">
        <div className="header-left">
          <span className="header-logo">⚡ ClientWorkspace</span>
          <span className="user-badge">👤 {currentUser.name} ({currentUser.segment})</span>
        </div>
        <div className="header-right">
          {/* Toggle View Mode */}
          <div className="view-mode-toggle">
            <button 
              className={viewMode === 'desktop' ? 'active' : ''} 
              onClick={() => setViewMode('desktop')}
            >
              💻 Desktop View
            </button>
            <button 
              className={viewMode === 'mobile' ? 'active' : ''} 
              onClick={() => setViewMode('mobile')}
            >
              📱 Mobile View
            </button>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Log Out</button>
        </div>
      </header>

      {state && (
        <div className="day-ticker">
          Simulation Day: <strong>{state.day_count}</strong> | Global Subscription Status: <strong className="green">Active</strong>
        </div>
      )}

      {/* DESKTOP WEB PORTAL */}
      {viewMode === 'desktop' && (
        <div className="desktop-layout">
          {/* Left Navigation Tabs */}
          <aside className="desktop-sidebar">
            <nav className="desktop-nav">
              <button 
                className={activeTab === 'billing' ? 'nav-item active' : 'nav-item'} 
                onClick={() => setActiveTab('billing')}
              >
                💳 Subscription & Invoices
              </button>
              <button 
                className={activeTab === 'email' ? 'nav-item active' : 'nav-item'} 
                onClick={() => setActiveTab('email')}
              >
                ✉️ Email Inbox <span className="count">{emails.length}</span>
              </button>
              <button 
                className={activeTab === 'sms' ? 'nav-item active' : 'nav-item'} 
                onClick={() => setActiveTab('sms')}
              >
                💬 SMS Log <span className="count">{sms.length}</span>
              </button>
              <button 
                className={activeTab === 'push' ? 'nav-item active' : 'nav-item'} 
                onClick={() => setActiveTab('push')}
              >
                🔔 Push Notifications <span className="count">{push.length}</span>
              </button>
            </nav>

            <div className="sidebar-footer">
              <h4>System Vibe Check</h4>
              <p>Engagement rating holds at <strong>{currentUser.engagement_score}/100</strong>.</p>
              <div className="small-health-bar" style={{ marginBottom: '0.6rem' }}>
                <div style={{ width: `${currentUser.engagement_score}%` }}></div>
              </div>
              <div style={{ fontSize: '0.7rem', color: '#c084fc', fontWeight: 700 }}>
                {currentUser.test_group || 'Group A (AI-driven CLM)'}
              </div>
            </div>
          </aside>

          {/* Right Content Pane */}
          <main className="desktop-content">
            
            {/* BILLING PORTAL */}
            {activeTab === 'billing' && (
              <div className="tab-pane">
                <h2>Subscription Billing Center</h2>
                {state && state.llm_provider && (
                  <div className="model-badge-info" style={{ background: 'rgba(255,255,255,0.03)', padding: '0.4rem 0.8rem', borderRadius: '8px', fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '1.2rem', display: 'inline-block', border: '1px solid var(--border-color)' }}>
                    🤖 Campaigns Orchestrated by: <strong style={{ color: 'white', textTransform: 'capitalize' }}>{state.llm_provider}</strong> Agent Model
                  </div>
                )}
                <p className="subtitle">Manage tier plans, check billing details, and verify active promotions.</p>
                
                <div className="billing-grid">
                  <div className="billing-card main-plan">
                    <span className="plan-label">CURRENT PLAN</span>
                    <h3>{currentProduct.name}</h3>
                    <p className="plan-desc">{currentProduct.desc}</p>
                    
                    <div className="price-box">
                      <span className="price-value">${finalPrice}</span>
                      <span className="price-period">/ month</span>
                    </div>

                    {hasActiveDiscount && (
                      <div className="discount-applied-pill">
                        🎁 30% SMS/Email Retention Discount Applied
                      </div>
                    )}
                  </div>

                  <div className="billing-card payment-history">
                    <h3>Billing Details</h3>
                    <div className="billing-row">
                      <span>Standard Base Price</span>
                      <span>${basePrice.toFixed(2)}/mo</span>
                    </div>
                    <div className="billing-row">
                      <span>Retention Discount</span>
                      <span>-{hasActiveDiscount ? '30%' : '$0.00'}</span>
                    </div>
                    <hr className="divider" />
                    <div className="billing-row total">
                      <span>Monthly Charge</span>
                      <span>${finalPrice}/mo</span>
                    </div>
                    <div className="billing-row" style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed var(--border-color)' }}>
                      <span>Lifetime Value (CLV)</span>
                      <span style={{ color: '#34d399', fontWeight: 'bold' }}>${(currentUser.clv || 0).toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="included-features">
                  <h3>Included Sub-Features</h3>
                  <ul>
                    {currentProduct.desc.split(',').map((f, i) => (
                      <li key={i}>✓ {f.trim()}</li>
                    ))}
                    <li>✓ High speed webhook integrations</li>
                    <li>✓ Custom SSL setups</li>
                  </ul>
                </div>
              </div>
            )}

            {/* EMAIL CLIENT */}
            {activeTab === 'email' && (
              <div className="tab-pane email-client">
                <h2>Mailbox Workspace</h2>
                {emails.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">✉️</div>
                    <p>Your inbox is empty. Retention outreach emails will appear here when the agent decides to contact you.</p>
                  </div>
                ) : (
                  <div className="email-workspace">
                    <div className="email-list">
                      {emails.map((e, index) => (
                        <div 
                          key={index} 
                          className={`email-item ${selectedEmail === e ? 'active' : ''}`}
                          onClick={() => setSelectedEmail(e)}
                        >
                          <div className="email-subject-line">
                            <strong>{e.content.split('\n')[0].replace('Subject: ', '')}</strong>
                          </div>
                          <div className="email-preview">
                            {e.content.split('\n').slice(2).join(' ').substring(0, 80)}...
                          </div>
                          <span className="email-day">Day {e.day}</span>
                        </div>
                      ))}
                    </div>
                    <div className="email-body">
                      {selectedEmail ? (
                        <div className="email-viewer">
                          <div className="email-header-info">
                            <h3>{selectedEmail.content.split('\n')[0].replace('Subject: ', '')}</h3>
                            <div className="sender-meta">
                              <span>From: <strong>RetentionX Operations &lt;ops@retentionx.ai&gt;</strong></span>
                              <span>Day {selectedEmail.day}</span>
                            </div>
                          </div>
                          <div className="email-content-text">
                            {selectedEmail.content.split('\n').slice(2).map((para, i) => (
                              <p key={i}>{para}</p>
                            ))}
                          </div>
                          <div className="email-actions-mock">
                            <button className="reply-btn">Reply to Operations</button>
                            <span className="reaction-meta">
                              🤝 <strong>Your Simulated Action:</strong> {selectedEmail.reaction}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="select-email-prompt">
                          <p>Select an email from the inbox list to read the full outreach content and inspect user reaction logs.</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* SMS WORKSPACE */}
            {activeTab === 'sms' && (
              <div className="tab-pane">
                <h2>Outbound Mobile SMS Transcripts</h2>
                <p className="subtitle">Review the raw text messages push-delivered to your cellular device.</p>
                {sms.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">💬</div>
                    <p>No SMS outreach logs recorded. The system uses SMS channels if you are price-sensitive or have dropped off.</p>
                  </div>
                ) : (
                  <div className="sms-list-desktop">
                    {sms.map((s, index) => (
                      <div key={index} className="sms-log-bubble">
                        <div className="sms-log-time">Day {s.day} via Mobile Carrier</div>
                        <div className="sms-log-body">
                          <div className="bubble-text">{s.content}</div>
                        </div>
                        <div className="sms-log-footer">
                          📱 <strong>Simulated Response:</strong> <i>{s.reaction} (Impact: {s.impact} score)</i>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* PUSH NOTIFICATIONS */}
            {activeTab === 'push' && (
              <div className="tab-pane">
                <h2>Mobile App Push Notifications</h2>
                <p className="subtitle">Alert notifications pushed to user lockscren dashboard.</p>
                {push.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">🔔</div>
                    <p>No push notification logs recorded.</p>
                  </div>
                ) : (
                  <div className="push-notifications-list">
                    {push.map((p, index) => (
                      <div key={index} className="push-notification-card">
                        <div className="push-header">
                          <span className="push-app-icon">⚡</span>
                          <span className="push-app-title">Workspace Client</span>
                          <span className="push-time">Day {p.day}</span>
                        </div>
                        <div className="push-content">
                          {p.content}
                        </div>
                        <div className="push-action-log">
                          👉 <strong>Reaction:</strong> {p.reaction} ({p.impact >= 0 ? '+' : ''}{p.impact} engagement)
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </main>

          {/* FLOATING IN-APP MODAL IF AGENT TRIGGERED IT TODAY */}
          {latestInApp && showInAppModal && (
            <div className="floating-inapp-popup">
              <div className="inapp-card">
                <div className="inapp-header">
                  <h4>💡 Account Check-in Alert</h4>
                  <button className="inapp-close" onClick={() => setShowInAppModal(false)}>×</button>
                </div>
                <div className="inapp-body">
                  <p>{latestInApp.content}</p>
                  {inAppSubmitted ? (
                    <div className="inapp-thanks">
                      ✅ Response sent! Your feedback will train the CLM agent model.
                    </div>
                  ) : (
                    <div className="inapp-actions">
                      <button 
                        className="inapp-confirm" 
                        onClick={() => setInAppSubmitted(true)}
                      >
                        Acknowledge & Sync Workspace
                      </button>
                      <button 
                        className="inapp-dismiss" 
                        onClick={() => setShowInAppModal(false)}
                      >
                        Dismiss
                      </button>
                    </div>
                  )}
                </div>
                <div className="inapp-footer">
                  <small>Agent Learning loop registers: <i>{latestInApp.reaction}</i></small>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

      {/* MOBILE DEVICE MOCKUP VIEW */}
      {viewMode === 'mobile' && (
        <div className="mobile-view-wrapper">
          <div className="phone-bezel">
            <div className="phone-screen">
              {/* Top Notch Status */}
              <div className="phone-status-bar">
                <span className="phone-time">14:05</span>
                <div className="phone-notch">
                  <div className="dynamic-island"></div>
                </div>
                <div className="phone-icons">📶 🛜 🔋</div>
              </div>

              {/* Lockscreen Alerts Overview */}
              <div className="phone-body-content">
                <div className="phone-app-grid">
                  <div className="phone-app-icon-wrapper" onClick={() => setActiveTab('sms')}>
                    <span className="app-icon message-icon">💬</span>
                    <span className="app-name">Messages</span>
                    {sms.length > 0 && <span className="app-badge">{sms.length}</span>}
                  </div>
                  <div className="phone-app-icon-wrapper" onClick={() => setActiveTab('email')}>
                    <span className="app-icon mail-icon">✉️</span>
                    <span className="app-name">Mail</span>
                    {emails.length > 0 && <span className="app-badge">{emails.length}</span>}
                  </div>
                  <div className="phone-app-icon-wrapper" onClick={() => setActiveTab('billing')}>
                    <span className="app-icon client-icon">⚡</span>
                    <span className="app-name">Workspace</span>
                  </div>
                </div>

                {/* Lockscreen banners displaying pushed communications */}
                {userMessages.length > 0 && (
                  <div className="phone-notifications-drawer">
                    <span className="drawer-title">Recent Lockscreen Notifications</span>
                    {userMessages.slice(-3).map((m, index) => (
                      <div key={index} className="phone-notification-banner">
                        <div className="banner-top">
                          <span className="banner-app">{m.channel === 'SMS' ? '💬 Messages' : m.channel === 'Email' ? '✉️ Mail' : '🔔 System'}</span>
                          <span className="banner-day">Day {m.day}</span>
                        </div>
                        <div className="banner-body">
                          {m.channel === 'Email' ? m.content.split('\n')[0] : m.content}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Active Chat view inside mobile device frame */}
                <div className="phone-active-app-wrapper">
                  <div className="phone-app-header">
                    <h4>💬 SMS Workspace Chat</h4>
                  </div>
                  <div className="imessage-container">
                    {sms.map((s, idx) => (
                      <div key={idx} className="imessage-bubble-row">
                        <div className="imessage-bubble inbound">
                          {s.content}
                        </div>
                        <div className="imessage-meta">
                          Delivered Day {s.day} • Reaction: {s.reaction}
                        </div>
                      </div>
                    ))}
                    {sms.length === 0 && (
                      <p style={{ textAlign: 'center', color: '#64748b', fontSize: '0.8rem', padding: '1rem' }}>
                        No text messages received.
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Bottom Home Indicator */}
              <div className="phone-home-indicator"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
