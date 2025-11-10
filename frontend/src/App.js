import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  Tab,
  Tabs,
  Paper
} from '@mui/material';
import {
  Security as SecurityIcon,
  Email as EmailIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import EmailScanner from './components/EmailScanner';
import ScanHistory from './components/ScanHistory';
import Stats from './components/Stats';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to load statistics. Please try again later.');
    }
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <div className="App">
      {/* Header Section */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 3, mb: 4 }}>
        <Container>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <SecurityIcon sx={{ fontSize: 40 }} />
            <Typography variant="h4" component="h1">
              PhishShield AI
            </Typography>
          </Box>
          <Typography variant="subtitle1" sx={{ mt: 1 }}>
            Intelligent Phishing Email Detector
          </Typography>
        </Container>
      </Box>

      {/* Main Content */}
      <Container>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            variant="fullWidth"
            textColor="primary"
            indicatorColor="primary"
          >
            <Tab icon={<EmailIcon />} label="Scan Emails" />
            <Tab icon={<AssessmentIcon />} label="Dashboard" />
            <Tab icon={<HistoryIcon />} label="Scan History" />
            <Tab icon={<SecurityIcon />} label="Statistics" />
          </Tabs>
        </Paper>

        {/* Tab Routing */}
        {currentTab === 0 && <EmailScanner onScanComplete={fetchStats} />}
        {currentTab === 1 && <Dashboard stats={stats} />}
        {currentTab === 2 && <ScanHistory />}
        {currentTab === 3 && <Stats stats={stats} />}
      </Container>
    </div>
  );
}

export default App;
