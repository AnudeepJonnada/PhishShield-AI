import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Button,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import ManageSearchIcon from '@mui/icons-material/ManageSearch';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function EmailScanner({ onScanComplete }) {
  const [maxEmails, setMaxEmails] = useState(10);
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleScan = async () => {
    setScanning(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/emails/scan`, {
        max_emails: maxEmails
      });
      setResults(response.data);
      if (onScanComplete) onScanComplete();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to scan emails');
    } finally {
      setScanning(false);
    }
  };

  const getThreatColor = (score) => {
    if (score >= 70) return 'error';
    if (score >= 50) return 'warning';
    return 'success';
  };

  const getThreatLabel = (score) => {
    if (score >= 70) return 'High Risk';
    if (score >= 50) return 'Moderate Risk';
    return 'Low Risk';
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Card elevation={4}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            🛡️ Scan Emails for Phishing
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <TextField
              label="Max Emails to Scan"
              type="number"
              value={maxEmails}
              onChange={(e) => setMaxEmails(parseInt(e.target.value) || 10)}
              inputProps={{ min: 1, max: 100 }}
              sx={{ width: 220 }}
            />

            <Button
              variant="contained"
              color="primary"
              startIcon={
                scanning ? <CircularProgress size={20} color="inherit" /> : <ManageSearchIcon />
              }
              onClick={handleScan}
              disabled={scanning}
              sx={{
                textTransform: 'none',
                px: 3,
                fontWeight: 600,
                backgroundColor: '#1976d2',
                '&:hover': { backgroundColor: '#115293' }
              }}
            >
              {scanning ? 'Scanning...' : 'Scan Emails'}
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {results && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                📬 Scan Results ({results.total_scanned} emails scanned)
              </Typography>
              <List>
                {results.results.map((result, index) => (
                  <React.Fragment key={index}>
                    <ListItem alignItems="flex-start">
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                              {result.subject || 'Unknown Subject'}
                            </Typography>
                            <Chip
                              label={getThreatLabel(result.threat_score)}
                              color={getThreatColor(result.threat_score)}
                              size="small"
                            />
                            <Chip
                              label={`Score: ${result.threat_score}`}
                              variant="outlined"
                              size="small"
                            />
                            {result.is_phishing && (
                              <Chip label="PHISHING" color="error" size="small" />
                            )}
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            <Typography variant="body2" color="text.secondary">
                              From: {result.from || 'Unknown Sender'}
                            </Typography>
                            {result.recommendations?.length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                {result.recommendations.map((rec, idx) => (
                                  <Typography key={idx} variant="body2" color="error">
                                    {rec}
                                  </Typography>
                                ))}
                              </Box>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Box>
          )}

          {!results && !error && !scanning && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Click "Scan Emails" to analyze your inbox for potential phishing threats.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default EmailScanner;
