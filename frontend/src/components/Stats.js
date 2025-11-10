import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function Stats({ stats }) {
  if (!stats) {
    return <Typography>Loading statistics...</Typography>;
  }

  const data = [
    { name: 'Safe Emails', value: stats.safe_emails, color: '#2e7d32' },
    { name: 'Phishing Detected', value: stats.phishing_detected, color: '#d32f2f' }
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Detection Statistics
        </Typography>
        <Box sx={{ height: 400, mt: 3 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Box>
        <Box sx={{ mt: 3 }}>
          <Typography variant="body1">
            Total Scans: <strong>{stats.total_scans}</strong>
          </Typography>
          <Typography variant="body1">
            Phishing Rate: <strong>{stats.phishing_rate.toFixed(2)}%</strong>
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default Stats;

