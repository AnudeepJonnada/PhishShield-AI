import React from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import {
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Email as EmailIcon
} from '@mui/icons-material';

function Dashboard({ stats }) {
  if (!stats) {
    return <Typography>Loading dashboard...</Typography>;
  }

  const statCards = [
    {
      title: 'Total Scans',
      value: stats.total_scans,
      icon: <EmailIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2'
    },
    {
      title: 'Phishing Detected',
      value: stats.phishing_detected,
      icon: <WarningIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f'
    },
    {
      title: 'Safe Emails',
      value: stats.safe_emails,
      icon: <CheckCircleIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32'
    },
    {
      title: 'Phishing Rate',
      value: `${stats.phishing_rate.toFixed(2)}%`,
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02'
    }
  ];

  return (
    <Grid container spacing={3}>
      {statCards.map((card, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ color: card.color }}>{card.icon}</Box>
                <Box>
                  <Typography variant="h4" component="div">
                    {card.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.title}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default Dashboard;

